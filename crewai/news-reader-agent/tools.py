import time

from crewai.tools import tool
from crewai_tools import SerperDevTool
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

search_tool = SerperDevTool(
    n_results=2,
)


@tool
def scrape_tool(url: str):
    """
    Use this when you need to read the content of a website.
    Returns the content of a website, in case the website is not available, it returns 'No content'.
    Input should be a `url` string. for example (https://www.reuters.com/world/asia-pacific/cambodia-thailand-begin-talks-malaysia-amid-fragile-ceasefire-2025-08-04/)
    """
    print(f"Scrapping URL: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # run browser without window.
        page = browser.new_page()  # create new page
        page.goto(url)
        time.sleep(5)
        html = page.content()  # extract html
        browser.close()
        soup = BeautifulSoup(html, "html.parser")  # manipulate html
        unwanted_tags = [
            "header",
            "footer",
            "nav",
            "aside",
            "script",
            "style",
            "noscript",
            "iframe",
            "form",
            "button",
            "input",
            "select",
            "textarea",
            "img",
            "svg",
            "canvas",
            "audio",
            "video",
            "embed",
            "object",
        ]
        for tag in soup.find_all(unwanted_tags):  # remove unwanted elements
            tag.decompose()
        # delete html code and return only text content separated by " "
        content = soup.get_text(separator=" ")
        return content if content != "" else "No content"
