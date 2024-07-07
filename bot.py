import os
import time
import subprocess
import sys
from flask import Flask, request, jsonify
from pyrogram import Client, filters
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_BOT_TOKEN

app = Flask(__name__)

# Telegram bot setup
bot = Client("my_bot", api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH, bot_token=TELEGRAM_BOT_TOKEN)

def remove_audio(input_file, output_file):
    try:
        command = ['ffmpeg', '-i', input_file, '-an', output_file]
        subprocess.run(command, check=True)
        print(f"Audio removed and saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

def trim_video(input_file, start_time, end_time, output_file):
    try:
        command = [
            'ffmpeg', '-i', input_file,
            '-ss', start_time,
            '-to', end_time,
            '-c', 'copy',
            output_file
        ]
        subprocess.run(command, check=True)
        print(f"Video trimmed and saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

@bot.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Hello! Send me a video to process. Use /help to see available commands.")

@bot.on_message(filters.command("help"))
def help(client, message):
    help_text = (
        "Available commands:\n"
        "/start - Start the bot\n"
        "/remove_audio - Remove audio from a video\n"
        "/trim_video - Trim a video\n"
    )
    message.reply_text(help_text)

@bot.on_message(filters.command("remove_audio"))
def handle_remove_audio(client, message):
    if not message.reply_to_message or not message.reply_to_message.video:
        message.reply_text("Please reply to a video message with the /remove_audio command.")
        return

    video = message.reply_to_message.video
    file_path = client.download_media(video)
    output_file_no_audio = "output_no_audio.mp4"

    remove_audio(file_path, output_file_no_audio)

    client.send_video(chat_id=message.chat.id, video=output_file_no_audio)

@bot.on_message(filters.command("trim_video"))
def handle_trim_video(client, message):
    args = message.command
    if len(args) != 3:
        message.reply_text("Usage: /trim_video <start_time> <end_time>\nExample: /trim_video 00:00:10 00:00:20")
        return

    if not message.reply_to_message or not message.reply_to_message.video:
        message.reply_text("Please reply to a video message with the /trim_video command.")
        return

    start_time = args[1]
    end_time = args[2]
    video = message.reply_to_message.video
    file_path = client.download_media(video)
    output_file_trimmed = "output_trimmed.mp4"

    trim_video(file_path, start_time, end_time, output_file_trimmed)

    client.send_video(chat_id=message.chat.id, video=output_file_trimmed)

@app.route('/process', methods=['POST'])
def process_request():
    data = request.json
    input_file = data['input_file']
    output_file = data['output_file']
    action = data['action']

    if action == 'remove_audio':
        remove_audio(input_file, output_file)
    elif action == 'trim_video':
        start_time = data['start_time']
        end_time = data['end_time']
        trim_video(input_file, start_time, end_time, output_file)
    else:
        return jsonify({"error": "Invalid action"}), 400

    return jsonify({"status": "success", "output_file": output_file})

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Run the bot or the web server.")
    parser.add_argument('mode', choices=['bot', 'web'], help="Run mode: bot or web")

    args = parser.parse_args()

    if args.mode == 'bot':
        bot.run()
    elif args.mode == 'web':
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
