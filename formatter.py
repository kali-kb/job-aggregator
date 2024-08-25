from datetime import datetime

class MessageContent:

    def format_telegram_message(self, about_post, jobs):
        message = f"{about_post['company']}\n{about_post['date']}\n\n"
        for job in jobs:
            message += f"<b>{job['title']}</b>\n\n"
            for detail in job['details']:
                message += f"{detail}\n"
            message += "\n" + "-" * 40 + "\n\n"
        message += f"full job description: {about_post['vacancy_link']}"
        message += f"\n#banking_jobs\n\n@arki_jobs"
        return message

    def hahu_message_content(self, job):
        
        date_obj = datetime.fromisoformat(job['created_at'])
        expiration_date = date_obj.strftime("%B %d, %Y")
        
        message = (
            f"<b>Company/Organization</b>: {job['entity']['name']}\n"
            f"\n"
            f"<b>Job Title</b>: {job['title']}\n"
            f"\n"
            f"<b>Location</b>: {', '.join(city['city']['name'] for city in job['job_cities'])}\n"
            f"\n"
            f"<b>Job Type</b>: {job['type'].capitalize().replace('_',' ')}\n"
            f"\n"
            f"<b>Required Gender:</b> {'Both' if job['gender_priority'] == 'neutral' else job['gender_priority'].capitalize().replace('_', ' ')}\n"
            f"\n"
            f"<b>Job Experience Required</b>: {job['years_of_experience']}\n"
            # f"\n"
            # f"<b>Available Positions</b>: {job['number_of_applicants']}\n"
            f"\n"
            f"<b>Job Sector</b>: #{job['sub_sector']['name'].lower().replace(' ', '_')}\n"
            f"\n"
            f"<b>Job Summary: </b> {job['summary']}"
            f"\n"
            f"<b>Expiration/Deadline Date</b>: {expiration_date}\n"
            f"\n"
            f"<b>How to Apply:</b> {job['how_to_apply']}\n"
            f"---------------------------------\n"
            f"\n"
            f"\n\n"
            # f"<b>Full Job Description</b>: {job['description']}\n"
        )

        if job["application_method"] == "email":
            message += f"Apply Link: <a href='mailto:{job['application_email']}'>{job['application_email']}</a>\n"

        other_message = (
            f"\n\n#zero_experience\n#fresh_graduate\n\n"
            f"\n\n\n"
            f"@arki_jobs\n"
        )   

        message += other_message

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
            message += f"\n<b>To Apply</b>: <a href='{job['apply_link']}'>Click here to apply</a>\n"

        message += other_details

        return message    
