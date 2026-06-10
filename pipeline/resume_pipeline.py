import requests
from services.db_service import get_supabase_db_connection
from ai.embeddings import generate_embedding
from dotenv import load_dotenv


load_dotenv()

BASE_URL = "https://resume-backend-1008648100114.us-west1.run.app"


def fetch_resume_text(
    resume_group_id: int,
    resume_id: int,
    token: str
) -> dict:
    """
    Fetches parsed resume text from backend API.

    Params:
        resume_group_id: ID integer of resume group
        resume_id: ID integer of resume
        token: Auth bearer token for user session

    Returns:
        Response from route
    """
    url = f"{BASE_URL}/resume/{resume_group_id}/{resume_id}/parse"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch resume: {response.text}")

    return response.json()


def insert_resume(conn, resume_data: dict):
    """
    Inserts parsed resume data into database.

    Params:
        conn: DB connection string
        resume_data: Resume text data from route
    """

    # Clean resume text
    cleaned_text = clean_text(resume_data["text"])

    # Insert resume data into supabase DB
    query = """
    INSERT INTO resumes (
        resume_id,
        resume_group_id,
        text
    )
    VALUES (%s, %s, %s)
    """

    # Connect to DB and execute query
    with conn.cursor() as cur:
        cur.execute(
            query,
            (
                resume_data["resume_id"],
                resume_data["resume_group_id"],
                cleaned_text
            )
        )

    conn.commit()


def run_single_resume(
    resume_data: dict
):
    """
    Full pipeline:
    1. Use provided JWT token
    2. Fetch parsed resume
    3. Insert into DB

    Params:
        resume_group_id: ID integer of resume group
        resume_id: ID integer of resume
        token: Auth bearer token for user session
    """
    conn = get_supabase_db_connection()

    try:
        # insert resume data into supabase DB
        insert_resume(conn, resume_data)
        print(f"[SUCCESS] Inserted resume {resume_data['resume_id']}")

        # Generate embedding for resume text
        embedding = generate_embedding(resume_data["text"])
        print(f"[SUCCESS] Generated embedding of length: {len(embedding)}")

        # Insert embedding into resume embedding table
        insert_resume_embedding(conn, resume_data, embedding)
        print(f"[SUCCESS] Inserted embedding of length: {len(embedding)}")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] {e}")
        raise

    finally:
        conn.close()


def clean_text(text: str) -> str:
    """
    Removes invalid NUL characters from text

    Params:
        text: raw resume text

    Returns:
        str: processed resume text
    """
    return text.replace("\x00", "")


def insert_resume_embedding(conn, resume_data: dict, embedding: list[float]):
    """
    Inserts resume embedding into database

    Params:
        conn: supabase connection string
        resume_data: Resume data
        embedding: Generated embeddings from resume text
    """
    # Insert embeddings into supabase DB
    query = """
    INSERT INTO resume_embeddings (
        resume_id,
        resume_group_id,
        embedding
    )
    VALUES (%s, %s, %s)
    ON CONFLICT (resume_id, resume_group_id)
    DO UPDATE SET
        embedding = EXCLUDED.embedding,
        created_at = CURRENT_TIMESTAMP
    """

    with conn.cursor() as cur:
        cur.execute(
            query,
            (
                resume_data["resume_id"],
                resume_data["resume_group_id"],
                str(embedding)
            )
        )

    conn.commit()


def delete_resume_from_supabase(*, resume_group_id: int, resume_id: int):
    """
    Deletes resume text and embeddings from Supabase tables

    Params:
        resume_group_id: Group ID integer of resume
        resume_id: ID integer of resume
    """
    conn = get_supabase_db_connection()

    try:
        with conn.cursor() as cur:
            # Delete embedding
            cur.execute(
                """
                DELETE FROM resume_embeddings
                WHERE resume_group_id = %s
                    AND resume_id = %s
                """,
                (resume_group_id, resume_id)
            )

            # Delete resume text
            cur.execute(
                """
                DELETE FROM resumes
                WHERE resume_group_id = %s
                    AND resume_id = %s
                """,
                (resume_group_id, resume_id)
            )

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to delete resume from Supabase: {str(e)}")

    finally:
        conn.close()


def delete_resumes_by_group_from_supabase(*, resume_group_id: int):
    """
    Deletes all resume text and embeddings from Supabase tables
    for a given resume group.

    Params:
        resume_group_id: Group ID integer of resumes to delete
    """
    conn = get_supabase_db_connection()

    try:
        with conn.cursor() as cur:
            # Delete all embeddings for this resume group
            cur.execute(
                """
                DELETE FROM resume_embeddings
                WHERE resume_group_id = %s
                """,
                (resume_group_id,)
            )

            # Delete all resume text records for this resume group
            cur.execute(
                """
                DELETE FROM resumes
                WHERE resume_group_id = %s
                """,
                (resume_group_id,)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to delete resumes from Supabase: {str(e)}")

    finally:
        conn.close()
