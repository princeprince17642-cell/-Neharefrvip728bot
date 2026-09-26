import json
import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update, MessageEntity
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, CommandHandler, ContextTypes

# --- FLASK SERVER ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Alive and Running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

BOT_TOKEN = "8451986992:AAGPq44dVUbhSq4Cv9zX2WDAaUsBlMxECbQ"
USERS_FILE = "users.json"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def save_user(user_id):
    users = []
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
        except:
            users = []
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    user_id = request.from_user.id
    
    save_user(user_id)

    text = "VIP CHANNEL ENTRY\n\nhttps://t.me/+aIdVyZX2GYthYmE1\nhttps://t.me/+aIdVyZX2GYthYmE1\nhttps://t.me/+aIdVyZX2GYthYmE1\nhttps://t.me/+aIdVyZX2GYthYmE1"
    emoji_id = "5368324170671202286"
    
    entities = [
        MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=emoji_id),
        MessageEntity(type=MessageEntity.BOLD, offset=2, length=17),
        MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=19, length=2, custom_emoji_id=emoji_id),
    ]

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"👍{text[:17]}👍\n\n{text[19:]}",
            entities=entities,
            disable_web_page_preview=True
        )
        print(f"Message successfully sent to {user_id}")
    except Exception as e:
        print(f"Error sending message: {e}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = " ".join(context.args)
    if not message_text:
        await update.message.reply_text("मैसेज लिखें, जैसे: /broadcast आपका संदेश")
        return

    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
        
        success = 0
        for user_id in users:
            try:
                await context.bot.send_message(chat_id=user_id, text=message_text)
                success += 1
            except Exception as e:
                print(f"Failed to send to {user_id}: {e}")
        
        await update.message.reply_text(f"ब्रॉडकास्ट पूरा हुआ! {success} लोगों को मैसेज भेज दिया गया है।")
    else:
        await update.message.reply_text("कोई यूजर डेटाबेस नहीं मिला!")

if __name__ == '__main__':
    keep_alive()
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    app.add_handler(CommandHandler("broadcast", broadcast))

    print("Bot start ho gaya hai...")
    app.run_polling(allowed_updates=["chat_join_request", "message"])