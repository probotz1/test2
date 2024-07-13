import os
import time
import subprocess
import sys
import tempfile
from flask import Flask, request, jsonify
from pyrogram import Client, filters
from plugins import open
from plugins.database import awtbotz
from progress import progress_for_pyrogram, humanbytes, convert
from concurrent.futures import ThreadPoolExecutor

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
    if not message.reply_to_message or not message.reply_to_message.video:
        message.reply_text("Please reply to a video message with the /remove_audio command.")
        return

    video = message.reply_to_message.video
    file_path = client.download_media(video)
    output_file_no_audio = tempfile.mktemp(suffix=".mp4")

    future = executor.submit(remove_audio, file_path, output_file_no_audio)
    success = future.result()

    if success:
        client.send_video(chat_id=message.chat.id, video=output_file_no_audio)
    else:
        message.reply_text("Failed to process the video. Please try again later.")

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

    future = executor.submit(trim_video, file_path, start_time, end_time, output_file_trimmed)
    success = future.result()

    if success:
        client.send_video(chat_id=message.chat.id, video=output_file_trimmed)
    else:
        message.reply_text("Failed to process the video. Please try again later.")

@app.route('/process', methods=['POST'])
def process_request():
    data = request.json
    input_file = data['input_file']
    output_file = data['output_file']
    action = data['action']

    if action == 'remove_audio':
        success = executor.submit(remove_audio, input_file, output_file).result()
    elif action == 'trim_video':
        start_time = data['start_time']
        end_time = data['end_time']
        success = executor.submit(trim_video, input_file, start_time, end_time, output_file).result()
    else:
        return jsonify({"error": "Invalid action"}), 400

    if not success:
        return jsonify({"status": "failure", "message": "Processing failed"}), 500

    return jsonify({"status": "success", "output_file": output_file})
