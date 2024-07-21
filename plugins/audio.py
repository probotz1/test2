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
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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
    success, _ = run_command(command)
    return success

def trim_video(input_file, start_time, end_time, output_file):
    command = [
        'ffmpeg', '-i', input_file,
        '-ss', start_time,
        '-to', end_time,
        '-c', 'copy',  # copy both audio and video
        '-avoid_negative_ts', 'make_zero',  # avoid negative timestamps
        output_file
    ]
    success, output = run_command(command)
    if not success:
        print(f"Failed to trim video: {output}", file=sys.stderr)
    return success

# Dictionary to store user data
user_data = {}

@Client.on_message(filters.video | filters.document)
async def handle_file(client, message):
    user_id = message.from_user.id
    file_id = message.video.file_id if message.video else message.document.file_id

    # Save the file ID in user data
    user_data[user_id] = {'file_id': file_id}

    # Prompt user to enter a new name
    await message.reply_text("Please enter a new name for the file:")

@Client.on_message(filters.text & ~filters.command)
async def handle_new_name(client, message):
    user_id = message.from_user.id
    if user_id in user_data and 'file_id' in user_data[user_id]:
        new_name = message.text
        user_data[user_id]['new_name'] = new_name

        # Prompt user with inline keyboard for actions
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Remove Audio", callback_data="remove_audio")],
            [InlineKeyboardButton("Trim Video", callback_data="trim_video")]
        ])
        await message.reply_text("What do you want me to do with this file?", reply_markup=keyboard)
    else:
        await message.reply_text("Please send a file first.")

@Client.on_callback_query()
async def handle_callback_query(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data

    if user_id in user_data and 'file_id' in user_data[user_id]:
        file_id = user_data[user_id]['file_id']
        new_name = user_data[user_id]['new_name']
        file_path = await client.download_media(file_id)

        output_file_path = os.path.join(tempfile.gettempdir(), new_name + ".mp4")

        if data == "remove_audio":
            await callback_query.message.edit_text("Removing audio...")
            success = await executor.submit(remove_audio, file_path, output_file_path)

        elif data == "trim_video":
            await callback_query.message.edit_text("Enter start and end time in the format HH:MM:SS HH:MM:SS")

            # Wait for user to enter start and end time
            @Client.on_message(filters.text & ~filters.command)
            async def handle_trim_times(client, message):
                times = message.text.split()
                if len(times) == 2:
                    start_time, end_time = times
                    await callback_query.message.edit_text("Trimming video...")
                    success = await executor.submit(trim_video, file_path, start_time, end_time, output_file_path)
                else:
                    await message.reply_text("Invalid format. Please enter start and end time in the format HH:MM:SS HH:MM:SS")

        if success:
            await client.send_document(chat_id=callback_query.message.chat.id, document=output_file_path)
            await callback_query.message.reply_text("Processing complete.")
        else:
            await callback_query.message.reply_text("Failed to process the video. Please try again later.")
        os.remove(file_path)
        os.remove(output_file_path)
    else:
        await callback_query.message.reply_text("Please send a file first.")

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
