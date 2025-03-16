import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ChatMember
from telegram.ext import (ApplicationBuilder, CommandHandler, ConversationHandler,
                          MessageHandler, filters, CallbackContext, ChatMemberHandler)
from Ustatus import UserStatus
from config import ADMIN_UN, BOT_TOKEN, ADMIN_ID
import db_connect

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)

"""
####### List of commands #######
---> /start - 🤖 Starts the bot
---> /chat - 💬 Start searching for a partner
---> /exit - 🔚 Exit from the chat
---> /newchat - ⏭ Exit from the chat and open a new one
---> /stats - 📊 Show bot statistics (only for admin)
"""

# Define a command keyboard for user convenience
command_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("/chat 💬"), KeyboardButton("/exit 🔚")],
        [KeyboardButton("/newchat ⏭"), KeyboardButton("/stats 📊 (Admin)")]
    ],
    resize_keyboard=True
)

# Conversation states
USER_ACTION = 0


async def start(update: Update, context: CallbackContext) -> int:
    """
    Welcomes the user and provides command buttons for easy interaction.
    """
    await update.message.reply_text(
        "👋 Welcome to the ChatBot!\n\n"
        " Use the commands below to interact:\n"
        " /chat - Start searching for a partner\n"
        " /exit - Leave the chat\n"
        " /newchat - Find a new partner\n"
        " /stats - View bot statistics (Admin only)\n\n"
        "Share the bot with your friend to get reward points",
        reply_markup=command_keyboard
    )

    # Insert user into the database if not already present
    user_id = update.effective_user.id
    db_connect.insert_user(user_id)

    return USER_ACTION


async def handle_chat(update: Update, context: CallbackContext) -> None:
    """
    Handles the /chat command, starts searching for a partner.
    """
    user_id = update.effective_user.id
    user_status = db_connect.get_user_status(user_id=user_id)

    if user_status in [UserStatus.IDLE, UserStatus.PARTNER_LEFT]:
        db_connect.set_user_status(user_id=user_id, new_status=UserStatus.IN_SEARCH)
        await update.message.reply_text("🤖 Searching for a partner...")

        # Try to find a match
        partner_id = db_connect.couple(current_user_id=user_id)
        if partner_id:
            await context.bot.send_message(chat_id=user_id, text=
                                            "🤖 You have been paired with a user!\n"
                                            " /chat - Start searching for a partner\n"
                                            " /exit - Leave the chat\n"
                                           )
            await context.bot.send_message(chat_id=partner_id, text=
                                            "🤖 You have been paired with a user!\n"
                                            " /chat - Start searching for a partner\n"
                                            " /exit - Leave the chat\n")
    elif user_status == UserStatus.IN_SEARCH:
        await update.message.reply_text("🤖 You are already searching for a partner.")
    elif user_status == UserStatus.COUPLED:
        await update.message.reply_text("🤖 You are already in a chat! Type /exit to leave.")

        
async def handle_exit_chat(update: Update, context: CallbackContext) -> None:
    """
    Handles the /exit command, leaving the current chat.
    """
    user_id = update.effective_user.id
    if db_connect.get_user_status(user_id=user_id) != UserStatus.COUPLED:
        await update.message.reply_text("🤖 You are not in a chat!type /chat to Start searching.")
        return

    partner_id = db_connect.get_partner_id(user_id)
    if partner_id:
        db_connect.uncouple(user_id=user_id)
        await update.message.reply_text("🤖 You have left the chat! type /newchat - For new chat.")
        await context.bot.send_message(chat_id=partner_id, text="🤖 Your partner has left. Type /chat to find a new partner.")
    else:
        await update.message.reply_text("🤖 Error: Could not find your partner! type /start ")


async def handle_newchat(update: Update, context: CallbackContext) -> None:
    """
    Handles the /newchat command, exiting current chat and finding a new one.
    """
    await handle_exit_chat(update, context)
    await handle_chat(update, context)


async def handle_stats(update: Update, context: CallbackContext) -> None:
    """
    Handles the /stats command, showing bot statistics for admin users.
    """
    user_id = update.effective_user.id
    if user_id != ADMIN_UN:
        await update.message.reply_text("⚠ You are not authorized to view bot statistics.")
        return

    total_users, paired_users = db_connect.retrieve_users_number()
    await update.message.reply_text(
        f"📊 Bot Statistics:\n\n"
        f"👥 Total Users: {total_users}\n"
        f"💑 Paired Users: {paired_users}"
    )


async def handle_message(update: Update, context: CallbackContext) -> None:
    """
    Handles messages sent by users who are in an active chat.
    """
    user_id = update.effective_user.id
    partner_id = db_connect.get_partner_id(user_id)

    if db_connect.get_user_status(user_id) == UserStatus.COUPLED and partner_id:
        await context.bot.copy_message(chat_id=partner_id, from_chat_id=user_id, message_id=update.message.message_id)
    else:
        await update.message.reply_text("🤖 Searching for a partner...")


def is_bot_blocked(update: Update) -> bool:
    """
    Checks if the bot was blocked by the user.
    """
    new_status = update.my_chat_member.new_chat_member.status
    old_status = update.my_chat_member.old_chat_member.status
    return new_status == ChatMember.BANNED and old_status == ChatMember.MEMBER


async def blocked_bot_handler(update: Update, context: CallbackContext):
    """
    Handles cases where the user blocks the bot.
    """
    if is_bot_blocked(update):
        user_id = update.effective_user.id
        if db_connect.get_user_status(user_id) == UserStatus.COUPLED:
            partner_id = db_connect.get_partner_id(user_id)
            db_connect.uncouple(user_id)
            await context.bot.send_message(chat_id=partner_id, text="🤖 Your partner has left. Type /chat to find a new partner.")
        db_connect.remove_user(user_id)


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Ensure database is initialized
    db_connect.create_db()
    db_connect.reset_users_status()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("chat", handle_chat))
    application.add_handler(CommandHandler("exit", handle_exit_chat))
    application.add_handler(CommandHandler("newchat", handle_newchat))
    application.add_handler(CommandHandler("stats", handle_stats))

    # Register other handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(ChatMemberHandler(blocked_bot_handler))

    # Start polling for updates
    application.run_polling()
