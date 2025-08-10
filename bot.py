import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Read secrets from environment variables (Railway Variables)
API_TOKEN = os.environ.get("8104540738:AAF2-c1MidpeulwhqP4-63y9OqYYLf_-v0Q")           # Telegram Bot Token from BotFather
STREAMTAPE_USER = os.environ.get("dadfda8ad99b4581e0a4")  # Streamtape Username
STREAMTAPE_KEY = os.environ.get("DWLM618ey0ckpzK")    # Streamtape API Key

# =========================
# Start Command
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a video or file and I will give you a streaming link.")

# =========================
# Handle File Upload
# =========================
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.video
    file_name = file.file_name
    file_id = file.file_id

    # Step 1: Get Telegram file path
    file_info = await context.bot.get_file(file_id)
    file_path = file_info.file_path
    file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"

    await update.message.reply_text("📥 Downloading your file...")

    # Step 2: Download file in chunks
    local_path = file_name
    with requests.get(file_url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)

    await update.message.reply_text("☁️ Uploading to Streamtape...")

    # Step 3: Upload to Streamtape
    upload_url = f"https://api.streamtape.com/file/ul?login={STREAMTAPE_USER}&key={STREAMTAPE_KEY}"
    with open(local_path, 'rb') as f:
        response = requests.post(upload_url, files={"file1": f})
    result = response.json()

    if result.get("status") == 200:
        streaming_link = result["result"]["url"]
        await update.message.reply_text(f"✅ Here’s your streaming link:\n{streaming_link}")
    else:
        await update.message.reply_text("❌ Upload failed. Please try again.")

    # Step 4: Remove local file to save space
    os.remove(local_path)

# =========================
# Main Function
# =========================
if __name__ == "__main__":
    app = ApplicationBuilder().token(API_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO, handle_file))

    # Webhook settings for Railway
    PORT = int(os.environ.get("PORT", 8080))
    APP_URL = f"https://{os.environ.get('RAILWAY_STATIC_URL')}/{API_TOKEN}"

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=API_TOKEN,
        webhook_url=APP_URL
    )
