import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from retrying import retry
import sqlalchemy
import schedule
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
        salary_badge = job.select_one('.area_badge .badge')
        salary = salary_badge.text.strip() if salary_badge else ''
        deadline = job.select_one('.job_date .date').text.strip()
        sector = job.select_one('.job_sector').text.strip() if job.select_one('.job_sector') else ''
        categories = sector.split(', ') if sector else []
        
        return {
            '회사명': company,
            '제목': title,
            '링크': link,
            '지역': location,
            '연봉정보': salary,
            '마감일': deadline,
            '직무분야': sector,
            '카테고리': categories
        }
    except AttributeError as e:
        logging.error(f"항목 파싱 중 에러 발생: {e}")
        return None

# 사람인 크롤링 함수
def crawl_saramin(keyword, pages=10):  # 페이지 수를 늘려 더 많은 데이터를 크롤링
    jobs = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    for page in range(1, pages + 1):
        url = f"https://www.saramin.co.kr/zf_user/search/recruit?searchType=search&searchword={keyword}&recruitPage={page}"
        try:
            data = fetch_page(url, headers)
            soup = BeautifulSoup(data, 'html.parser')
            job_listings = soup.select('.item_recruit')
            for job in job_listings:
                parsed_job = parse_job(job)
                if parsed_job:
                    jobs.append(parsed_job)
            logging.info(f"{page}페이지 크롤링 완료")
        except Exception as e:
            logging.error(f"페이지 요청 중 에러 발생: {e}")
    
    # 중복 제거 후 데이터프레임 생성
    df_jobs = pd.DataFrame(jobs).drop_duplicates(subset=['링크'])
    
    # 최소 100개 데이터 확보를 위한 추가 요청 처리
    while len(df_jobs) < 100:
        pages += 1
        url = f"https://www.saramin.co.kr/zf_user/search/recruit?searchType=search&searchword={keyword}&recruitPage={pages}"
        try:
            data = fetch_page(url, headers)
            soup = BeautifulSoup(data, 'html.parser')
            job_listings = soup.select('.item_recruit')
            for job in job_listings:
                parsed_job = parse_job(job)
                if parsed_job:
                    jobs.append(parsed_job)
            logging.info(f"{pages}페이지 추가 크롤링 완료")
        except Exception as e:
            logging.error(f"추가 페이지 요청 중 에러 발생: {e}")
        
        df_jobs = pd.DataFrame(jobs).drop_duplicates(subset=['링크'])

    return df_jobs

# 회사 ID를 가져오는 함수
def get_company_id(engine, company_name):
    query = f"SELECT id FROM company WHERE name = '{company_name}'"
    result = pd.read_sql(query, con=engine)
    if not result.empty:
        return result.iloc[0]['id']
    else:
        logging.error(f"회사 '{company_name}'가 company 테이블에 존재하지 않습니다.")
        return None

# 데이터 분리 및 정규화 함수
def separate_data(parsed_jobs, engine):
    companies_data = []
    jobs_data = []
    deadlines_data = []
    salaries_data = []
    locations_data = []

    for idx, job in enumerate(parsed_jobs):
        # 회사 정보
        companies_data.append({
            'name': job['회사명'],
            'industry': job['직무분야'],
            'category': ', '.join(job.get('카테고리', []))
        })
        
        # 채용 공고 정보
        jobs_data.append({
            'title': job['제목'],
            'link': job['링크'],
            'company_id': get_company_id(engine, job['회사명'])  # engine 전달
        })

        # 마감일 정보
        deadlines_data.append({
            'job_notice_id': idx + 1,
            'deadline_date': pd.to_datetime(job['마감일'], errors='coerce')
        })
        
        # 연봉 정보
        salaries_data.append({
            'job_notice_id': idx + 1,
            'salary': job['연봉정보']
        })
        
        # 지역 정보
        locations_data.append({
            'job_notice_id': idx + 1,
            'region': job['지역']
        })

    return {
        'companies': pd.DataFrame(companies_data).drop_duplicates(subset=['name']),
        'jobs': pd.DataFrame(jobs_data).drop_duplicates(subset=['link']),
        'deadlines': pd.DataFrame(deadlines_data).drop_duplicates(),
        'salaries': pd.DataFrame(salaries_data).drop_duplicates(),
        'locations': pd.DataFrame(locations_data).drop_duplicates()
    }

# MySQL 연결 설정 함수
def create_db_connection(user, password, host, db_name):
    try:
        engine = sqlalchemy.create_engine(f'mysql+pymysql://root:easycow03@localhost/job_db')
        logging.info("MySQL Database connection 성공")
        return engine
    except Exception as e:
        logging.error(f"Database 연결 실패: {e}")
        return None

# 사용자 및 지원/북마크 데이터 생성 함수 (최소 100개 연동)
def generate_user_and_related_data(engine):
    users_df = pd.DataFrame([
        {"username": "user1", "email": "user1@example.com"},
        {"username": "user2", "email": "user2@example.com"},
        {"username": "user3", "email": "user3@example.com"}
    ])
    
    save_to_mysql(users_df, engine, table_name="user")
    
    query_job_ids = "SELECT id FROM job_notice LIMIT 100"
    job_ids_df = pd.read_sql(query_job_ids, con=engine)
    
    applications, bookmarks = [], []
    
    for user_id in range(1, 4):  # user_id 순환 (1~3번 사용자)
        for idx, row in job_ids_df.iterrows():
            applications.append({"user_id": user_id, "job_notice_id": row['id'], "status": "지원 완료"})
            bookmarks.append({"user_id": user_id, "job_notice_id": row['id']})
    
    applications_df = pd.DataFrame(applications)
    bookmarks_df = pd.DataFrame(bookmarks)
    
    save_to_mysql(applications_df, engine, table_name="application")
    save_to_mysql(bookmarks_df, engine, table_name="bookmark")

# 데이터 저장 함수 (모든 테이블에 저장)
def save_all_tables(separated_data, engine):
    save_to_mysql(separated_data['companies'], engine, table_name='company')
    save_to_mysql(separated_data['jobs'], engine, table_name='job_notice')
    save_to_mysql(separated_data['deadlines'], engine, table_name='deadline')
    save_to_mysql(separated_data['salaries'], engine, table_name='money')
    save_to_mysql(separated_data['locations'], engine, table_name='location')

# 데이터 저장 함수 (기존 save_to_mysql 유지)
def save_to_mysql(df, engine, table_name):
    try:
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
        logging.info(f"{table_name} 테이블에 데이터 저장 완료")
    except Exception as e:
        logging.error(f"{table_name} 테이블 저장 중 에러 발생: {e}")

# 주기적인 크롤링 실행 함수 (schedule 사용)
def scheduled_crawling():
    user = "root"
    password = "easycow03"
    host = "localhost"
    db_name = "job_db"

    engine = create_db_connection(user, password, host, db_name)

    if engine:
        df_jobs = crawl_saramin('python', pages=10)
        
        if df_jobs.empty:
            logging.error("크롤링 결과가 비어 있습니다.")
            return

        separated_data = separate_data(df_jobs.to_dict(orient='records'), engine)  # engine 전달
        
        save_all_tables(separated_data, engine)

        generate_user_and_related_data(engine)

# 스케줄 설정 (매일 1시간마다 실행)
schedule.every(60).minutes.do(scheduled_crawling)

if __name__ == "__main__":
    while True:
        schedule.run_pending()