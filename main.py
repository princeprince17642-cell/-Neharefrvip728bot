import json
import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update, MessageEntity
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, CommandHandler, MessageHandler, filters, ContextTypes

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
ADMIN_ID = 8343576029  # तेरी एडमिन आईडी
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
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("तू इस कमांड को इस्तेमाल नहीं कर सकता!")
        return

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

async def broadcast_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("तू इस कमांड को इस्तेमाल नहीं कर सकता!")
        return

    reply_msg = update.message.reply_to_message
    if not reply_msg or not reply_msg.voice:
        await update.message.reply_text("कृपया किसी वॉइस नोट को रिप्लाई करके यह कमांड भेजें: /sendvoice")
        return

    voice_file_id = reply_msg.voice.file_id

    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
        
        success = 0
        for user_id in users:
            try:
                await context.bot.send_voice(chat_id=user_id, voice=voice_file_id)
                success += 1
            except Exception as e:
                print(f"Failed to send voice to {user_id}: {e}")
        
        await update.message.reply_text(f"वॉइस ब्रॉडकास्ट पूरा हुआ! {success} लोगों को वॉइस नोट भेज दिया गया है।")
    else:
        await update.message.reply_text("कोई यूजर डेटाबेस नहीं मिला!")

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    # अगर मैसेज एडमिन (तू) की तरफ से है
    if user.id == ADMIN_ID:
        # चेक कर कि क्या एडमिन ने किसी मैसेज पर रिप्लाई किया है
        if message.reply_to_message:
            replied_text = message.reply_to_message.text or message.reply_to_message.caption
            if replied_text and "User ID:" in replied_text:
                try:
                    # फॉरवर्ड किए गए मैसेज से यूजर की असली आईडी निकालना
                    line = [l for l in replied_text.split('\n') if "User ID:" in l][0]
                    target_user_id = int(line.split(":")[1].strip())
                    
                    # यूजर को एडमिन का जवाब भेजना (चाहे टेक्स्ट हो या वॉइस)
                    if message.voice:
                        await context.bot.send_voice(chat_id=target_user_id, voice=message.voice.file_id)
                    elif message.text:
                        await context.bot.send_message(chat_id=target_user_id, text=message.text)
                    
                    await message.reply_text("✅ मैसेज यूजर को भेज दिया गया है!")
                except Exception as e:
                    await message.reply_text(f"❌ भेजने में एरर आया: {e}")
        return

    # अगर मैसेज किसी आम यूजर की तरफ से है (जो एडमिन नहीं है)
    else:
        save_user(user.id) # यूजर की आईडी सेव कर लो ताकि ब्रॉडकास्ट में काम आए
        
        # यूजर का नाम और यूजरनेम निकालना
        user_name = user.full_name
        username = f"@{user.username}" if user.username else "कोई यूजरनेम नहीं"
        
        # एडमिन (तेरे पास) मैसेज फॉरवर्ड करना
        forward_header = f"📩 नया मैसेज आया है!\n👤 नाम: {user_name}\n🔗 यूजरनेम: {username}\n🆔 User ID: {user.id}\n-------------------\n"
        
        try:
            if message.text:
                await context.bot.send_message(chat_id=ADMIN_ID, text=forward_header + message.text)
            elif message.voice:
                await context.bot.send_message(chat_id=ADMIN_ID, text=forward_header + "[नीचे यूजर का वॉइस नोट है]")
                await context.bot.send_voice(chat_id=ADMIN_ID, voice=message.voice.file_id)
            elif message.photo:
                await context.bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=forward_header + (message.caption or ""))
            else:
                await context.bot.send_message(chat_id=ADMIN_ID, text=forward_header + "[यूजर ने मीडिया/डॉक्यूमेंट भेजा है]")
        except Exception as e:
            print(f"Error forwarding to admin: {e}")

if __name__ == '__main__':
    keep_alive()
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("sendvoice", broadcast_voice))
    
    # बाकी सारे टेक्स्ट, वॉइस या फोटो वाले मैसेजेस को हैंडल करने के लिए
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_messages))

    print("Bot start ho gaya hai...")
    app.run_polling(allowed_updates=["chat_join_request", "message"])