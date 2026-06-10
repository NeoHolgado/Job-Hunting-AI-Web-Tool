import json
import os
from psycopg2.extras import execute_values


def get_jobs_from_json():
    """
    TESTING ONLY:
    Loads jobs from local JSON file

    returns:
        list[dict]: List of job objects in dictionary format
    """
    # Resolve path to pipeline output file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "..", "pipeline", "jobs.json")
    json_path = os.path.normpath(json_path)

    # Load and return job data
    with open(json_path, "r") as f:
        return json.load(f)


def get_jobs_from_db(db_connection):
    """
    Primary data source for job listings.
    Queries PostgreSQL database for all stored jobs.

    Params:
        db_connection: Active database connection
    """
    cursor = db_connection.cursor()

    # Query all jobs from database
    cursor.execute("""
        SELECT
            id,
            external_job_id,
            title,
            company,
            location,
            description,
            embedding,
            url,
            date_posted
        FROM jobs
        ORDER BY date_posted DESC
    """)

    rows = cursor.fetchall()

    # Convert column names + rows into dictionaries
    columns = [desc[0] for desc in cursor.description]

    jobs = []
    for row in rows:
        jobs.append(dict(zip(columns, row)))

    cursor.close()
    return jobs


def insert_jobs_into_db(jobs, db_connection):
    """
    Batch inserts Job objects into PostgreSQL.

    params:
        jobs: list[Job]
        db_connection: Active DB connection
    """
    # Skip of no jobs to insert
    if not jobs:
        return

    cursor = db_connection.cursor()

    # Transform job objects into tuple format
    values = [
        (
            job.external_job_id,
            job.title,
            job.company,
            job.location,
            job.description,
            job.embedding,
            job.url,
            job.date_posted
        )
        for job in jobs
    ]

    # SQL insert query
    query = """
        INSERT INTO jobs (
            external_job_id,
            title,
            company,
            location,
            description,
            embedding,
            url,
            date_posted
        )
        VALUES %s
        ON CONFLICT (external_job_id) DO NOTHING;
    """

    try:
        # Bulk insert all rows in one query
        execute_values(
            cursor,
            query,
            values
        )

        db_connection.commit()

    except Exception as e:
        # Rollback to prevent partial writes
        db_connection.rollback()
        print(f"Bulk insert failed: {e}")

    finally:
        cursor.close()
