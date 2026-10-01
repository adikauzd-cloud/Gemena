import logging
import os
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
BOT_TOKEN = os.getenv("BOT_TOKEN", "8301245356:AAHTqrlV3AbpINhQ1kymSB47SIe5dYKM4hA")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "7030641737"))
# -------------------------------------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የመጀመሪያው የመግቢያ መልእክት እና ምርጫዎች"""
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
    """የቁልፍ ምርጫዎችን ማስተናገጃ"""
    query = update.callback_query
    await query.answer()
    data = query.data

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

        # ለአድሚኑ ማሳወቅ
        admin_alert = (
            f"🔔 **አዲስ ደንበኛ ተገናኝቷል!**\n\n"
            f"• ስም፦ {user.full_name}\n"
            f"• Username: @{user.username if user.username else 'የለውም'}\n"
            f"• ID: `{user.id}`\n"
            f"• መንገድ፦ {comm_type}\n"
            f"• ቆይታ፦ {duration}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_alert, parse_mode="Markdown")

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

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ተጠቃሚው ቦቱ ላይ የሚልከውን ጽሑፍ/ድምፅ በቀጥታ ላንተ ያስተላልፋል"""
    user = update.effective_user
    msg = update.message

    caption_prefix = f"📩 መልእክት ከ: {user.first_name} (`{user.id}`)\n\n"

    if msg.text:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"{caption_prefix}{msg.text}",
            parse_mode="Markdown",
        )
    elif msg.voice:
        await context.bot.send_voice(
            chat_id=ADMIN_CHAT_ID,
            voice=msg.voice.file_id,
            caption=caption_prefix,
            parse_mode="Markdown",
        )
    else:
        await context.bot.forward_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=msg.chat_id,
            message_id=msg.message_id,
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_to_admin))

    print("ገመና ቦት ስራ ጀምሯል...")
    app.run_polling()

if __name__ == "__main__":
    main()
