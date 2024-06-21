import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from scraper import scrape_jobs
from filter import messages_generator, load_config

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

config = load_config()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    instructions = "Say '/search' to start the search.\nSay '/stop' to stop the search."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hello, {update.effective_chat.first_name}.\n{instructions}")

async def callback_search(context):
    update = context.job.data["update"]
    config = load_config()  # Reload config in case of changes

    logging.info("Scraping jobs")
    df = scrape_jobs(config)
    await update.message.reply_text(f"{len(df)} new job postings found")
    
    await update.message.reply_text("Analyzing job postings...")
    logging.info("Filtering jobs")
    messages = messages_generator(config)
    
    found_one = False
    for m in messages:
        found_one = True
        logging.info(m)
        await update.message.reply_text(m)
    
    if not found_one:
        await update.message.reply_text("No new relevant jobs found for you!")
    else:
        await update.message.reply_text("No more job updates for now!")

def start_search(update, context):
    chat_id = update.message.chat_id
    context.job_queue.run_repeating(
        callback_search,
        first=1,
        interval=3600,
        data={"chat_id": chat_id, "update": update},
        name=str(chat_id),
    )
    return context.bot.send_message(chat_id=chat_id, text="Job search agent started, you will receive an update every hour.")

def stop_notify(update, context):
    chat_id = update.message.chat_id
    job = context.job_queue.get_jobs_by_name(str(chat_id))
    job[0].schedule_removal()
    return context.bot.send_message(chat_id=chat_id, text="Stopping automatic messages!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logging.info(f"Received message from {user_id}")
    if user_id in config['telegram']['allowed_users']:
        instructions = "Say '/search' to start the search agent.\nSay '/stop' to stop the search agent."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=instructions)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I'm not authorized to talk to you.")

if __name__ == "__main__":
    application = ApplicationBuilder().token(config['telegram']['token']).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", start_search))
    application.add_handler(CommandHandler("stop", stop_notify))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

    try:
        application.run_polling()
    except Exception as e:
        logging.error(f"Error: {e}")
