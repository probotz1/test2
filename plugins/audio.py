import os
import tempfile
import subprocess
import sys
import math
import time
import asyncio 
import progress 
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
from pyrogram import Client, filters
from plugins import start
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

app = Flask(__name__)

# Thread pool for async processing
executor = ThreadPoolExecutor(max_workers=4)

def run_command(command):
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

def convert_to_video(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, '-c:v', 'libx264', '-preset', 'slow', '-crf', '22', output_file]
    return run_command(command)

def remove_audio(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, '-c', 'copy', '-an', output_file]
    return run_command(command)

def trim_video(input_file, start_time, end_time, output_file):
    command = [
        'ffmpeg', '-i', input_file,
        '-ss', start_time,
        '-to', end_time,
        '-c', 'copy',
        output_file
    ]
    return run_command(command)

@Client.on_message(filters.command("remove_audio"))
def handle_remove_audio(client, message):
    if not message.reply_to_message or not message.reply_to_message.document:
        message.reply_text("Please reply to a document message with the /remove_audio command.")
        return

    document = message.reply_to_message.document
    start_time = time.time()
    progress_message = message.reply_text("Downloading...")

    file_path = client.download_media(document, progress=progress, progress_args=(progress_message, start_time))
    video_file = tempfile.mktemp(suffix=".mp4")
    output_file_no_audio = tempfile.mktemp(suffix=".mp4")

    future_convert = executor.submit(convert_to_video, file_path, video_file)
    success_convert = future_convert.result()

    if not success_convert:
        progress_message.edit_text("Failed to convert the file to a video. Please try again later.")
        return

    future_remove_audio = executor.submit(remove_audio, video_file, output_file_no_audio)
    success_remove_audio = future_remove_audio.result()

    if success_remove_audio:
        upload_start_time = time.time()
        client.send_video(chat_id=message.chat.id, video=output_file_no_audio, progress=progress, progress_args=(progress_message, upload_start_time))
    else:
        progress_message.edit_text("Failed to process the video. Please try again later.")

@Client.on_message(filters.command("trim_video"))
def handle_trim_video(client, message):
    args = message.command
    if len(args) != 3:
        message.reply_text("Usage: /trim_video <start_time> <end_time>\nExample: /trim_video 00:00:10 00:00:20")
        return

    if not message.reply_to_message or not message.reply_to_message.document:
        message.reply_text("Please reply to a document message with the /trim_video command.")
        return

    start_time = args[1]
    end_time = args[2]
    document = message.reply_to_message.document
    download_start_time = time.time()
    progress_message = message.reply_text("Downloading...")

    file_path = client.download_media(document, progress=progress, progress_args=(progress_message, download_start_time))
    video_file = tempfile.mktemp(suffix=".mp4")
    output_file_trimmed = tempfile.mktemp(suffix=".mp4")

    future_convert = executor.submit(convert_to_video, file_path, video_file)
    success_convert = future_convert.result()

    if not success_convert:
        progress_message.edit_text("Failed to convert the file to a video. Please try again later.")
        return

    future_trim_video = executor.submit(trim_video, video_file, start_time, end_time, output_file_trimmed)
    success_trim_video = future_trim_video.result()

    if success_trim_video:
        upload_start_time = time.time()
        client.send_video(chat_id=message.chat.id, video=output_file_trimmed, progress=progress, progress_args=(progress_message, upload_start_time))
    else:
        progress_message.edit_text("Failed to process the video. Please try again later.")

@app.route('/process', methods=['POST'])
def process_request():
    data = request.json
    input_file = data['input_file']
    output_file = data['output_file']
    action = data['action']

    video_file = tempfile.mktemp(suffix=".mp4")
    convert_success = executor.submit(convert_to_video, input_file, video_file).result()

    if not convert_success:
        return jsonify({"status": "failure", "message": "Failed to convert file to video"}), 500

    if action == 'remove_audio':
        success = executor.submit(remove_audio, video_file, output_file).result()
