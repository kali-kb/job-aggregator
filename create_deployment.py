from prefect import flow

if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/kali-kb/job-aggregator.git",
        entrypoint="scraper.py:main",
    ).deploy(
        name="my-first-deployment",
        work_pool_name="my-managed-pool",
        cron="0 1 * * *",
    )