from services.db_service import get_supabase_db_connection


def get_ranked_jobs(
    conn,
    resume_id: int,
    resume_group_id: int,
    limit: int = 10
):
    """
    Retrieves a list of jobs ranked by cosine similarity
    """
    query = """
    SELECT
        j.id,
        j.external_job_id,
        j.title,
        j.company,
        j.location,
        j.description,
        j.url,
        j.date_posted,
        1 - (j.embedding <=> re.embedding) AS similarity_score
    FROM jobs j
    CROSS JOIN resume_embeddings re
    WHERE re.resume_id = %s
        AND re.resume_group_id = %s
        AND j.embedding IS NOT NULL
    ORDER BY j.embedding <=> re.embedding
    LIMIT %s
    """

    # Execute query
    with conn.cursor() as cur:
        cur.execute(query, (resume_id, resume_group_id, limit))

        rows = cur.fetchall()

        formatted_jobs = []

        for row in rows:
            (
                job_id,
                external_job_id,
                title,
                company,
                location,
                description,
                url,
                date_posted,
                similarity_score
            ) = row

            formatted_jobs.append({
                "id": job_id,
                "external_job_id": external_job_id,
                "title": title,
                "company": company,
                "location": location,
                "description": description,
                "url": url,
                "date_posted": (
                    date_posted.isoformat()
                    if date_posted else None
                ),
                "similarity_score": float(similarity_score)
            })

        return formatted_jobs


if __name__ == '__main__':
    conn = get_supabase_db_connection()

    try:
        results = get_ranked_jobs(
            conn,
            resume_id=16,
            resume_group_id=6,
            limit=10
        )

        for job in results:
            print(job)

    finally:
        conn.close()
