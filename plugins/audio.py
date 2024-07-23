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
from config import Config 
from plugins import extractor 
from pyrogram.errors import FloodWait

app = Flask(__name__)

# Thread pool for async processing
executor = ThreadPoolExecutor(max_workers=4)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {e.stderr.decode('utf-8')}")
        return False, e.stderr.decode('utf-8')

def remove_audio(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, '-c', 'copy', '-an', output_file]
    success, output = run_command(command)
    if not success:
        logging.error(f"Failed to remove audio: {output}")
    return success

def trim_video(input_file, start_time, end_time, output_file):
    command = [
        'ffmpeg', '-i', input_file,
        '-ss', start_time,
        '-to', end_time,
        '-c', 'copy',
        '-avoid_negative_ts', 'make_zero',
        output_file
    ]
    success, output = run_command(command)
    if not success:
        logging.error(f"Failed to trim video: {output}")
    return success

@Client.on_message(filters.video | filters.document)
async def ask_action(client, message):
    keyboard = [
        [
            types.InlineKeyboardButton("Remove Audio", callback_data="remove_audio"),
            types.InlineKeyboardButton("Trim Video", callback_data="trim_video"),
        ]
    ]
    reply_markup = types.InlineKeyboardMarkup(keyboard)
    await message.reply_text("What do you want to do?", reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r"remove_audio|trim_video"))
async def handle_callback_query(client, callback_query):
    action = callback_query.data
    message = callback_query.message
    reply_to_message = message.reply_to_message

    if not reply_to_message:
        await callback_query.answer("This action cannot be performed.")
        return

    media = reply_to_message.video or reply_to_message.document
    if not media:
        await callback_query.answer("This action cannot be performed on this type of message.")
        return

    downloading_message = await message.edit_text("Downloading media...")

    file_path = await client.download_media(media)
    await downloading_message.edit_text("Download complete. Processing...")

    if action == "remove_audio":
        output_file_no_audio = tempfile.mktemp(suffix=".mp4")
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(executor, remove_audio, file_path, output_file_no_audio)

        if success:
            await client.send_document(chat_id=message.chat.id, document=output_file_no_audio)
            await message.reply_text("Audio removed and upload complete.")
        else:
            await message.reply_text("Failed to process the video. Please try again later.")
        
        os.remove(output_file_no_audio)

    elif action == "trim_video":
        # Here we need to handle the additional input required for trimming.
        await callback_query.answer("Please specify the start and end times using the /trim_video command.")
        return

    os.remove(file_path)

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

    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(executor, trim_video, file_path, start_time, end_time, output_file_trimmed)

    if success:
        await client.send_document(chat_id=message.chat.id, document=output_file_trimmed)
        await message.reply_text("Video trimmed and upload complete.")
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
