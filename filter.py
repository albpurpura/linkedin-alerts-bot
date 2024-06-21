import logging
import os
import requests
import json
import pandas as pd
from tqdm import tqdm


def load_config():
    with open("config.json", "r") as f:
        return json.load(f)


def load_latest_jobs(config):
    scraped_jobs_dir = config["paths"]["scraped_jobs_dir"]
    fpaths = []
    for fname in os.listdir(scraped_jobs_dir):
        if fname.endswith(".csv"):
            fpaths.append(os.path.join(scraped_jobs_dir, fname))
    last_fpath = sorted(fpaths)[-1]
    try:
        df = pd.read_csv(last_fpath)
    except Exception as e:
        df = pd.DataFrame()

    candidates = []
    for idx, row in df.iterrows():
        company = row.company
        job_title = row.job_title
        level = row.level
        desc = row.description

        data = {
            "company": company,
            "level": level,
            "title": job_title,
            "description": desc,
            "jobid": row.jobid,
            "url": row.url,
        }
        candidates.append(data)
    return candidates


def ask_ai_model(prompt, config):
    headers = {"Content-Type": "application/json"}
    data = {
        "model": config["ai_model"]["model_name"],
        "prompt": prompt,
        "stream": False,
    }
    response = requests.post(config["ai_model"]["api_url"], headers=headers, json=data)
    return json.loads(response.text)["response"]


def load_resume(config):
    with open(config["paths"]["resume_file"]) as f:
        return f.read()


def messages_generator(config):
    cover_letters_dir = config["paths"]["cover_letters_dir"]
    if not os.path.exists(cover_letters_dir):
        os.makedirs(cover_letters_dir)

    resume = load_resume(config)
    candidates = load_latest_jobs(config)

    for c in tqdm(candidates, "filtering candidates"):
        if any(
            title in c["title"].lower()
            for title in config["filters"]["excluded_title_kws"]
        ):
            continue

        prompt = f'Job information: {json.dumps(c)}\n\n{config["filters"]["filter1"]}.'
        resp = ask_ai_model(prompt, config)
        if "YES" in resp:
            prompt = f'Job information: {json.dumps(c)}\n\n{config["filters"]["filter2"]}.'
            resp = ask_ai_model(prompt, config)
            if "YES" in resp:
                logging.info("FOUND a good job match!")

                cover_letter = ask_ai_model(
                    f"Resume: {resume}\n\nJob info: {json.dumps(c)}\n\n{config['cover_letter']['prompt']}",
                    config,
                )
                fpath = f'{cover_letters_dir}/{c["job_id"]}_cover_letter.txt'
                with open(fpath, "w") as f:
                    f.write(cover_letter)

                yield json.dumps(
                    {
                        "title": c["title"],
                        "url": c["url"],
                        "company": c["company"],
                    }
                )


if __name__ == "__main__":
    config = load_config()
    for item in messages_generator(config):
        print(item)
        print("\n\n")
