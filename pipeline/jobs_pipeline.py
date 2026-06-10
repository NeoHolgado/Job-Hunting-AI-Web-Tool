import time
from ingestion.jobs_api import fetch_jobs
from pipeline.preprocess import clean_html
from models.schemas import Job


def run_jobs_pipeline(company: str, output_file: str = "jobs.json"):
    """
    Executes the full job ingestion and processing pipeline
    for a given company.

    Params:
        company (str): Company name (e.g., "stripe")
        output_file (str): Path to output JSON file

    Returns:
        results: List of processed job objects
    """
    # Fetch job listings
    jobs = fetch_jobs(company)

    # Container for fully processed job objects
    results = []

    # Iterate through each job and fetch full details
    for i, job in enumerate(jobs):

        cleaned_text = clean_html(job.get("content", ""))

        job_obj = Job(
            external_job_id=str(job.get("id")),
            title=job.get("title", "N/A"),
            company=company,
            location=job.get("location", {}).get("name", "N/A"),
            description=cleaned_text,
            embedding=None,         # Embedding is NONE until implemented
            url=job.get("absolute_url", ""),
            date_posted=job.get("first_published")
        )

        # Store processed job
        results.append(job_obj)

        # Rate limiting to avoid overwhelming API
        time.sleep(0.01)

    return results
