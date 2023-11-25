from utils import attach_symbol, convert_string_to_datetime, clean_data
import logging
import asyncio
import streamlit as st
from urllib.parse import quote
from tqdm import tqdm
from playwright.async_api import Locator, Page, Playwright, async_playwright

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def extract_data(job_element: Locator) -> None:
    """The function `extract_data` extracts job data from a web page using XPath locators and saves it in a
    dictionary format.

    Parameters
    ----------
    job_element : Locator
        The `job_element` parameter is a Locator object that represents a specific job element on a
    webpage. It is used to extract data from that element.

    """

    xpath_title = "//h2[@class='KLsYvd']"
    xpath_location = "//div[@class='sMzDkb']"
    xpath_details = "//span[@class='LL4CDc']"
    xpath_job_description_span = "//span[@class='HBvzbc']"
    xpath_job_highlights = "//div[@class='JxVj3d']"
    xpath_employer = 'div[class*="nJlQNd"]'
    xpath_url = "a[class*='pMhGee']"
    

    title = await job_element.locator(xpath_title).inner_text()
    location = await job_element.locator(xpath_location).inner_text()
    details = await job_element.locator(xpath_details).all_inner_texts()
    post_date = details[0] if details[0].find('ago') != -1 else None
    salary_details = [detail for detail in details if detail.find('an hour')!=-1 or detail.find('a year')!=-1]
    salary = salary_details[0] if salary_details else ""
    employer = await job_element.locator(xpath_employer).inner_text()
    job_description = await job_element.locator(xpath_job_description_span).all_inner_texts()
    urls = await job_element.locator(xpath_url).all()
    url = None
    for u in urls:
        href_value = await u.get_attribute('href')
        if href_value is not None:
            url = href_value
            break

    highlights_elements = job_element.locator(xpath_job_highlights)
    highlights_count = await highlights_elements.count()
    all_text_highlights = []
    for i in range(highlights_count):
        all_text_highlights.extend(
            await highlights_elements.nth(i)
            .locator("//div[@class='IiQJ2c']")
            .all_inner_texts()
        )

    title = clean_data(title)
    location = clean_data(location)
    post_date = convert_string_to_datetime(clean_data(post_date)).strftime("%Y-%m-%d") if post_date is not None else ""
    salary = attach_symbol(salary)
    salary = clean_data(salary)
    job_description = clean_data(job_description)
    highlights = clean_data(all_text_highlights)
    employer = clean_data(employer)
    url = clean_data(url) if url is not None else ""

    data_to_save = {
        "title": title,
        "location": location,
        "post_date": post_date,
        "salary": salary,
        "employer": employer,
        "job_description": job_description,
        "job_highlights": highlights,
        "url": url
    }

    st.session_state.data.append(data_to_save)


async def parse_listing_page(page: Page) -> None:
    """The `parse_listing_page` function parses a listing page to extract job details.

    Parameters
    ----------
    page : Page
        The `page` parameter is an instance of the `Page` class. It represents a web page that you want to
    parse.

    """
    xpath_jobs_tabs = "//div[@class='gws-plugins-horizon-jobs__tl-lif']"

    try:
        await page.wait_for_selector(xpath_jobs_tabs)
    except Exception as e:
        # Playwright Timeout error can occur when no jobs are found in the search
        logger.debug(e)
        return

    jobs = page.locator(xpath_jobs_tabs)
    jobs_count = await jobs.count()
    logger.debug(f"Parse {jobs_count} jobs")

    xpath_job_detail = "//div[@id='gws-plugins-horizon-jobs__job_details_page']"
    job_details = page.locator(xpath_job_detail)
    for i in range(jobs_count):
        job_element = job_details.nth(i)
        await extract_data(job_element)

async def run(playwright: Playwright, max_scroll: int, query: str) -> None:
    """The function opens a browser, navigates to a Google search page for job listings, scrolls down the
    page, parses the listings, saves the data, and processes the keyword.

    Parameters
    ----------
    playwright : Playwright
        The `playwright` parameter is an instance of the Playwright class, which is used to control the
    browser and perform actions on web pages.
    max_scroll : int
        The `max_scroll` parameter determines the maximum number of times the page will be scrolled down to
    load more content. It is an integer value that specifies the number of scroll actions to perform.
    query : str
        The `query` parameter is a string that represents the search query to be used on Google. It is used
    to search for job listings related to the query.

    """
    # Initializing browser and opening a new page
    browser = await playwright.firefox.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()

    url = f"https://www.google.com/search?hl=en&q={quote(query)}&ibp=htl;jobs"
    await page.goto(url, wait_until="domcontentloaded")

    await page.wait_for_timeout(2000)
    await asyncio.sleep(5)

    job_tree = page.locator("//div[@role='tree']")
    await job_tree.click()
    previousYBound = 0

    for _ in tqdm(range(max_scroll), desc="Scroll"):
        await page.mouse.wheel(0, 5000)
        await asyncio.sleep(2)
        box3 = await job_tree.bounding_box()
        if previousYBound == box3["y"]:
            break
        previousYBound = box3["y"]

    await parse_listing_page(page)
    logger.debug(f"Finished Parsing `{query}`")
    await context.close()
    await browser.close()