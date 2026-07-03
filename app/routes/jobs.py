from flask import Blueprint, jsonify, request

from app.services.job_service import create_job, get_job_by_id

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

    data = request.get_json()
    if data is None:
        return jsonify({"error":"Request body must be json"}),400
    language = data.get("language")
    source_code = data.get("source_code")

    if not language:
        return jsonify({"error":"language is required"}),400
    if not source_code:
        return jsonify({"error": "source code is required"}),400
    
    if language != "python":
        return jsonify({"error":"only python is supported for now"}),400
    
    job = create_job(language=language,source_code=source_code)

    return jsonify(job.to_dict()),201

jobs_bp.route("/jobs/<int:job_id>",methods=['GET'])
def get_job(job_id):
    job = get_job_by_id(job_id)
    if job is None:
        return jsonify({"error":"job not found"}),404
    return jsonify(job.to_dict()),200
