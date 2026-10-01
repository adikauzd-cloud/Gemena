import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ----------------- ማስተካከያዎች (CONFIG) -----------------
BOT_TOKEN = "8301245356:AAFrrgMP-RG_JHGyp49-_WCk_PyIdJAT17s"
ADMIN_CHAT_ID = 7030641737
# -------------------------------------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Render ለሚፈልገው ፖርት Dummy HTTP Server ማዘጋጀት
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Gemena Bot is running fine!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logging.info(f"Dummy Web Server running on port {port} for Render")
    server.serve_forever()

def get_admin_reply_markup(user_id: int):
    keyboard = [
        [InlineKeyboardButton("💬 መልስ (Reply)", callback_data=f"reply_to_{user_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"ሰላም {user.first_name}፣ እንኳን ወደ **ገመና** በደህና መጡ! 🤍\n\n"
        "ብቸኝነት ተሰምቶዎታል? ጭንቀትዎን ወይም ሃሳብዎን ማካፈል የሚፈልጉት ታማኝ አድማጭ ይፈልጋሉ?\n\n"
        "እዚህ ያወሩት ነገር ሁሉ ፍጹም ምስጢር ነው፤ ማንም አይፈርድብዎትም።\n"
        "እንዴት ማውራት ይፈልጋሉ?"
    )

    keyboard = [
        [
            InlineKeyboardButton("✍️ በጽሑፍ (Text)", callback_data="type_text"),
            InlineKeyboardButton("📞 በድምፅ (Voice)", callback_data="type_voice"),
        ],
        [InlineKeyboardButton("ℹ️ ስለ ገመና እና ምስጢራዊነት", callback_data="about_service")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("reply_to_"):
        target_id = int(data.split("_")[2])
        context.user_data["replying_to_user_id"] = target_id
        await query.message.reply_text(
            f"✍️ **ለተጠቃሚው (ID: `{target_id}`) የሚላከውን መልእክት አሁን ይጻፉ/ይላኩ፦**\n"
            "*(ለመሰረዝ /cancel ይበሉ)*",
            parse_mode="Markdown"
        )
        return

    if data in ["type_text", "type_voice"]:
        comm_type = "በጽሑፍ (Text)" if data == "type_text" else "በድምፅ (Voice Call)"
        context.user_data["comm_type"] = comm_type

        duration_text = (
            f"የመረጡት መንገድ፦ **{comm_type}**\n\n"
            "ስንት ደቂቃ መቆየት ይፈልጋሉ? (አሁን በነጻ መጀመር ይችላሉ)"
        )
        keyboard = [
            [
                InlineKeyboardButton("⏱ 20 ደቂቃ (ነጻ ሙከራ)", callback_data="dur_20"),
                InlineKeyboardButton("⏱ 40 ደቂቃ", callback_data="dur_40"),
            ],
            [InlineKeyboardButton("🔙 ወደ ኋላ", callback_data="back_start")],
        ]
        await query.edit_message_text(duration_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data in ["dur_20", "dur_40"]:
        duration = "20 ደቂቃ" if data == "dur_20" else "40 ደቂቃ"
        comm_type = context.user_data.get("comm_type", "በጽሑፍ")
        user = query.from_user

        confirm_text = (
            "✅ **ምርጫዎ ተመዝግቧል!**\n\n"
            f"• መንገድ፦ {comm_type}\n"
            f"• ቆይታ፦ {duration}\n\n"
            "አድማጭዎ ዝግጁ ነው። አሁኑኑ ልብዎ የያዘውን ማውራት መጀመር ይችላሉ። "
            "የሚጽፉት መልእክት በቀጥታ ለአድማጭዎ ይደርሳል።"
        )
        await query.edit_message_text(confirm_text, parse_mode="Markdown")

        admin_alert = (
            f"🔔 **አዲስ ደንበኛ ተገናኝቷል!**\n\n"
            f"• ስም፦ {user.full_name}\n"
            f"• Username: @{user.username if user.username else 'የለውም'}\n"
            f"• ID: `{user.id}`\n"
            f"• መንገድ፦ {comm_type}\n"
            f"• ቆይታ፦ {duration}"
        )
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_alert,
            reply_markup=get_admin_reply_markup(user.id),
            parse_mode="Markdown"
        )

    elif data == "about_service":
        about_text = (
            "🛡️ **ገመና — የመደመጥ እና የጓደኝነት አገልግሎት**\n\n"
            "• **ምስጢራዊነት፦** የእርስዎ ማንነት እና የሚያወሩት ጉዳይ 100% ምስጢር ነው።\n"
            "• **ያለፍርድ፦** ምንም ዓይነት ስህተት ወይም የግል ታሪክ ቢሆን ያለ ምንም ፍርድ ይደመጣሉ።\n"
            "• **ማስታወሻ፦** ይህ አገልግሎት የጓደኝነት እና የመደመጥ እንጂ ሙያዊ የሆስፒታል/ሳይካትሪ ሕክምና አይደለም።\n\n"
            "ክፍያን በተመለከተ፦ የመጀመሪያውን ክፍለ-ጊዜ በነጻ ወይም በፈቃደኝነት መሞከር ይችላሉ!"
        )
        keyboard = [[InlineKeyboardButton("🔙 ተመለስ", callback_data="back_start")]]
        await query.edit_message_text(about_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "back_start":
        await start(update, context)

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_CHAT_ID:
        context.user_data.pop("replying_to_user_id", None)
        await update.message.reply_text("✅ የመልስ ሁነታ ተሰርዟል።")

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message

    if user.id == ADMIN_CHAT_ID:
        target_id = context.user_data.get("replying_to_user_id")

        if not target_id and msg.reply_to_message and msg.reply_to_message.reply_markup:
            for row in msg.reply_to_message.reply_markup.inline_keyboard:
                for btn in row:
                    if btn.callback_data and btn.callback_data.startswith("reply_to_"):
                        target_id = int(btn.callback_data.split("_")[2])

        if target_id:
            try:
                if msg.text:
                    await context.bot.send_message(chat_id=target_id, text=msg.text)
                elif msg.voice:
                    await context.bot.send_voice(chat_id=target_id, voice=msg.voice.file_id)
                elif msg.audio:
                    await context.bot.send_audio(chat_id=target_id, audio=msg.audio.file_id)
                elif msg.photo:
                    await context.bot.send_photo(chat_id=target_id, photo=msg.photo[-1].file_id, caption=msg.caption)
                else:
                    await context.bot.copy_message(chat_id=target_id, from_chat_id=msg.chat_id, message_id=msg.message_id)

                await msg.reply_text("✅ መልእክትዎ ለተጠቃሚው ተልኳል!", quote=True)
            except Exception as e:
                await msg.reply_text(f"❌ መልእክቱን መላክ አልተቻለም፦ {e}", quote=True)
        else:
            await msg.reply_text("⚠ እባክዎ መልስ ለመስጠት የተጠቃሚው መልእክት ስር ያለውን «💬 መልስ (Reply)» የሚለውን ቁልፍ ይጫኑ።", quote=True)
        return

    caption_prefix = f"📩 መልእክት ከ: {user.first_name} (`{user.id}`)\n\n"
    reply_markup = get_admin_reply_markup(user.id)

    if msg.text:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"{caption_prefix}{msg.text}",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
    elif msg.voice:
        await context.bot.send_voice(
            chat_id=ADMIN_CHAT_ID,
            voice=msg.voice.file_id,
            caption=caption_prefix,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
    elif msg.photo:
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=msg.photo[-1].file_id,
            caption=f"{caption_prefix}{msg.caption if msg.caption else ''}",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
    else:
        await context.bot.copy_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=msg.chat_id,
            message_id=msg.message_id,
            reply_markup=reply_markup,
        )

def main():
    # Render የሚያስፈልገውን HTTP ሰርቨር በBackground ማስጀመር
    threading.Thread(target=run_http_server, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_messages))

    print("ገመና ቦት ስራ ጀምሯል...")
    app.run_polling()

if __name__ == "__main__":
    main()
