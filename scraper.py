from fastapi import FastAPI
from datetime import datetime, timedelta
import pprint
import uvicorn
from formatter import MessageContent
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import TelegramError
from dotenv import load_dotenv
from os import getenv
from datetime import timedelta
import logging
import asyncio
from lxml import etree
import json
import pprint
import requests
import lxml
import bs4
import re

app = FastAPI()


# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


def job_detail(detail_page_link):
    response = requests.get(detail_page_link)
    soup = bs4.BeautifulSoup(response.content, "html.parser")
    company = soup.find("h1").text
    date = soup.find("time").text
    about_post = {"vacancy_link": detail_page_link, "company":company, "date": date}
    job_listings = []
    current_job = {}

    def extract_text(element):
        if isinstance(element, bs4.NavigableString):
            return element.strip()
        return ' '.join(extract_text(child) for child in element.children if child.name != 'br')

    for element in soup.find_all(['h4', 'p']):
        if element.name == 'h4':
            if current_job:
                job_listings.append(current_job)
            current_job = {'title': extract_text(element), 'details': []}
        elif element.name == 'p' and current_job:
            current_job['details'].append(extract_text(element))

    if current_job:
        job_listings.append(current_job)

    return about_post, job_listings
    # for job in job_listings:
    #     print(f"Title: {job['title']}")
    #     print("Details:")
    #     for detail in job['details']:
    #         print(f"- {detail}")
    #     print("\n")
    
    print(job_listings)


def daily_jobs_links():
    response = requests.get("https://dailyjobsethiopia.com/category/banking-jobs/")
    page = bs4.BeautifulSoup(response.content, "html.parser")
    title_date_container = page.find_all("header", class_="entry-header")
    links = []
    for title_date in title_date_container:
        if title_date:
            job_detail_link = title_date.find("h2", class_="entry-title").a.get("href")
            date = title_date.find("time").text
            date_obj = datetime.strptime(date, "%B %d, %Y")
            yesterday = datetime.now().date() - timedelta(days=1)
            if date_obj.date() == yesterday:
                links.append(job_detail_link)
                # print(job_detail(job_detail_link))
    return links
            


class HahuJobsQuery:
    def __init__(self):
        self.endpoint = getenv("HAHU_ENDPOINT")

    def get_jobs(self):
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        start_of_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day).isoformat() + "+00:00"
        query = f"""
        query {{
            jobs(where: {{expired: {{_eq: false}}, years_of_experience: {{_eq: 0}}, created_at: {{_gte: "{start_of_yesterday}"}}}}) {{
                id
                title
                type
                location
                application_method
                job_application_city {{
                    name
                }}
                job_cities {{
                    city {{
                        name
                    }}
                }}
                application_email
                gender_priority
                expired
                deadline
                years_of_experience
                max_years_of_experience
                application_method
                application_url
                salary
                summary
                how_to_apply
                created_at
                description
                entity {{
                    name
                }}
                sub_sector {{
                    name    
                }}
            }}
        }}
        """
        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "query": query
        }
        response = requests.post(self.endpoint, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('data', {}).get('jobs', [])
            for job in jobs:
                job['source'] = 'hahu'
            return jobs        
        else:
            logger.error(f"Error fetching jobs: {response.status_code} - {response.text}")
            return None


class HarmeeScraper:

    def __init__(self):
        self.url = "https://harmeejobs.com/jobs/"


    def job_detail(self, link):
        #job_description
        print(link)
        response = requests.get(link)
        page = bs4.BeautifulSoup(response.content, "html.parser")
        job_title = page.select_one(".job-overview > ul:nth-child(1) > li:nth-child(5) > div:nth-child(2) > span:nth-child(2)").text.strip() 
        company = page.select_one(".content > h4:nth-child(1) > a:nth-child(1) > strong:nth-child(1)").text.strip() if page.select_one(".content > h4:nth-child(1) > a:nth-child(1) > strong:nth-child(1)") else page.select_one(".content > h4:nth-child(1) > strong:nth-child(1)").text.strip() if page.select_one(".content > h4:nth-child(1) > strong:nth-child(1)") else ""
        location = page.select_one("#job-details > div > div > ul > li:nth-child(4) > div > span").text.strip()
        date_posted = page.select_one(".job-overview > ul:nth-child(1) > li:nth-child(2) > div:nth-child(2) > span:nth-child(2) > time:nth-child(1)").text.strip()
        expiration_date = page.select_one(".job-overview > ul:nth-child(1) > li:nth-child(3) > div:nth-child(2) > span:nth-child(2)").text.strip()
        job_type = page.select_one("span.job-type, div.eleven:nth-child(1) > h1:nth-child(2) > span:nth-child(1)")
        job_type = job_type.text.strip() if job_type and job_type.text.strip() != "NEW" else ""

        salary_element = page.select_one(".job-overview > ul:nth-child(1) > li:nth-child(6) > div:nth-child(2) > span:nth-child(2)")
        salary = salary_element.text.strip() if salary_element else ""

        apply_link_element = page.select_one(".company-info-apply-btn > a:nth-child(1)")
        apply_link = apply_link_element['href'] if apply_link_element else ""
        job_description = page.select_one(".job_description")


        return {
            "source": self.url,
            "job_link": link,
            "job_title": job_title,
            "company": company,
            "apply_link": apply_link,
            "job_type": job_type,
            "location": location,
            "date_posted": date_posted,
            "expiration_date": expiration_date,
            "salary": salary,
            # "job_description": job_description
        }

    def job_post(self):
        job_post_data = []
        response = requests.get(self.url)
        page = bs4.BeautifulSoup(response.content, "html.parser")
        links = page.find_all("a", class_="workscout-grid-job-link-handler")
        for link in links:
            job_post_data.append(self.job_detail(str(link["href"])))
        return job_post_data

    def clean_unicode_escape(content):
        if isinstance(content, str):
            cleaned_content = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), content)
            return cleaned_content
        elif isinstance(content, list):
            return [clean_unicode_escape(item) for item in content]
        elif isinstance(content, dict):
            return {key: clean_unicode_escape(value) for key, value in content.items()}
        return content

    def group_content(job_description_element):

        grouped_content = []
        current_heading = None
        content_list = []

        for child in job_description_element.children:
            if child.name in ['h2', 'h3']:
                if current_heading:
                    grouped_content.append({
                        'heading': current_heading.text.strip(),
                        'content': content_list
                    })
                current_heading = child
                content_list = []
            elif child.name == 'p':
                content_list.append(child.text.strip())
            elif child.name == 'ul':
                for li in child.find_all('li'):
                    content_list.append(li.text.strip())

        # Add the last group if any
        if current_heading:
            grouped_content.append({
                'heading': current_heading.text.strip(),
                'content': content_list
            })

        return grouped_content


class TelegramPoster:
# Replace with your bot's token
    def __init__(self):
        self.TOKEN = getenv("TELEGRAM_BOT_TOKEN")
        self.CHANNEL_ID = getenv("TELEGRAM_CHANNEL_ID")
        self.PRIVATE_CHANNEL_ID = getenv("TEST_TELEGRAM_CHANNEL_ID")
    async def post_vacancies(self, about_post, jobs):
        bot = Bot(token=self.TOKEN)
        message_content = MessageContent()
        # for job in jobs:
        message = message_content.format_telegram_message(about_post, jobs)
        await bot.send_message(chat_id=self.PRIVATE_CHANNEL_ID, text=message, parse_mode="HTML")

    async def post_to_channel(self, job):
        try:
            message = None
            # if job["source"] == "https://hahu.jobs/jobs":
            if job["data"]["source"] == "hahu":
                message_content = MessageContent()
                message = message_content.hahu_message_content(job["data"])
            else:
                message_content = MessageContent()
                message = message_content.harmee_message_content(job["data"])
            bot = Bot(token=self.TOKEN)
            if job["data"]["source"] == "hahu":
                if job["data"]["application_method"] == "url":
                    await bot.send_message(chat_id=self.CHANNEL_ID, text=message, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("Read Full Detail", url=f"https://hahu.jobs/jobs/{job['data']['id']}")]
                            [InlineKeyboardButton("Apply Now", url=job["data"]["application_link"])]
                        ]
                        )
                    )
                else:
                    await bot.send_message(chat_id=self.CHANNEL_ID, text=message, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Read Full Detail", url=f"https://hahu.jobs/jobs/{job['data']['id']}")]]))
            else:
                await bot.send_message(chat_id=self.CHANNEL_ID, text=message, parse_mode="HTML")
            logger.info(f"Message posted to {self.CHANNEL_ID}: {message}")
        except TelegramError as e:
            logger.error(f"Failed to post message to {self.CHANNEL_ID}: {e}")


@app.get("/api")
def health_check():
    return "alive"

@app.post("/api/daily-jobs-vacancies")   
@app.get("/api/daily-jobs-vacancies")
async def server():
    tg_poster = TelegramPoster()
    links = daily_jobs_links()
    for link in links:
        about_post, job = job_detail(link) 
        await tg_poster.post_vacancies(about_post, job)


@app.post("/api/task")
@app.get("/api/task")
async def main():
    telegram_poster = TelegramPoster()
    harmee = HarmeeScraper()
    hahu = HahuJobsQuery()
    harmee_jobs = harmee.job_post()
    hahu_jobs = hahu.get_jobs()
    jobs = harmee_jobs[:10] + hahu_jobs
    # jobs = hahu_jobs
    print(json.dumps(jobs, indent=4))
    for job in jobs:
        await telegram_poster.post_to_channel({'data':job})

# uncomment when testing locally

# if __name__=="__main__":
#     uvicorn.run("scraper:app", host="localhost", port=8000, reload=True)