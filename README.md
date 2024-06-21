# Job Search Assistant Bot

This repository contains a Telegram bot that automates job searching, filtering, and notification processes. 
It scrapes job listings, filters them based on user-defined criteria, and sends notifications about relevant positions.

## Features

- Scrapes job listings from a specified job search website
- Filters jobs based on customizable criteria using an AI model
- Generates cover letter drafts for matching job positions
- Sends job notifications via Telegram bot
- Configurable settings through a JSON file

## Setup

1. Clone the repository
2. Install dependencies
3. Set up your Telegram bot:
- Create a new bot using BotFather on Telegram
- Note down the bot token

4. Configure the `config.json` file:
- Update the `telegram.token` with your bot token
- Modify the `job_search` parameters to match your desired job search criteria
- Adjust the `filters` and other settings as needed

5. Prepare your resume:
- Place your resume text in a file named `resume.txt` in the project directory

## Usage

1. Start the bot: `pythonh main.py`
2. Interact with the bot on Telegram:
- Send `/start` to get started
- Use `/search` to initiate a job search
- Use `/stop` to stop automatic updates

## File Structure

- `main.py`: The main script that runs the Telegram bot
- `scraper.py`: Contains the job scraping functionality
- `filter.py`: Handles job filtering and cover letter generation
- `config.json`: Configuration file for all settings
- `resume.txt`: Your resume in text format
- `scraped_jobs/`: Directory where scraped job data is stored
- `cover_letters/`: Directory where generated cover letters are saved

## Customization

You can customize the bot's behavior by modifying the `config.json` file. This includes:

- Job search parameters (URL, keywords, location)
- Filtering criteria and prompts
- AI model settings
- File paths and directory names

## Security Note

This bot uses a local AI model for text generation. Ensure that you have the necessary permissions and comply with the terms of service of any external APIs or services you might integrate.

## Disclaimer

This bot is for educational purposes only. Make sure to comply with the terms of service of any job boards or websites you scrape. Be respectful of rate limits and robots.txt files.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
