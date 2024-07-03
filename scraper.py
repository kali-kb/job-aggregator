from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import requests
import lxml
import bs4
import re



def get_job_links():
    job_links = []
    response = requests.get("https://hahu.jobs/jobs")
    soup = bs4.BeautifulSoup(response.content, "html.parser")
    for link in soup.find_all('a', href=lambda href: href and href.startswith('https://app.hahu.jobs/app/jobs/')):
        pattern = r"https://app\.hahu\.jobs/app/jobs/([a-f0-9]+)\?save=true"
        match = re.search(pattern, link['href'])
        if match:
            path = "https://hahu.jobs/jobs"
            job_id = str(match.group(1))
            job_path = f"{path}/{job_id}"
            job_links.append(job_path)

    return job_links

# print(scrape_job_links())

#job_link https://hahu.jobs/jobs/66825d7b484dc27c347aa4eb
def get_job_content(job_link):
    response = requests.get(job_link)
    page = bs4.BeautifulSoup(response.content, "html.parser")
    job_title = page.select_one(".font-extrabold").text.strip()
    company = page.select_one("p.text-secondary-6").text.strip()
    location = page.select_one(".grid > div:nth-child(2) > p:nth-child(2)").text.strip()
    experience = page.select_one("div.gap-2:nth-child(3) > p:nth-child(2)").text.strip()
    number_of_positions = page.select_one("div.items-center:nth-child(4) > p:nth-child(2)").text.strip()
    education = page.select_one("#job_description > ul:nth-child(5) > li:nth-child(1) > p:nth-child(1)")
    apply_link = page.select(".mb-20")
    # tree = etree.HTML(str(page))

    return page.prettify()
    # education = tree.xpath("/html/body/div[1]")
    # if number_of_positions:
    #     number_of_positions = number_of_positions.text
    # else:
    #     number_of_positions = None
    # return job_title, company, location, apply_link, experience, number_of_positions


# print(get_job_content("https://hahu.jobs/jobs/ZX57o7cmPELKwZC"))

# def dynamic_scraping(link):
#     driver = webdriver.Chrome()
#     driver.get(link)
#     element = driver.find_element(By.CSS_SELECTOR, ".md\:mt-12 > a:nth-child(1)")
#     return element

# print(dynamic_scraping("https://hahu.jobs/jobs/ZX57o7cmPELKwZC"))
