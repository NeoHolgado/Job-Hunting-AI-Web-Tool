from flask import Blueprint, request, jsonify, g
from services.resume_service import (
    upload_resume_version,
    get_resume_data,
    get_resume_file_url,
    delete_resume,
    get_resumes_for_group,
    get_resume_text
)
from services.db_service import get_db_connection
from services.resume_group_service import create_resume_group, get_resume_groups, delete_resume_group
from utils.auth import require_auth

from pipeline.resume_pipeline import (
    run_single_resume,
    delete_resume_from_supabase,
    delete_resumes_by_group_from_supabase
)


resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/resume/upload", methods=["POST"])
@require_auth
def upload_resume_route():
    db_connection = None
    try:
        user_id = g.user_id
        file = request.files["file"]
        resume_group_id = int(request.form["resume_group_id"])

        db_connection = get_db_connection()

        resume_upload = upload_resume_version(
            user_id=user_id,
            resume_group_id=resume_group_id,
            file_name=file.filename,
            file_bytes=file.read(),
            db_connection=db_connection,
        )

        resume_id = resume_upload["id"]

        resume_data = get_resume_text(
            user_id=g.user_id,
            resume_group_id=resume_group_id,
            resume_id=resume_id,
            db_connection=db_connection,
        )

        run_single_resume(
            resume_data=resume_data
        )

        return jsonify({
            "message": "Resume uploaded and processed successfully",
            "resume": resume_upload
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if db_connection:
            db_connection.close()


@resume_bp.route("/resume/<resume_group_id>/<resume_id>", methods=["GET"])
@require_auth
def retrieve_resume_metadata_route(resume_group_id, resume_id):
    db_connection = None
    try:
        db_connection = get_db_connection()

        result = get_resume_data(
            user_id=g.user_id,
            resume_group_id=resume_group_id,
            resume_id=resume_id,
            db_connection=db_connection,
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if db_connection:
            db_connection.close()


@resume_bp.route("/resume/<resume_group_id>/<resume_id>/file", methods=["GET"])
@require_auth
def retrieve_resume_file_url_route(resume_group_id, resume_id):
    db_connection = None
    try:
        db_connection = get_db_connection()

        result = get_resume_file_url(
            user_id=g.user_id,
            resume_group_id=resume_group_id,
            resume_id=resume_id,
            db_connection=db_connection,
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if db_connection:
            db_connection.close()


@resume_bp.route("/resume/<resume_group_id>/<resume_id>/parse", methods=["GET"])
@require_auth
def retrieve_resume_text_route(resume_group_id, resume_id):
    db_connection = None
    try:
        db_connection = get_db_connection()

        result = get_resume_text(
            user_id=g.user_id,
            resume_group_id=resume_group_id,
            resume_id=resume_id,
            db_connection=db_connection,
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if db_connection:
            db_connection.close()


@resume_bp.route("/resume/<resume_group_id>", methods=["GET"])
@require_auth
def get_resumes_for_group_route(resume_group_id):
    db_connection = None

    try:
        db_connection = get_db_connection()

        result = get_resumes_for_group(
            user_id=g.user_id,
            resume_group_id=resume_group_id,
            db_connection=db_connection,
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if db_connection:
            db_connection.close()


@resume_bp.route("/resume/<resume_group_id>/<resume_id>", methods=["DELETE"])
@require_auth
def delete_resume_route(resume_group_id, resume_id):
    db_connection = None
    try:
        db_connection = get_db_connection()

        result = delete_resume(
            user_id=g.user_id,
            resume_group_id=resume_group_id,
            resume_id=resume_id,
            db_connection=db_connection,
        )

        # Delete resume from Supabase
        delete_resume_from_supabase(
            resume_group_id=resume_group_id,
            resume_id=resume_id
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if db_connection:
            db_connection.close()


@resume_bp.route("/resume_group/create", methods=["POST"])
@require_auth
def create_resume_group_route():
    db_connection = None
    try:
        data = request.get_json()
        name = data["name"]

        db_connection = get_db_connection()

        result = create_resume_group(
            user_id=g.user_id,
            name=name,
            db_connection=db_connection,
        )

        return jsonify(result), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if db_connection:
            db_connection.close()


@resume_bp.route("/resume_group", methods=["GET"])
@require_auth
def retrieve_resume_groups_route():
    db_connection = None
    try:
        db_connection = get_db_connection()

        result = get_resume_groups(
            user_id=g.user_id,
            db_connection=db_connection,
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if db_connection:
            db_connection.close()


@resume_bp.route("/resume_group/<resume_group_id>", methods=["DELETE"])
@require_auth
def delete_resume_group_route(resume_group_id):
    db_connection = None
    try:
        db_connection = get_db_connection()

        result = delete_resume_group(
            user_id=g.user_id,
            resume_group_id=resume_group_id,
            db_connection=db_connection,
        )

        # Delete all resumes by group from supabase
        delete_resumes_by_group_from_supabase(resume_group_id=resume_group_id)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if db_connection:
            db_connection.close()
