from flask import Blueprint, jsonify

from app.models import JobNotice

bp = Blueprint('jobs', __name__)

@bp.route('/', methods=['GET'])
def get_jobs():
    jobs = JobNotice.query.all()
    result = [{"id": job.id, "title": job.title} for job in jobs]
    
    return jsonify(result), 200

@bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = JobNotice.query.get_or_404(job_id)
    
    return jsonify({
        "id": job.id,
        "title": job.title,
        "link": job.link,
        "company_id": job.company_id,
    }), 200