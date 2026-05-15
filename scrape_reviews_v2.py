"""
네이버 지도 방문자 리뷰 크롤러 v2
- Playwright로 실제 브라우저를 띄워 GraphQL API 요청을 캡처
- 캡처한 헤더/페이로드를 재사용해 requests로 전체 페이지 수집
- API 캡처 실패 시 DOM 스크래핑으로 폴백
실행: pip install playwright requests && python -m playwright install chromium
"""

import csv
import json
import re
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

import requests
from playwright.sync_api import Request, Response, sync_playwright

PLACE_ID = "493555339"
OUTPUT_FILE = "review.csv"
PER_PAGE = 10

# pcmap URL에 직접 접근 (map.naver.com의 iframe 내용)
PCMAP_URLS = [
    f"https://pcmap.place.naver.com/restaurant/{PLACE_ID}/review/visitor",
    f"https://pcmap.place.naver.com/place/{PLACE_ID}/review/visitor",
]

CSV_FIELDS = ["번호", "작성자", "별점", "방문횟수", "작성일", "리뷰내용", "좋아요수", "사진수"]


# ── 데이터 클래스 ─────────────────────────────────────────────────────────────

@dataclass
class ApiCapture:
    url: str = ""
    req_headers: dict = field(default_factory=dict)
    payload: Optional[list] = None   # GraphQL 배치 배열
    reviews: list = field(default_factory=list)
    total: int = 0
    ok: bool = False


# ── GraphQL 응답 파싱 ──────────────────────────────────────────────────────────

def _parse_response_body(body) -> tuple[list, int]:
    """GraphQL 응답(단일 dict or 배열)에서 리뷰 목록과 전체 수 반환"""
    if isinstance(body, list):
        body = body[0] if body else {}

    # data.visitorReviews 또는 data.getVisitorReviews
    data_node = body.get("data") or body
    for key in ("visitorReviews", "getVisitorReviews", "reviews", "visitorReviewList"):
        node = data_node.get(key)
        if node and isinstance(node, dict):
            items = node.get("items") or node.get("list") or []
            total = node.get("total") or node.get("totalCount") or 0
            return [_parse_item(i) for i in items], int(total)

    return [], 0


def _parse_item(item: dict) -> dict:
    author = item.get("author") or {}
    nickname = (
        author.get("nickname") or author.get("name") or author.get("id") or "익명"
    )
    body_text = (item.get("body") or item.get("text") or "").replace("\n", " ").strip()
    rating = item.get("rating") or ""
    visit_count = item.get("visitCount") or ""

    raw_date = item.get("created") or item.get("createdAt") or ""
    created = raw_date[:10] if raw_date else ""

    reaction = item.get("userReaction") or {}
    like_count = reaction.get("helpCount") or item.get("likeCount") or 0

    medias = item.get("medias") or item.get("photos") or []
    photo_count = len(medias)

    return {
        "작성자": nickname,
        "별점": rating,
        "방문횟수": visit_count,
        "작성일": created,
        "리뷰내용": body_text,
        "좋아요수": like_count,
        "사진수": photo_count,
    }


# ── payload에서 page 번호 업데이트 ───────────────────────────────────────────

def _set_page(obj, page: int):
    """GraphQL variables 안의 page 필드를 재귀적으로 업데이트"""
    if isinstance(obj, list):
        for item in obj:
            _set_page(item, page)
    elif isinstance(obj, dict):
        if "page" in obj and isinstance(obj["page"], int):
            obj["page"] = page
        for v in obj.values():
            if isinstance(v, (dict, list)):
                _set_page(v, page)


# ── Playwright: 브라우저 실행 + API 캡처 ─────────────────────────────────────

def _is_review_api(url: str) -> bool:
    return (
        "graphql" in url
        or ("review" in url and "pcmap" in url)
    ) and "naver.com" in url


def browser_capture(pcmap_url: str) -> ApiCapture:
    cap = ApiCapture()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="ko-KR",
            timezone_id="Asia/Seoul",
        )
        page = ctx.new_page()

        # 요청 캡처 (헤더 + 페이로드)
        def on_request(req: Request):
            if not cap.req_headers and _is_review_api(req.url):
                cap.url = req.url
                cap.req_headers = dict(req.headers)
                try:
                    raw = req.post_data
                    if raw:
                        cap.payload = json.loads(raw)
                except Exception:
                    pass

        # 응답 캡처 (리뷰 데이터)
        def on_response(resp: Response):
            if cap.ok:
                return
            if resp.status == 200 and _is_review_api(resp.url):
                try:
                    body = resp.json()
                    reviews, total = _parse_response_body(body)
                    if reviews:
                        cap.reviews = reviews
                        cap.total = total
                        cap.ok = True
                        print(f"  API 캡처 완료 ({resp.url[:70]}...)")
                        print(f"  전체 리뷰 수: {total}")
                except Exception:
                    pass

        page.on("request", on_request)
        page.on("response", on_response)

        print(f"  브라우저 로딩: {pcmap_url}")
        try:
            page.goto(pcmap_url, wait_until="networkidle", timeout=30000)
        except Exception:
            try:
                page.goto(pcmap_url, wait_until="domcontentloaded", timeout=20000)
                time.sleep(4)
            except Exception as e:
                print(f"  페이지 로딩 실패: {e}")
                browser.close()
                return cap

        time.sleep(2)

        # 스크롤해서 추가 API 트리거
        if not cap.ok:
            page.evaluate("window.scrollBy(0, 600)")
            time.sleep(3)

        # 그래도 실패하면 DOM 스크래핑
        if not cap.ok:
            print("  API 캡처 실패 → DOM 스크래핑 시작")
            cap.reviews = _dom_scrape(page)

        browser.close()

    return cap


# ── requests: 나머지 페이지 수집 ─────────────────────────────────────────────

def fetch_all_pages(cap: ApiCapture) -> list:
    all_reviews = list(cap.reviews)

    if not cap.payload or not cap.req_headers or cap.total <= len(all_reviews):
        return all_reviews

    # content-length 제거 (requests가 자동 계산)
    headers = {
        k: v for k, v in cap.req_headers.items()
        if k.lower() not in ("content-length",)
    }

    page_num = 2
    while len(all_reviews) < cap.total:
        payload = json.loads(json.dumps(cap.payload))  # 깊은 복사
        _set_page(payload, page_num)

        print(f"  페이지 {page_num} 수집 중...", end=" ", flush=True)
        try:
            resp = requests.post(
                cap.url, json=payload, headers=headers, timeout=15
            )
            resp.raise_for_status()
            reviews, _ = _parse_response_body(resp.json())
            if not reviews:
                print("(없음) 수집 완료")
                break
            all_reviews.extend(reviews)
            print(f"({len(reviews)}건, 누적: {len(all_reviews)}/{cap.total})")
        except Exception as e:
            print(f"(오류: {e}) 중단")
            break

        page_num += 1
        time.sleep(0.5)

    return all_reviews


# ── DOM 스크래핑 (폴백) ───────────────────────────────────────────────────────

def _text(el, selector: str) -> str:
    found = el.query_selector(selector)
    return found.inner_text().strip() if found else ""


def _dom_scrape(page) -> list:
    reviews = []
    seen: set[str] = set()
    no_change = 0

    while no_change < 4:
        # 다양한 셀렉터 시도 (네이버는 obfuscated 클래스명 사용)
        items = page.query_selector_all(
            "li.place_apply_pui, "
            "li[data-id], "
            "[class*='ReviewItem'], "
            "[class*='review_item'], "
            "li[class*='pui']"
        )

        prev = len(reviews)
        for item in items:
            try:
                uid = item.inner_text()[:80]
                if uid in seen:
                    continue
                seen.add(uid)

                reviews.append({
                    "작성자": _text(item, "[class*='name'], [class*='nickname']"),
                    "별점": _text(item, "[class*='rating'], [class*='star'], em"),
                    "방문횟수": "",
                    "작성일": _text(item, "[class*='date'], time, [class*='time']"),
                    "리뷰내용": _text(item, "[class*='body'], [class*='text'], p, span:last-child"),
                    "좋아요수": _text(item, "[class*='like'], [class*='help']"),
                    "사진수": str(len(item.query_selector_all("img"))),
                })
            except Exception:
                continue

        if len(reviews) == prev:
            no_change += 1
        else:
            no_change = 0

        print(f"  DOM 수집: {len(reviews)}건", end="\r", flush=True)
        page.evaluate("window.scrollBy(0, 1000)")
        time.sleep(1.5)

    print()
    return reviews


# ── CSV 저장 ──────────────────────────────────────────────────────────────────

def save_csv(reviews: list) -> None:
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for i, r in enumerate(reviews, 1):
            writer.writerow({k: r.get(k, "") for k in CSV_FIELDS if k != "번호"} | {"번호": i})
    print(f"\n[저장 완료] {OUTPUT_FILE}  ({len(reviews)}건)")


# ── 진입점 ────────────────────────────────────────────────────────────────────

def main():
    print(f"[시작] 이디야 사당역점 리뷰 크롤링  (place_id={PLACE_ID})\n")

    cap = ApiCapture()
    for url in PCMAP_URLS:
        cap = browser_capture(url)
        if cap.ok or cap.reviews:
            break

    if not cap.reviews:
        print("[경고] 리뷰를 하나도 수집하지 못했습니다.")
        print("  → headless=False 로 바꾸어 브라우저 화면을 직접 확인해 보세요.")
        sys.exit(1)

    all_reviews = fetch_all_pages(cap)
    save_csv(all_reviews)


if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print(
            "[오류] playwright 미설치\n"
            "  pip install playwright\n"
            "  python -m playwright install chromium"
        )
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[중단]")
        sys.exit(0)
