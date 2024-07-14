import time 

@Client.on_message(filters.command("start"))
def start(client, message):
    start_text = "Hello! Send me a video to process. Use /help to see available commands."
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Update Channel", url="https://t.me/update_channel")],
        [InlineKeyboardButton("Support Group", url="https://t.me/support_group")],
        [InlineKeyboardButton("Help", callback_data="help")],
        [InlineKeyboardButton("About", callback_data="about")],
        [InlineKeyboardButton("Close", callback_data="close")]
    ])
    message.reply_text(start_text, reply_markup=keyboard)

@Client.on_message(filters.command("help"))
def help(client, message):
    help_text = (
        "Available commands:\n"
        "/start - Start the bot\n"
        "/remove_audio - Remove audio from a video\n"
        "/trim_video - Trim a video\n"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data="back")],
        [InlineKeyboardButton("Close", callback_data="close")]
    ])
    message.reply_text(help_text, reply_markup=keyboard)

@Client.on_callback_query(filters.regex("help"))
def on_help_callback(client, callback_query):
    help_text = (
        "Available commands:\n"
        "/start - Start the bot\n"
        "/remove_audio - Remove audio from a video\n"
        "/trim_video - Trim a video\n"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data="back")],
        [InlineKeyboardButton("Close", callback_data="close")]
    ])
    callback_query.message.edit_text(help_text, reply_markup=keyboard)

@Client.on_callback_query(filters.regex("about"))
def on_about_callback(client, callback_query):
    about_text = (
        "This bot allows you to process videos by removing audio or trimming them.\n"
        "Developed by [Your Name or Company]."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data="back")],
        [InlineKeyboardButton("Close", callback_data="close")]
    ])
    callback_query.message.edit_text(about_text, reply_markup=keyboard)

@Client.on_callback_query(filters.regex("back"))
def on_back_callback(client, callback_query):
    start_text = "Hello! Send me a video to process. Use /help to see available commands."
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Update Channel", url="https://t.me/update_channel")],
        [InlineKeyboardButton("Support Group", url="https://t.me/support_group")],
        [InlineKeyboardButton("Help", callback_data="help")],
        [InlineKeyboardButton("About", callback_data="about")],
        [InlineKeyboardButton("Close", callback_data="close")]
    ])
    callback_query.message.edit_text(start_text, reply_markup=keyboard)

@Client.on_callback_query(filters.regex("close"))
def on_close_callback(client, callback_query):
    callback_query.message.delete()
