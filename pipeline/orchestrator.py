import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from pipeline.jobs_pipeline import run_jobs_pipeline
from services.db_service import get_supabase_db_connection
from services.job_service import insert_jobs_into_db
from utils.file_utils import save_jobs_to_json


def load_greenhouse_companies():
    """
    Loads the list of companies that use Greenhouse job boards.

    The company list is stored in a JSON file and contains the
    identifiers required to query the Greenhouse API.

    Returns:
        list[str]: List of company identifiers
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))

    json_path = os.path.join(
        base_dir,
        "..",
        "ingestion",
        "green_companies.json"
    )

    json_path = os.path.normpath(json_path)

    with open(json_path, "r") as f:
        return json.load(f)


def process_company(company):
    """
    Runs full pipeline for a single company.
    Calculates

    Params:
        company: Company utilizing Greenhouse job boards

    Returns:
        jobs: List of processed job objects for a company
        total_time: Total processing time for a company
    """
    db_connection = get_supabase_db_connection()

    try:
        print(f"[START] {company}")
        process_start = time.perf_counter()

        # Fetch and process jobs
        fetch_start = time.perf_counter()
        jobs = run_jobs_pipeline(company)
        fetch_time = time.perf_counter() - fetch_start

        # Insert into DB
        insert_start = time.perf_counter()
        insert_jobs_into_db(jobs, db_connection)
        insert_time = time.perf_counter() - insert_start

        # Total time
        total_time = time.perf_counter() - process_start

        # Print time
        print(
            f"\n[DONE] {company} | "
            f"Num jobs = {len(jobs)} | "
            f"Fetch jobs time = {fetch_time:.2f}s | "
            f"DB insert time = {insert_time:.2f}s | "
            f"Total processing time = {total_time:.2f}s"
        )

        return jobs, total_time

    except Exception as e:
        print(f"[ERROR] {company}: {e}")
        return [], 0

    finally:
        db_connection.close()


def run_pipeline(max_workers: int = 5, save_json: bool = True):
    """
    Executes the full multi-company job ingestion pipeline in parallel.

    Workflow:
    1. Load list of companies
    2. Run each company pipeline concurrently using threads
    3. Batch insert jobs into DB
    4. Aggregate all processed jobs
    5. Optionally save jobs to JSON for debugging
    6. Print pipeline performance summary

    Params:
        max_workers: Maximum number of concurrent worker threads
        save_json: If true, saves all processed jobs to jobs.json

    Returns:
        list[Job]: Combined list of all processed job objects
    """
    # Load companies to process
    companies = load_greenhouse_companies()

    # Container for all job results and total processing time
    all_jobs = []

    # Sum of all individual company processing times
    total_company_time = 0

    # Overall pipeline timer
    pipeline_start = time.perf_counter()

    # Create thread pool for parallel execution
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all companies to thread pool
        futures = {
            executor.submit(process_company, company): company
            for company in companies
        }

        # Process completed threads as they finish
        for future in as_completed(futures):
            company = futures[future]

            try:
                jobs, duration = future.result()

                # Aggregate jobs from completed worker
                all_jobs.extend(jobs)

                # Add company processing time
                total_company_time += duration

            except Exception as e:
                print(f"[FAILED] {company}: {e}")

    # Calculate total pipeline runtime
    pipeline_time = time.perf_counter() - pipeline_start

    # Optionally save to JSON
    if save_json:
        save_jobs_to_json(all_jobs)

    # Final Pipeline Summary
    print(
        "\n==========================\n"
        f"TOTAL JOBS: {len(all_jobs)}\n"
        f"PIPELINE TIME: {pipeline_time:.2f}s\n"
        f"SUM OF COMPANY TIMES {total_company_time:.2f}s\n"
        "==========================\n"
    )

    return all_jobs


if __name__ == "__main__":
    run_pipeline(max_workers=10)
