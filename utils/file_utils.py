import json
import os
from dataclasses import asdict


def save_jobs_to_json(jobs, filename="jobs.json"):
    """
    Saves jobs to a local JSON file for debugging purposes.
    """
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "pipeline",
        filename
    )

    with open(output_path, "w") as f:
        json.dump(
            [asdict(job) for job in jobs],
            f,
            indent=2,
            ensure_ascii=False
        )
