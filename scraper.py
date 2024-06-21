import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from tqdm import tqdm
from datetime import datetime
import json
import numpy as np


def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def scrape_jobs(config):
    df = pd.DataFrame()
    output_dir = config['paths']['scraped_jobs_dir']
    parsed_jobs_file = config['paths']['parsed_jobs_file']
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    prev_len = 0
    parsed_jobs = set()
    if os.path.isfile(parsed_jobs_file):
        with open(parsed_jobs_file, 'r') as f:
            parsed_jobs = set(line.strip() for line in f)

    target_url = config['job_search']['url']


    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


    new_jobids_to_parse = set()
    o = {}
    k = []

    for page_num in np.arange(0, config["job_search"]["max_pages"], step=10):
        res = requests.get(target_url.format(page_num))
        print(target_url.format(page_num))
        soup = BeautifulSoup(res.text, "html.parser")
        alljobs_on_this_page = soup.find_all("li")
        time.sleep(2)

        for x in range(0, len(alljobs_on_this_page)):
            try:
                jobid = (
                    alljobs_on_this_page[x]
                    .find("div", {"class": "base-search-card"})
                    .get("data-entity-urn")
                    .split(":")[3]
                )
                new_jobids_to_parse.add(jobid)
            except:
                pass

        if len(new_jobids_to_parse) > prev_len:
            prev_len = len(new_jobids_to_parse)
        else:
            break

    new_jobids_to_parse = [
        item for item in new_jobids_to_parse if item not in parsed_jobs
    ]

    target_url = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}"
    for j in tqdm(range(0, len(new_jobids_to_parse)), "getting jobs info"):
        time.sleep(2)
        resp = requests.get(target_url.format(new_jobids_to_parse[j]))
        soup = BeautifulSoup(resp.text, "html.parser")
        o["url"] = target_url.format(new_jobids_to_parse[j])
        o["jobid"] = new_jobids_to_parse[j]
        try:
            o["company"] = (
                soup.find("div", {"class": "top-card-layout__card"})
                .find("a")
                .find("img")
                .get("alt")
            )
        except:
            o["company"] = None

        try:
            o["job_title"] = (
                soup.find("div", {"class": "top-card-layout__entity-info"})
                .find("a")
                .text.strip()
            )
        except:
            o["job_title"] = None

        try:
            o["level"] = (
                soup.find("ul", {"class": "description__job-criteria-list"})
                .find("li")
                .text.replace("Seniority level", "")
                .strip()
            )
        except:
            o["level"] = None

        try:
            desc_items = [
                item.text.replace("\n", " ")
                .replace("\t", " ")
                .strip()
                .replace("   ", " ")
                .replace("   ", " ")
                .replace("   ", " ")
                .replace("  ", " ")
                .replace("  ", " ")
                .replace("  ", " ")
                .strip()
                for item in soup
            ]
            desc_items = [item for item in desc_items if len(item) > 0]
            o["description"] = "\n".join(desc_items)
        except:
            o["description"] = None

        k.append(o)
        o = {}
    # if len(k) > 0:
    df = pd.DataFrame(k)
    datetime_str = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    df.to_csv(
        f"{output_dir}/linkedinjobs_{datetime_str}.csv", index=False, encoding="utf-8"
    )

    with open(parsed_jobs_file, "a") as f:
        for item in new_jobids_to_parse:
            f.write(f"{item}\n")
    return df


if __name__ == "__main__":
    config = load_config()
    scrape_jobs(config)
