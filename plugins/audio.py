import os
import tempfile
import subprocess
import sys
import math
import time
import asyncio
import logging 
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
from pyrogram import Client, filters
from plugins import start
from plugins import extractor 
from pyrogram.errors import FloodWait

app = Flask(__name__)

# Thread pool for async processing
executor = ThreadPoolExecutor(max_workers=4)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

user_data = {}

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {e.stderr.decode('utf-8')}")
        return False, e.stderr.decode('utf-8')

def remove_audio(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, '-c', 'copy', '-an', output_file]
    success, _ = run_command(command)
    return success

def trim_video(input_file, start_time, end_time, output_file):
    command = [
        'ffmpeg', '-i', input_file,
        '-ss', start_time,
        '-to', end_time,
        '-map', '0:v',  # map video stream
        '-map', '0:a?',  # map audio stream (if present)
        '-c', 'copy',  # copy both audio and video
        '-avoid_negative_ts', 'make_zero',  # avoid negative timestamps
        output_file
    ]
    success, output = run_command(command)
    if not success:
        print(f"Failed to trim video: {output}", file=sys.stderr)
    return success

@Client.on_message(filters.command("remove_audio"))
async def handle_remove_audio(client, message):
    if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.document):
        await message.reply_text("Please reply to a video or document message with the /remove_audio command.")
        return

    media = message.reply_to_message.video or message.reply_to_message.document
    downloading_message = await message.reply_text("Downloading media...")

    file_path = await client.download_media(media)
    await downloading_message.edit_text("Download complete. Processing...")

    output_file_no_audio = tempfile.mktemp(suffix=".mp4")

    future = executor.submit(remove_audio, file_path, output_file_no_audio)
    success = future.result()

    if success:
        await client.send_document(chat_id=message.chat.id, document=output_file_no_audio)
        await message.reply_text("Upload complete.")
    else:
        await message.reply_text("Failed to process the video. Please try again later.")

@Client.on_message(filters.command("trim_video"))
async def handle_trim_video(client, message):
    args = message.command
    if len(args) != 3:
        await message.reply_text("Usage: /trim_video <start_time> <end_time>\nExample: /trim_video 00:00:10 00:00:20")
        return

    if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.document):
        await message.reply_text("Please reply to a video or document message with the /trim_video command.")
        return

    start_time = args[1]
    end_time = args[2]
    media = message.reply_to_message.video or message.reply_to_message.document
    downloading_message = await message.reply_text("Downloading media...")

    file_path = await client.download_media(media)
    await downloading_message.edit_text("Download complete. Processing...")

    output_file_trimmed = tempfile.mktemp(suffix=".mp4")

    future = executor.submit(trim_video, file_path, start_time, end_time, output_file_trimmed)
    success = future.result()

    if success:
        await client.send_document(chat_id=message.chat.id, document=output_file_trimmed)
        await message.reply_text("Upload complete.")
    else:
        await message.reply_text("Failed to process the video. Please try again later.")
    os.remove(file_path)
    os.remove(output_file_trimmed)

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

@Client.on_message(filters.command("trim_audio"))
async def handle_trim_audio_command(client, message):
    if not message.reply_to_message or not (message.reply_to_message.audio or message.reply_to_message.document):
        await message.reply_text("Please reply to an audio or document message with the /trim_audio command.")
        return

    user_id = message.from_user.id
    user_data[user_id] = {"message_id": message.reply_to_message.message_id}
    await message.reply_text("Enter the start time (in seconds):")

@Client.on_message(filters.text & filters.private)
async def handle_user_input(client, message):
    user_id = message.from_user.id
    if user_id not in user_data:
        return

    if "start_time" not in user_data[user_id]:
        user_data[user_id]["start_time"] = message.text
        await message.reply_text("Enter the end time (in seconds):")
    elif "end_time" not in user_data[user_id]:
        user_data[user_id]["end_time"] = message.text
        await process_audio_trim(client, message)

async def process_audio_trim(client, message):
    user_id = message.from_user.id
    start_time = user_data[user_id]["start_time"]
    end_time = user_data[user_id]["end_time"]
    message_id = user_data[user_id]["message_id"]

    original_message = await client.get_messages(chat_id=message.chat.id, message_ids=message_id)
    media = original_message.audio or original_message.document

    downloading_message = await message.reply_text("Downloading media...")

    file_path = await client.download_media(media)
    await downloading_message.edit_text("Download complete. Processing...")

    output_file_trimmed = tempfile.mktemp(suffix=".mp3")

    command = [
        'ffmpeg', '-i', file_path,
        '-ss', start_time,
        '-to', end_time,
        '-c', 'copy',
        output_file_trimmed
    ]

    success, output = run_command(command)
    if success:
        await client.send_audio(chat_id=message.chat.id, audio=output_file_trimmed)
        await message.reply_text("Upload complete.")
    else:
        await message.reply_text("Failed to process the audio. Please try again later.")
    
    os.remove(file_path)
    os.remove(output_file_trimmed)
    del user_data[user_id]

@Client.on_callback_query()  # Added callback handler
async def callback_handler(client, callback_query):
    data = callback_query.data

    if data == "handle_remove_audio":
        await callback_query.answer()
        await handle_remove_audio(client, callback_query.message)
    elif data == "handle_trim_video":
        await callback_query.answer()
        await callback_query.message.reply_text("Please use the command in the format: /trim_video <start_time> <end_time>.\nExample: /trim_video 00:00:10 00:00:20")
    elif data == "download_file":
        await callback_query.answer()
        await extractor.extract_audio(client, callback_query.message)
    elif data == "close":
        await callback_query.message.delete()

