import psycopg2
from utils.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_URL


# This function was written by one of my team members
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


def get_supabase_db_connection():
    """
    Creates and returns a connection to the supabase database.

    Returns:
        psycopg2 connection object
    """
    database_url = DB_URL

    if not database_url:
        raise ValueError("DATABASE_URL is not set in environment variables")

    return psycopg2.connect(database_url)
