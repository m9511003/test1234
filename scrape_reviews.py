"""
네이버 지도 방문자 리뷰 크롤러
대상: https://map.naver.com/p/place/493555339 (이디야 매장)
결과: review.csv 저장
"""

import csv
import json
import time
import sys
from datetime import datetime

import requests

PLACE_ID = "493555339"
OUTPUT_FILE = "review.csv"
PER_PAGE = 10
MAX_PAGES = 100  # 최대 페이지 수 (과도한 요청 방지)

BASE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": f"https://map.naver.com/p/place/{PLACE_ID}/review",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}

REVIEW_API_URL = (
    "https://place.map.naver.com/place/v1/place/"
    f"{PLACE_ID}/review/visitor"
    "?page={page}&perPage={per_page}&lang=ko"
)

CSV_FIELDS = [
    "번호",
    "작성자",
    "별점",
    "방문횟수",
    "작성일",
    "리뷰내용",
    "좋아요수",
    "사진수",
]


def fetch_page(session: requests.Session, page: int) -> dict:
    url = REVIEW_API_URL.format(page=page, per_page=PER_PAGE)
    for attempt in range(3):
        try:
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            print(f"  [타임아웃] 페이지 {page}, 재시도 {attempt + 1}/3")
            time.sleep(2 ** attempt)
        except requests.exceptions.HTTPError as e:
            print(f"  [HTTP 오류] {e}")
            raise
        except Exception as e:
            print(f"  [오류] {e}")
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError(f"페이지 {page} 수집 실패")


def parse_review(idx: int, item: dict) -> dict:
    author = item.get("author") or {}
    nickname = author.get("nickname") or author.get("id") or "익명"

    body = item.get("body") or item.get("text") or ""
    rating = item.get("rating") or item.get("score") or ""
    visit_count = item.get("visitCount") or ""

    # 작성일: ISO 형식 → YYYY-MM-DD
    created_raw = item.get("created") or item.get("createdAt") or ""
    try:
        created = datetime.fromisoformat(
            created_raw.replace("Z", "+00:00")
        ).strftime("%Y-%m-%d")
    except Exception:
        created = created_raw[:10] if created_raw else ""

    like_count = item.get("likeCount") or 0
    photo_count = len(item.get("photos") or [])

    return {
        "번호": idx,
        "작성자": nickname,
        "별점": rating,
        "방문횟수": visit_count,
        "작성일": created,
        "리뷰내용": body.replace("\n", " ").strip(),
        "좋아요수": like_count,
        "사진수": photo_count,
    }


def crawl() -> list[dict]:
    session = requests.Session()
    session.headers.update(BASE_HEADERS)

    reviews = []
    total_count = None

    print(f"[시작] place_id={PLACE_ID} 리뷰 수집")

    for page in range(1, MAX_PAGES + 1):
        print(f"  페이지 {page} 요청 중...", end=" ", flush=True)
        data = fetch_page(session, page)

        # 응답 구조 탐색 (result 또는 최상위)
        result = data.get("result") or data
        items = (
            result.get("items")
            or result.get("reviews")
            or result.get("list")
            or []
        )

        if total_count is None:
            total_count = (
                result.get("totalCount")
                or result.get("total")
                or "?"
            )
            print(f"(전체 리뷰 수: {total_count})")
        else:
            print(f"({len(items)}건)")

        if not items:
            print("  더 이상 리뷰 없음. 수집 완료.")
            break

        start_idx = len(reviews) + 1
        for i, item in enumerate(items, start=start_idx):
            reviews.append(parse_review(i, item))

        # 마지막 페이지 확인
        has_next = result.get("hasNextPage") or result.get("nextPage")
        if not has_next and len(items) < PER_PAGE:
            break

        time.sleep(0.5)  # 서버 부하 방지

    return reviews


def save_csv(reviews: list[dict]) -> None:
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(reviews)
    print(f"\n[저장 완료] {OUTPUT_FILE} ({len(reviews)}건)")


def main():
    try:
        reviews = crawl()
        if not reviews:
            print("[경고] 수집된 리뷰가 없습니다.")
            sys.exit(1)
        save_csv(reviews)
    except KeyboardInterrupt:
        print("\n[중단] 사용자 중단")
        sys.exit(0)
    except Exception as e:
        print(f"\n[에러] {e}")
        print(
            "\n--- 추가 안내 ---\n"
            "API 차단 시 브라우저(Playwright/Selenium) 방식을 사용하세요.\n"
            "  pip install playwright && python -m playwright install chromium\n"
            "  그 후 scrape_reviews_browser.py 실행\n"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
