"""
네이버 지도 방문자 리뷰 크롤러 (Playwright 브라우저 방식)
API 방식(scrape_reviews.py)이 차단될 때 사용
설치: pip install playwright && python -m playwright install chromium
"""

import csv
import re
import time
import sys
from datetime import datetime

TARGET_URL = (
    "https://map.naver.com/p/search/"
    "%EC%9D%B4%EB%94%94%EC%95%BC%20%EB%A7%A4%EC%9E%A5"
    "/place/493555339"
    "?c=15.00,0,0,2,dh&placePath=/review"
)
OUTPUT_FILE = "review.csv"
SCROLL_PAUSE = 1.5

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


def extract_star_count(star_text: str) -> str:
    m = re.search(r"[\d.]+", star_text or "")
    return m.group() if m else ""


def scrape_with_playwright() -> list[dict]:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

    reviews = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
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

        print("[브라우저] 페이지 로딩 중...")
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)

        # 리뷰 iframe 또는 내부 패널 대기
        try:
            page.wait_for_selector(
                "iframe#entryIframe, div[data-nclick*='review']",
                timeout=15000,
            )
        except PWTimeout:
            print("[경고] 리뷰 패널 감지 실패. 계속 시도합니다.")

        # 네이버 지도는 entryIframe 안에 콘텐츠를 렌더링
        frame = None
        for f in page.frames:
            if "entry" in f.url or "place" in f.url:
                frame = f
                break
        if frame is None:
            frame = page.main_frame

        print("[브라우저] 리뷰 목록 스크롤 수집 시작")
        seen_ids: set[str] = set()
        prev_count = -1
        no_change_rounds = 0

        while True:
            # 리뷰 카드 선택 (여러 가능 셀렉터 시도)
            items = frame.query_selector_all(
                "li.pui__X35jYm, li[class*='ReviewItem'], "
                "div[class*='ReviewItem'], li.place_apply_pui"
            )

            for item in items:
                try:
                    # 고유 ID (data 속성 또는 텍스트 해시)
                    uid = item.get_attribute("data-id") or item.inner_text()[:60]
                    if uid in seen_ids:
                        continue
                    seen_ids.add(uid)

                    # 작성자
                    author_el = item.query_selector(
                        "span[class*='name'], span.pui__uslU0d, "
                        "span[class*='reviewer']"
                    )
                    author = author_el.inner_text().strip() if author_el else "익명"

                    # 별점
                    star_el = item.query_selector(
                        "span[class*='rating'], em[class*='rating'], "
                        "span.pui__jhkzMC"
                    )
                    star = extract_star_count(
                        star_el.inner_text() if star_el else ""
                    )

                    # 작성일
                    date_el = item.query_selector(
                        "span[class*='date'], span.pui__gfuPNA, "
                        "time, span[class*='time']"
                    )
                    date_raw = date_el.inner_text().strip() if date_el else ""

                    # 리뷰 내용
                    body_el = item.query_selector(
                        "span[class*='body'], div[class*='body'], "
                        "span.pui__xndfMs, p[class*='text']"
                    )
                    body = body_el.inner_text().replace("\n", " ").strip() if body_el else ""

                    # 좋아요
                    like_el = item.query_selector(
                        "span[class*='like'], button[class*='like'] span, "
                        "em[class*='like']"
                    )
                    like_text = like_el.inner_text() if like_el else "0"
                    like_count = int(re.sub(r"[^\d]", "", like_text) or "0")

                    # 사진
                    photos = item.query_selector_all("img[class*='photo'], ul[class*='photo'] img")

                    reviews.append({
                        "번호": len(reviews) + 1,
                        "작성자": author,
                        "별점": star,
                        "방문횟수": "",
                        "작성일": date_raw,
                        "리뷰내용": body,
                        "좋아요수": like_count,
                        "사진수": len(photos),
                    })
                except Exception:
                    continue

            current_count = len(reviews)
            print(f"  현재까지 수집: {current_count}건", end="\r", flush=True)

            if current_count == prev_count:
                no_change_rounds += 1
                if no_change_rounds >= 3:
                    print("\n  더 이상 새 리뷰 없음.")
                    break
            else:
                no_change_rounds = 0
            prev_count = current_count

            # 스크롤 다운
            frame.evaluate("window.scrollBy(0, 1200)")
            time.sleep(SCROLL_PAUSE)

            # 더보기 버튼 클릭 시도
            more_btn = frame.query_selector(
                "a[class*='more'], button[class*='more'], "
                "span[class*='more']"
            )
            if more_btn:
                try:
                    more_btn.click()
                    time.sleep(SCROLL_PAUSE)
                except Exception:
                    pass

        browser.close()

    return reviews


def save_csv(reviews: list[dict]) -> None:
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(reviews)
    print(f"[저장 완료] {OUTPUT_FILE} ({len(reviews)}건)")


def main():
    try:
        reviews = scrape_with_playwright()
        if not reviews:
            print("[경고] 수집된 리뷰가 없습니다.")
            sys.exit(1)
        save_csv(reviews)
    except ImportError:
        print(
            "[오류] Playwright 미설치\n"
            "  pip install playwright\n"
            "  python -m playwright install chromium"
        )
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[중단] 사용자 중단")
        sys.exit(0)
    except Exception as e:
        print(f"\n[에러] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
