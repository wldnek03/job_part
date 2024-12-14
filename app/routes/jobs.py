from flask import Blueprint, jsonify, request
from app.models import JobNotice, Company, Location, Money
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

bp = Blueprint('jobs', __name__)

@bp.route('/', methods=['GET'])
def get_jobs():
    """
    채용 공고 목록 조회
    ---
    tags:
      - Jobs
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: "페이지 번호"
      - name: per_page
        in: query
        type: integer
        required: false
        default: 20
        description: "페이지당 항목 수"
      - name: sort_by
        in: query
        type: string
        required: false
        default: id
        description: "정렬 기준 (예: id, title)"
      - name: sort_order
        in: query
        type: string
        required: false
        default: asc
        description: "정렬 순서 (asc 또는 desc)"
      - name: location
        in: query
        type: string
        required: false
        description: "지역 필터 (예: 서울)"
      - name: salary
        in: query
        type: string
        required: false
        description: "급여 필터 (예: 인기많은)"
      - name: company_name
        in: query
        type: string
        required: false
        description: "회사 이름 필터 (예: 네이버)"
      - name: category
        in: query
        type: string
        required: false
        description: "회사 카테고리 필터 (예: IT)"
      - name: keyword
        in: query
        type: string
        required: false
        description: "키워드 검색 (예: 개발자)"
    responses:
      200:
        description: "성공적으로 데이터를 반환합니다."
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')

    region = request.args.get('region')  # 'location' 대신 'region'
    salary = request.args.get('salary')
    company_name = request.args.get('company_name')
    category = request.args.get('category')
    keyword = request.args.get('keyword')
    
    exact_match = request.args.get('exact_match', 'false').lower() == 'true'

    query = JobNotice.query.options(joinedload(JobNotice.company))

    if region:
        query = query.join(Location).filter(Location.region == region)

    if salary:
        query = query.join(Money).filter(Money.salary == salary)
    
    if company_name:
        if exact_match:
            query = query.join(Company).filter(Company.name == company_name)
        else:
            query = query.join(Company).filter(Company.name.ilike(f"%{company_name}%"))
    
    if category:
        if hasattr(Company, 'category'):
            query = query.join(Company).filter(Company.category.ilike(f"%{category}%"))

    if keyword:
        query = query.filter(or_(
            JobNotice.title.ilike(f"%{keyword}%"),
            JobNotice.link.ilike(f"%{keyword}%")
        ))

    if sort_order == 'desc':
        query = query.order_by(getattr(JobNotice, sort_by).desc())
    else:
        query = query.order_by(getattr(JobNotice, sort_by))

    paginated_jobs = query.paginate(page=page, per_page=per_page)

    result = [{
        "id": job.id,
        "title": job.title,
        "link": job.link,
        "company_id": job.company_id,
        "company_name": job.company.name if job.company else None,
        "locations": [location.region for location in job.locations],  # 올바른 속성 사용 
        "salaries": [money.salary for money in job.salaries]
    } for job in paginated_jobs.items]

    return jsonify({
        "jobs": result,
        "total": paginated_jobs.total,
        "pages": paginated_jobs.pages,
        "current_page": paginated_jobs.page
    }), 200

@bp.route('/<int:id>', methods=['GET'])
def get_job(id):
    """
    특정 채용 공고 조회 
    ---
    tags:
      - Jobs 
    parameters:
      - name : id 
        in : path 
        type : integer 
        required : true 
        description : "공고 아이디"
    responses :
      200 :
          description : "특정 채용 공고의 세부 정보를 반환합니다."
          schema :
              type : object 
              properties :
                  id :
                      type : integer 
                  title :
                      type : string 
                  link :
                      type : string 
                  company_id :
                      type : integer 
                  company_name :
                      type : string 
                  locations :
                      type : array 
                      items :
                          type : string 
                  salaries :
                      type : array 
                      items :
                          type : string 
      404 :
          description : "해당 공고를 찾을 수 없음."
    """
    try:
        job = JobNotice.query.options(
            joinedload(JobNotice.company),
            joinedload(JobNotice.locations),
            joinedload(JobNotice.salaries)
          ).get_or_404(id)

        return jsonify({
            "id": job.id,
            "title": job.title,
            "link": job.link,
            "company_id": job.company_id,
            "company_name": job.company.name if job.company else None,
            "locations": [location.region for location in job.locations],  # 올바른 속성 사용 
            "salaries": [money.salary for money in job.salaries]
         }), 200

    except Exception as e:
         # 오류 로깅 및 디버깅 메시지 출력 (개발 환경에서만)
         print(f"Error fetching job notice with ID {id}: {e}")
         return jsonify({"error": f"An internal error occurred while fetching the job notice with ID {id}."}), 500

