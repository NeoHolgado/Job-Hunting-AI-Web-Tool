from bs4 import BeautifulSoup
import html


def clean_html(raw_html: str) -> str:
    """
    Converts raw HTML content into clean, plain text.

    Params:
        raw_html (str): Raw HTML string from an external source

    Returns:
        str: Cleaned, normalized plain text string
    """
    if not raw_html:
        return ""

    # Unescape HTML entities
    unescaped = html.unescape(raw_html)

    # Parse real HTML
    soup = BeautifulSoup(unescaped, "html.parser")

    # Extract text
    text = soup.get_text(separator=" ")
    text = " ".join(text.split())

    return text
