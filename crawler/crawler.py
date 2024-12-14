import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from retrying import retry
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 페이지 요청 함수 (재시도 포함)
@retry(stop_max_attempt_number=3, wait_fixed=2000)
def fetch_page(url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

# 채용 공고 데이터 파싱 함수
def parse_job(job):
    try:
        company = job.select_one('.corp_name a').text.strip()
        title = job.select_one('.job_tit a').text.strip()
        link = 'https://www.saramin.co.kr' + job.select_one('.job_tit a')['href']
        conditions = job.select('.job_condition span')
        location = conditions[0].text.strip() if len(conditions) > 0 else ''
        experience = conditions[1].text.strip() if len(conditions) > 1 else ''
        education = conditions[2].text.strip() if len(conditions) > 2 else ''
        employment_type = conditions[3].text.strip() if len(conditions) > 3 else ''
        salary_badge = job.select_one('.area_badge .badge')
        salary = salary_badge.text.strip() if salary_badge else ''
        deadline = job.select_one('.job_date .date').text.strip()
        sector = job.select_one('.job_sector').text.strip() if job.select_one('.job_sector') else ''
        
        return {
            '회사명': company,
            '제목': title,
            '링크': link,
            '지역': location,
            '경력': experience,
            '학력': education,
            '고용형태': employment_type,
            '마감일': deadline,
            '직무분야': sector,
            '연봉정보': salary
        }
    except AttributeError as e:
        logging.error(f"항목 파싱 중 에러 발생: {e}")
        return None

# 사람인 크롤링 함수
def crawl_saramin(keyword, pages=1):
    jobs = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for page in range(1, pages + 1):
        url = f"https://www.saramin.co.kr/zf_user/search/recruit?searchType=search&searchword={keyword}&recruitPage={page}"

        try:
            data = fetch_page(url, headers)
            soup = BeautifulSoup(data, 'html.parser')

            # 채용공고 목록 가져오기
            job_listings = soup.select('.item_recruit')

            for job in job_listings:
                parsed_job = parse_job(job)
                if parsed_job:
                    jobs.append(parsed_job)

            logging.info(f"{page}페이지 크롤링 완료")
            time.sleep(1)  # 서버 부하 방지를 위한 딜레이

        except requests.RequestException as e:
            logging.error(f"페이지 요청 중 에러 발생: {e}")
            continue

    return pd.DataFrame(jobs)

# 사용 예시
if __name__ == "__main__":
    # 'python' 키워드로 3페이지 크롤링
    df = crawl_saramin('python', pages=3)
    print(df)
    df.to_csv('saramin_python.csv', index=False)
