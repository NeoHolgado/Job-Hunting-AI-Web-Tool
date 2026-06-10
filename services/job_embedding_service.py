from ai.embeddings import generate_embedding
from services.db_service import get_supabase_db_connection
import time


def get_jobs_missing_embeddings(conn, limit: int = 100):
    """
    Get jobs that are missing embeddings.
    """
    # Retrieve jobs where the embeddings are null
    query = """
    SELECT
        id,
        title,
        company,
        location,
        description
    FROM jobs
    WHERE embedding is NULL
    LIMIT %s
    """

    with conn.cursor() as cur:
        cur.execute(query, (limit,))
        return cur.fetchall()


def update_job_embedding(conn, job_id: int, embedding: list[float]):
    """
    Update embeddings for jobs.
    """
    query = """
    UPDATE jobs
    SET embedding = %s
    WHERE id = %s
    """

    with conn.cursor() as cur:
        cur.execute(query, (embedding, job_id))


def generate_missing_job_embeddings(conn, batch_size: int = 100):
    """
    Generate embeddings for jobs.
    """
    total_embedded = 0

    while True:
        jobs = get_jobs_missing_embeddings(conn, batch_size)

        if not jobs:
            print("[DONE] No jobs missing embeddings")
            break

        print(f"[INFO] Processing batch of {len(jobs)} jobs")

        for job in jobs:
            job_id, title, company, location, description = job

            job_text = f"""
            Title": {title}
            Company: {company}
            Location: {location}
            Description: {description}
            """

            embedding = generate_embedding(job_text)
            update_job_embedding(conn, job_id, embedding)

            total_embedded += 1
            print(f"[SUCCESS] Embedded job {job_id}")
            time.sleep(6)

        conn.commit()
        print(f"[INFO] Total embedded so far: {total_embedded}")


if __name__ == "__main__":
    conn = get_supabase_db_connection()

    try:
        generate_missing_job_embeddings(conn, batch_size=100)

    finally:
        conn.close()
