import os
import tempfile
from flask import Flask, request, jsonify
from pyrogram import Client, filters
from plugins import progress, process_video, progress_bar_template

app = Flask(__name__)

@Client.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Hello! Send me a video to process. Use /help to see available commands.")

@Client.on_message(filters.command("help"))
def help(client, message):
    help_text = (
        "Available commands:\n"
        "/start - Start the bot\n"
        "/remove_audio - Remove audio from a video\n"
        "/trim_video - Trim a video\n"
    )
    message.reply_text(help_text)

@Client.on_message(filters.command("remove_audio"))
def handle_remove_audio(client, message):
    if not message.reply_to_message or not message.reply_to_message.video:
        message.reply_text("Please reply to a video message with the /remove_audio command.")
        return

    video = message.reply_to_message.video
    file_path = client.download_media(video)
    output_file_no_audio = tempfile.mktemp(suffix=".mp4")

    try:
        process_video('remove_audio', file_path, output_file_no_audio)
        client.send_video(chat_id=message.chat.id, video=output_file_no_audio)
    except Exception as e:
        message.reply_text(f"Failed to process the video. Error: {e}")

@Client.on_message(filters.command("trim_video"))
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
    output_file_trimmed = tempfile.mktemp(suffix=".mp4")

    try:
        process_video('trim_video', file_path, output_file_trimmed, start_time=start_time, end_time=end_time)
        client.send_video(chat_id=message.chat.id, video=output_file_trimmed)
    except Exception as e:
        message.reply_text(f"Failed to process the video. Error: {e}")

@app.route('/process', methods=['POST'])
def process_request():
    data = request.json
    input_file = data['input_file']
    output_file = data['output_file']
    action = data['action']
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    try:
        process_video(action, input_file, output_file, start_time=start_time, end_time=end_time)
        return jsonify({"status": "success", "output_file": output_file})
    except Exception as e:
        return jsonify({"status": "failure", "message": str(e)}), 500
