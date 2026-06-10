import requests
import json
import os


def check_greenhouse(company_name):
    """
    Checks whether a given company uses Greenhouse as its job board provider.

    Params:
        company_name (str): The slug or normalized name
        of the company to check.

    Returns:
        str or None: The first valid Greenhouse job board URL if found,
        otherwise None.
    """
    urls = [
        f"https://boards.greenhouse.io/{company_name}",
        f"https://{company_name}.greenhouse.io"
    ]

    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200 and "jobs" in r.text.lower():
                return url
        except requests.RequestException:
            pass

    return None


def load_seed_companies():
    """
    Loads seed companies from seed_companies.json
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))

    json_path = os.path.join(base_dir, "seed_companies.json")
    json_path = os.path.normpath(json_path)

    with open(json_path, "r") as f:
        return json.load(f)


def save_greenhouse_companies(companies):
    """
    Saves detected Greenhouse companies to JSON file.
    """
    # remove duplicates while preserving order
    companies = list(dict.fromkeys(companies))

    base_dir = os.path.dirname(os.path.abspath(__file__))

    output_path = os.path.join(base_dir, "green_companies.json")
    output_path = os.path.normpath(output_path)

    with open(output_path, "w") as f:
        json.dump(companies, f, indent=2)

    return companies


def main():
    seed_companies = load_seed_companies()

    greenhouse_companies = []

    print(f"Testing {len(seed_companies)} companies...\n")

    for i, company in enumerate(seed_companies):
        print(f"[{i+1}/{len(seed_companies)}] Checking {company}")

        result = check_greenhouse(company)

        if result:
            print(f"FOUND: {company} -> {result}")
            greenhouse_companies.append(company)
        else:
            print(f"MISS: {company}")

    greenhouse_companies = save_greenhouse_companies(greenhouse_companies)

    print("\n======================")
    print(f"Final list: {greenhouse_companies}")
    print(f"Total Greenhouse companies: {len(greenhouse_companies)}")
    print("======================")


if __name__ == "__main__":
    main()
