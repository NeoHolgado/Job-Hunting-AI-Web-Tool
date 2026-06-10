from dataclasses import dataclass


@dataclass
class Job:
    """
    Job object schema
    """
    external_job_id: str        # Greenhouse job id
    title: str
    company: str
    location: str
    description: str
    embedding: list[float] | None
    url: str
    date_posted: str | None


@dataclass
class RankedJob:
    """
    Similarity score schema
    """
    job: Job
    similarity_score: float
