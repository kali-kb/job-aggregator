from fastapi import FastAPI
import uvicorn
from telegram import Bot
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


class HahuScraper:

    def __init__(self):
        self.url = "https://hahu.jobs/jobs"

    def get_job_content(self, job_link):
        print(job_link)
        response = requests.get(job_link)
        page = bs4.BeautifulSoup(response.content, "html.parser")
        job_title = page.select_one(".font-extrabold").text.strip()
        job_type = page.select_one("div.xl\:text-lg > div:nth-child(1)").text.strip()
        company = page.select_one("p.text-secondary-6").text.strip()
        location = page.select_one(".grid > div:nth-child(2) > p:nth-child(2)").text.strip()
        experience = page.select_one("div.gap-2:nth-child(3) > p:nth-child(2)").text.strip()
        number_of_positions = page.select_one("div.items-center:nth-child(4) > p:nth-child(2)").text.strip()
        job_sector = page.select_one("div.gap-2:nth-child(1) > p:nth-child(2)").text.strip()
        # expiration_date = page.select_one("div.items-center:nth-child(5) > p:nth-child(4)").text.strip()
        # apply_link = page.select(".mb-20")
        # tree = etree.HTML(str(page))
        job = {
            "source": self.url,
            "job_title": job_title,
            "job_type": job_type,
            "job_sector": job_sector,
            "company": company,
            "location": location,
            "experience": experience,
            # "expiration_date": expiration_date,
            "number_of_positions": number_of_positions,
            "job_link": job_link
        }
        return job


    def get_jobs(self):
        job_links = []
        jobs = []
        response = requests.get(self.url)
        soup = bs4.BeautifulSoup(response.content, "html.parser")
        for link in soup.find_all('a', href=lambda href: href and href.startswith('https://app.hahu.jobs/app/jobs/')):
            pattern = r"https://app\.hahu\.jobs/app/jobs/([a-f0-9]+)\?save=true"
            match = re.search(pattern, link['href'])
            if match:
                path = self.url
                job_id = str(match.group(1))
                job_path = f"{path}/{job_id}"
                jobs.append(self.get_job_content(job_path))
                # job_links.append(job_path)
        return jobs

 
# hs = HahuScraper()
# print(hs.get_jobs())
# hs.get_job_content("https://hahu.jobs/jobs/ZX57o7cmPELKwZC")

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

        # return group_content(job_description)
        # return job_title, company, apply_link, job_type, location, date_posted, expiration_date
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


hs = HarmeeScraper()
# print(json.dumps(hs.job_post(), indent=4))
# pprint.pprint(hs.job_post())
# pprint.pprint(job_detail("https://harmeejobs.com/job/regional-sales-manager-2/"))
# print(json.dumps(job_detail("https://harmeejobs.com/job/regional-sales-manager-2/"), indent=4))
# print(json.dumps(clean_unicode_escape(job_detail("https://harmeejobs.com/job/regional-sales-manager-2/")), indent=4))
class MessageContent:

    def hahu_message_content(self, job):
        message = (
            f"<b>Company/Organization</b>: {job['company']}\n"
            f"\n"
            f"<b>Job Title</b>: {job['job_title']}\n"
            f"\n"
            f"<b>Location</b>: {job['location']}\n"
            f"\n"
            f"<b>Job Type</b>: {job['job_type']}\n"
            f"\n"
            f"<b>Job Experience Required</b>: {job['experience']}\n"
            f"\n"
            f"<b>Available Position</b>: {job['number_of_positions']}\n"
            f"\n"
            f"<b>Job Sector</b>: #{job['job_sector'].lower()}\n"
            f"\n"
            # f"<b>Expiration Date</b>: {self.job['expiration_date']}\n"
            f"---------------------------------\n"
            f"\n"
            f"<b>Full Job Description</b>: 👉 {job['job_link']}\n"
            f"\n\n\n"
            f"@arki_jobs\n"
        )
        return message

    def harmee_message_content(self, job):
        message = (
            f"<b>Company/Organization</b>: {job['company']}\n"
            f"\n"
            f"<b>Job Title</b>: {job['job_title']}\n"
            f"\n"
            f"<b>Location</b>: {job['location']}\n"
            f"\n"
        )
        if job['job_type'] != "":
            message += f"\n<b>Job Type</b>: {job['job_type']}\n"

        other_details = (
            f"\n"
            f"<b>Date Posted</b>: {job['date_posted']}\n"
            f"\n"
            f"<b>Expiration Date</b>: {job['expiration_date']}"
            f"\n"
            f"--------------------------\n"
            f"\n"
            f"\n\n\n"
            f"<b>Full job information</b>: 👉 {job['job_link']}"
            f"\n\n"
            f"@arki_jobs\n"
        )

        if job['salary']!= "":
            message += f"\n<b>Salary</b>: {job['salary']}\n"

        if job['apply_link'] != "":
            message += f"\n<b>Apply Link</b>: <a href='{job['apply_link']}'>Click here to apply</a>\n"

        message += other_details

        return message    


class TelegramPoster:
# Replace with your bot's token
    def __init__(self):
        self.TOKEN = getenv("TELEGRAM_BOT_TOKEN")
        self.CHANNEL_ID = getenv("TELEGRAM_CHANNEL_ID")

    async def post_to_channel(self, job):
        try:
            message = None
            if job["source"] == "https://hahu.jobs/jobs":
                message_content = MessageContent()
                message = message_content.hahu_message_content(job)
            else:
                message_content = MessageContent()
                message = message_content.harmee_message_content(job)
            bot = Bot(token=self.TOKEN)
            await bot.send_message(chat_id=self.CHANNEL_ID, text=message, parse_mode=ParseMode.HTML)
            logger.info(f"Message posted to {self.CHANNEL_ID}: {message}")
        except TelegramError as e:
            logger.error(f"Failed to post message to {self.CHANNEL_ID}: {e}")


@app.get("/api")
async def server():
    return "Hi"

@app.post("/api/task")
@app.get("/api/task")
async def main():
    telegram_poster = TelegramPoster()
    harmee = HarmeeScraper()
    hahu = HahuScraper()
    harmee_jobs = harmee.job_post()
    hahu_jobs = hahu.get_jobs()
    jobs = harmee_jobs + hahu_jobs
    jobs = jobs[::-1]
    print(json.dumps(jobs, indent=4))
    for job in jobs:
        await telegram_poster.post_to_channel(job)

# uncomment when testing locally
# if __name__=="__main__":
#     uvicorn.run("scraper:app", host="localhost", port=8000, reload=True)