"""
네이버 지도 방문자 리뷰 크롤러 v3
수정 사항:
  - 원본 API 응답 → debug_api_response.json 저장 + 첫 아이템 구조 출력
  - 작성자·별점·리뷰내용 등 모든 필드를 재귀 탐색 (필드명 변경 대응)
  - 페이지네이션: MIN_REVIEWS(50)건 이상 수집될 때까지 반복
  - perPage 자동 감지 후 증가 시도

실행:
  pip install playwright requests
  python -m playwright install chromium
  python scrape_reviews_v3.py
"""

import csv
import json
import re
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import requests
from playwright.sync_api import Request, Response, sync_playwright

# ── 설정 ──────────────────────────────────────────────────────────────────────
PLACE_ID    = "493555339"
OUTPUT_FILE = "review.csv"
DEBUG_FILE  = "debug_api_response.json"   # 원본 JSON 저장 (구조 확인용)
MIN_REVIEWS = 50    # 최소 수집 목표
MAX_PAGES   = 30    # 최대 페이지 수

PCMAP_URLS = [
    f"https://pcmap.place.naver.com/restaurant/{PLACE_ID}/review/visitor",
    f"https://pcmap.place.naver.com/place/{PLACE_ID}/review/visitor",
]

CSV_FIELDS = ["번호", "작성자", "별점", "방문횟수", "작성일", "리뷰내용", "좋아요수", "사진수"]

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# 리뷰 아이템임을 판별하는 키 집합
_REVIEW_SIGNAL_KEYS = frozenset({
    "body", "text", "created", "author", "rating", "reviewer",
    "visitCount", "medias", "photos", "reviewBody", "visitReviewBody",
})


# ── 캡처 상태 ─────────────────────────────────────────────────────────────────
@dataclass
class ApiCapture:
    url:          str  = ""
    req_headers:  dict = field(default_factory=dict)
    payload:      Any  = None
    raw_response: Any  = None
    reviews:      list = field(default_factory=list)
    total:        int  = 0
    per_page:     int  = 10
    ok:           bool = False


# ── 재귀 탐색: 리뷰 배열 찾기 ────────────────────────────────────────────────
def _find_items(obj: Any, depth: int = 0) -> Optional[tuple[list, int]]:
    """JSON 트리를 재귀 탐색하여 리뷰 아이템 배열과 전체 수 반환"""
    if depth > 8:
        return None
    if isinstance(obj, dict):
        for arr_key in ("items", "list", "reviews", "reviewList",
                        "visitorReviews", "reviewItems", "contents"):
            lst = obj.get(arr_key)
            if lst and isinstance(lst, list) and len(lst) > 0:
                first = lst[0]
                if isinstance(first, dict):
                    overlap = _REVIEW_SIGNAL_KEYS & set(first.keys())
                    if len(overlap) >= 2 or ("created" in overlap and len(overlap) >= 1):
                        total = int(
                            obj.get("total") or obj.get("totalCount")
                            or obj.get("count") or 0
                        )
                        return lst, total
        for v in obj.values():
            if isinstance(v, (dict, list)):
                result = _find_items(v, depth + 1)
                if result:
                    return result
    elif isinstance(obj, list):
        for item in obj:
            result = _find_items(item, depth + 1)
            if result:
                return result
    return None


# ── 필드 추출 헬퍼 ────────────────────────────────────────────────────────────
def _str(obj: dict, *keys) -> str:
    """여러 키를 순서대로 시도, 첫 번째 유효한 문자열 반환"""
    for k in keys:
        v = obj.get(k)
        if v is not None and isinstance(v, (str, int, float)):
            s = str(v).strip()
            if s and s.lower() not in ("null", "none", ""):
                return s
    return ""


def _get_author(item: dict) -> str:
    """작성자 닉네임 — 여러 경로 시도"""
    for fld in ("author", "reviewer", "user", "writer", "profile", "visitor"):
        obj = item.get(fld)
        if obj and isinstance(obj, dict):
            v = _str(obj, "nickname", "name", "displayName", "id", "userId")
            if v:
                return v
    return _str(item, "nickname", "authorNickname", "userName",
                "writerNickname", "userId") or "익명"


def _get_body(item: dict) -> str:
    """리뷰 본문 — 여러 경로 시도"""
    # 최상위 필드
    v = _str(item,
        "body", "text", "reviewBody", "visitReviewBody", "reviewContent",
        "contents", "content", "description", "comment", "reviewText",
    )
    if v:
        return v.replace("\n", " ")
    # 중첩 객체
    for fld in ("review", "visitReview", "reviewInfo", "reviewDetail"):
        obj = item.get(fld)
        if obj and isinstance(obj, dict):
            v = _str(obj, "body", "text", "content", "reviewBody", "contents")
            if v:
                return v.replace("\n", " ")
    return ""


def _get_rating(item: dict) -> str:
    return _str(item, "rating", "score", "starScore", "grade",
                "starRating", "point", "reviewScore")


def _get_visit(item: dict) -> str:
    return _str(item,
        "visitCount", "visitCountText", "visitedCount", "visitInfo",
        "visitType", "visitTime", "mealType", "visitTimeType", "timeSlot",
    )


def _get_date(item: dict) -> str:
    for k in ("created", "createdAt", "visitDate", "date",
              "registDate", "updatedAt", "reviewDate"):
        v = item.get(k)
        if v and isinstance(v, str) and v.strip():
            raw = v.strip()
            # ISO 형식이면 앞 10자리만, 아니면 그대로 유지
            return raw[:10] if ("T" in raw or len(raw) > 12) else raw
    return ""


def _get_likes(item: dict) -> str:
    reaction = item.get("userReaction") or {}
    v = _str(reaction, "helpCount", "likeCount", "like", "thumbsUp")
    if v and v != "0":
        return v
    return _str(item, "likeCount", "helpCount", "likeNum") or "0"


def _get_photos(item: dict) -> int:
    for k in ("medias", "photos", "images", "imageList", "photoList"):
        lst = item.get(k)
        if isinstance(lst, list):
            return len(lst)
    return 0


# ── 응답 파싱 ─────────────────────────────────────────────────────────────────
def parse_response(body: Any) -> tuple[list, int]:
    result = _find_items(body)
    if not result:
        return [], 0
    raw_items, total = result
    reviews = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        reviews.append({
            "작성자":  _get_author(item),
            "별점":    _get_rating(item),
            "방문횟수": _get_visit(item),
            "작성일":  _get_date(item),
            "리뷰내용": _get_body(item),
            "좋아요수": _get_likes(item),
            "사진수":  _get_photos(item),
        })
    return reviews, total


# ── 페이로드 수정 (page, perPage) ─────────────────────────────────────────────
def _mutate_payload(obj: Any, page: int, per_page: int) -> None:
    if isinstance(obj, list):
        for item in obj:
            _mutate_payload(item, page, per_page)
    elif isinstance(obj, dict):
        if "page" in obj and isinstance(obj["page"], int):
            obj["page"] = page
        if "perPage" in obj and isinstance(obj["perPage"], int):
            obj["perPage"] = per_page
        for v in obj.values():
            if isinstance(v, (dict, list)):
                _mutate_payload(v, page, per_page)


# ── Playwright: 브라우저 + API 캡처 ──────────────────────────────────────────
def _is_review_api(url: str) -> bool:
    return "naver.com" in url and (
        "graphql" in url
        or ("review" in url and "pcmap" in url)
    )


def browser_capture(pcmap_url: str) -> ApiCapture:
    cap = ApiCapture()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        ctx = browser.new_context(
            user_agent=UA, locale="ko-KR", timezone_id="Asia/Seoul"
        )
        page = ctx.new_page()

        def on_request(req: Request):
            if not cap.req_headers and _is_review_api(req.url):
                cap.url = req.url
                cap.req_headers = dict(req.headers)
                try:
                    if req.post_data:
                        cap.payload = json.loads(req.post_data)
                except Exception:
                    pass

        def on_response(resp: Response):
            if cap.ok or resp.status != 200:
                return
            if not _is_review_api(resp.url):
                return
            try:
                body = resp.json()
                reviews, total = parse_response(body)
                if reviews:
                    cap.raw_response = body
                    cap.reviews = reviews
                    cap.total = total
                    cap.ok = True
                    # perPage 자동 감지
                    m = re.search(r'"perPage"\s*:\s*(\d+)', json.dumps(body))
                    cap.per_page = int(m.group(1)) if m else 10
                    print(
                        f"  API 캡처 완료 | 전체: {total}건 | "
                        f"첫 페이지: {len(reviews)}건 | perPage: {cap.per_page}"
                    )
            except Exception:
                pass

        page.on("request", on_request)
        page.on("response", on_response)

        print(f"  브라우저 접속: {pcmap_url}")
        try:
            page.goto(pcmap_url, wait_until="networkidle", timeout=30000)
        except Exception:
            page.goto(pcmap_url, wait_until="domcontentloaded", timeout=25000)
            time.sleep(5)

        if not cap.ok:
            page.evaluate("window.scrollBy(0, 800)")
            time.sleep(3)

        # ── 디버그 출력 ──────────────────────────────────────────────────────
        if cap.raw_response is not None:
            with open(DEBUG_FILE, "w", encoding="utf-8") as f:
                json.dump(cap.raw_response, f, ensure_ascii=False, indent=2)
            print(f"  원본 응답 저장 → {DEBUG_FILE}")

            result = _find_items(cap.raw_response)
            if result and result[0]:
                first = result[0][0]
                print(f"\n  ┌─ 첫 번째 리뷰 아이템 키: {list(first.keys())}")
                print("  │  주요 필드 값:")
                for k, v in first.items():
                    display = v if not isinstance(v, (list, dict)) else f"[{type(v).__name__}]"
                    print(f"  │    {k}: {display}")
                print("  └─" + "─" * 40)
        # ─────────────────────────────────────────────────────────────────────

        browser.close()

    return cap


# ── requests: 나머지 페이지 수집 ─────────────────────────────────────────────
def fetch_all(cap: ApiCapture) -> list:
    all_reviews = list(cap.reviews)

    if not cap.payload or not cap.req_headers:
        print("  [경고] 페이로드/헤더 미캡처 → 첫 페이지만 반환")
        return all_reviews

    total    = cap.total if cap.total > 0 else 9999
    per_page = max(cap.per_page, 10)   # 최소 10건 이상 요청
    headers  = {
        k: v for k, v in cap.req_headers.items()
        if k.lower() != "content-length"
    }

    page_num        = 2
    consecutive_empty = 0

    while (
        (len(all_reviews) < max(total, MIN_REVIEWS))
        and page_num <= MAX_PAGES
        and consecutive_empty < 2
    ):
        payload = json.loads(json.dumps(cap.payload))
        _mutate_payload(payload, page_num, per_page)

        print(f"  페이지 {page_num} 수집 중...", end=" ", flush=True)
        try:
            resp = requests.post(
                cap.url, json=payload, headers=headers, timeout=15
            )
            resp.raise_for_status()
            reviews, _ = parse_response(resp.json())
            if not reviews:
                consecutive_empty += 1
                print("(없음)")
                if consecutive_empty >= 2:
                    print("  수집 완료")
                    break
            else:
                consecutive_empty = 0
                all_reviews.extend(reviews)
                print(f"({len(reviews)}건  누적: {len(all_reviews)}/{total})")
        except Exception as e:
            print(f"(오류: {e})")
            break

        page_num += 1
        time.sleep(0.5)

    return all_reviews


# ── CSV 저장 ──────────────────────────────────────────────────────────────────
def save_csv(reviews: list) -> None:
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for i, r in enumerate(reviews, 1):
            row = {k: r.get(k, "") for k in CSV_FIELDS}
            row["번호"] = i
            writer.writerow(row)
    print(f"\n[저장 완료] {OUTPUT_FILE}  ({len(reviews)}건)")


# ── 진입점 ────────────────────────────────────────────────────────────────────
def main():
    print(f"[시작] 이디야 사당역점 리뷰 크롤링  (place_id={PLACE_ID})")
    print(f"       목표: {MIN_REVIEWS}건 이상\n")

    cap = ApiCapture()
    for url in PCMAP_URLS:
        cap = browser_capture(url)
        if cap.ok or cap.reviews:
            break

    if not cap.reviews:
        print(f"\n[실패] 리뷰를 수집하지 못했습니다.")
        print(
            f"  → {DEBUG_FILE} 파일을 확인하거나\n"
            "    코드 내 headless=True → headless=False 로 바꾸어 브라우저를 직접 확인하세요."
        )
        sys.exit(1)

    all_reviews = fetch_all(cap)
    print(f"\n최종 수집: {len(all_reviews)}건")
    save_csv(all_reviews)


if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print(
            "[오류] 패키지 미설치:\n"
            "  pip install playwright requests\n"
            "  python -m playwright install chromium"
        )
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[중단]")
        sys.exit(0)
