from flask import Blueprint, jsonify, request

from app.services.job_service import create_job, get_job_by_id
from app.services.job_validation_services import validate_job_submission

jobs_bp = Blueprint("jobs", __name__)

@jobs_bp.route("/jobs", methods=['POST'])
def submit_job():
    """
        Expected json body:
        {
            "language":"python",
            "source_code": "print('hello')"
            }
    """

    data = request.get_json(silent=True)
    
    is_valid, error_message = validate_job_submission(data)

    if not is_valid:
        return jsonify({
            "error": error_message
        }),400
    
    language = data["language"].strip().lower()
    source_code = data["source_code"]
    
    job = create_job(language=language,source_code=source_code)

    return jsonify(job.to_dict()),201

jobs_bp.route("/jobs/<int:job_id>",methods=['GET'])
def get_job(job_id):
    job = get_job_by_id(job_id)
    if job is None:
        return jsonify({"error":"job not found"}),404
    return jsonify(job.to_dict()),200
