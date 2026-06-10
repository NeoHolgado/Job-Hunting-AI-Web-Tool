import requests


def fetch_jobs(company: str):
    """
    Fetches a list of job postings for a given company from the Greenhouse API.

    Params:
        company (str): The Greenhouse board identifier (e.g., "discord")

    Returns:
        list[dict]: List of raw job objects from the API.
                    Returns an empty list if the request fails.
    """
    # Create Greenhouse job board URL
    base_url = (
        f"https://boards-api.greenhouse.io/v1/boards/"
        f"{company}/jobs?content=true"
    )

    # Send request to external API
    response = requests.get(base_url)

    # Return empty list if API request fails
    if response.status_code != 200:
        return []

    # Extract job listings from JSON response
    return response.json().get("jobs", [])
