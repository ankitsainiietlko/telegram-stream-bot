import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ====== CONFIG ======
API_TOKEN = "8104540738:AAF2-c1MidpeulwhqP4-63y9OqYYLf_-v0Q"  # from BotFather
STREAMTAPE_USER = "dadfda8ad99b4581e0a4"
STREAMTAPE_KEY = "DWLM618ey0ckpzK"
# ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a video file and I will give you a streaming link.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.video
    file_name = file.file_name
    file_id = file.file_id

    # Step 1: Get file path from Telegram
    file_info = await context.bot.get_file(file_id)
    file_path = file_info.file_path
    file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"

    await update.message.reply_text("Downloading your file...")

    # Step 2: Download file in chunks
    local_path = file_name
    with requests.get(file_url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)

    await update.message.reply_text("Uploading to Streamtape...")

    # Step 3: Upload to Streamtape
    upload_url = f"https://api.streamtape.com/file/ul?login={STREAMTAPE_USER}&key={STREAMTAPE_KEY}"
    with open(local_path, 'rb') as f:
        response = requests.post(upload_url, files={"file1": f})
    result = response.json()

    if result.get("status") == 200:
        streaming_link = result["result"]["url"]
        await update.message.reply_text(f"Here’s your streaming link:\n{streaming_link}")
    else:
        await update.message.reply_text("Upload failed. Please try again.")

    os.remove(local_path)

def main():
    app = ApplicationBuilder().token(API_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO, handle_file))

    app.run_polling()

if __name__ == "__main__":
    main()
