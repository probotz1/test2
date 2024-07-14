import os
import time 
import math
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.command("start"))
def start(client, message):
    start_text = Txt.START_TXT,
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Update Channel", url="https://t.me/Anime_Warrior_Tamil"),
        InlineKeyboardButton("Support Group", url="https://t.me/+NITVxLchQhYzNGZl")
    ],[
        InlineKeyboardButton("Help", callback_data="help"),
        InlineKeyboardButton("About", callback_data="about")
    ],[
        InlineKeyboardButton("Close", callback_data="close")
    ]])
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
    about_text = Txt.ABOUT_TXT,
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data="back")],
        [InlineKeyboardButton("Close", callback_data="close")]
    ])
    callback_query.message.edit_text(about_text, reply_markup=keyboard)

@Client.on_callback_query(filters.regex("back"))
def on_back_callback(client, callback_query):
    start_text = "Hello! Send me a video to process. Use /help to see available commands."
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Update Channel", url="https://t.me/Anime_Warrior_Tamil"),
        InlineKeyboardButton("Support Group", url="https://t.me/+NITVxLchQhYzNGZl")
    ],[
        InlineKeyboardButton("Help", callback_data="help"),
        InlineKeyboardButton("About", callback_data="about")
    ],[
        InlineKeyboardButton("Close", callback_data="close")
    ]])
    callback_query.message.edit_text(start_text, reply_markup=keyboard)

@Client.on_callback_query(filters.regex("close"))
def on_close_callback(client, callback_query):
    callback_query.message.delete()
