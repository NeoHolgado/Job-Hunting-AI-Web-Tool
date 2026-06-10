from flask import Blueprint, jsonify
from services.db_service import get_supabase_db_connection
from services.recommendation_service import get_ranked_jobs
from utils.auth import require_auth

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route(
    "/recommendations/<int:resume_group_id>/<int:resume_id>",
    methods=["GET"]
)
@require_auth
def get_resume_similarity_list(resume_group_id, resume_id):
    """
    GET /recommendations/<int:resume_group_id>/<int:resume_id>

    Retrieves a list of jobs ranked by similarity score.

    Response:
        {
            "resume_group_id": int,
            "resume_id": int,
            "jobs": [ranked_job]
        }
    """
    db_connection = None

    try:
        db_connection = get_supabase_db_connection()

        ranked_jobs = get_ranked_jobs(
            db_connection,
            resume_id=resume_id,
            resume_group_id=resume_group_id,
            limit=10
        )

        return jsonify({
            "resume_group_id": resume_group_id,
            "resume_id": resume_id,
            "jobs": ranked_jobs
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if db_connection:
            db_connection.close()
