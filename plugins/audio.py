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
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

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
    command = ['ffmpeg', '-i', input_file, '-c:v', 'copy', '-an', '-map_metadata', '0', '-movflags', 'use_metadata_tags', output_file]
    success, _ = run_command(command)
    return success

def trim_video(input_file, start_time, end_time, output_file):
    command = [
        'ffmpeg', '-i', input_file,
        '-ss', start_time,
        '-to', end_time,
        '-c:v', 'copy',  # copy video stream
        '-c:a', 'copy',  # copy audio stream
        '-map_metadata', '0', '-movflags', 'use_metadata_tags',
        output_file
    ]
    success, output = run_command(command)
    if not success:
        print(f"Failed to trim video: {output}", file=sys.stderr)
    return success

async def get_video_details(file_path):
    command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size', '-of', 'default=noprint_wrappers=1', file_path]
    success, output = run_command(command)
    if success:
        details = {}
        for line in output.splitlines():
            key, value = line.split('=')
            details[key] = value
        return details
    return None

async def upload_video(client, message, file_loc):

    msg = await message.edit_text(
        text="**Uploading video...**",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Progress", callback_data="progress_msg")]])
    )

    thumb = None
    duration = 0
    width = 0
    height = 0
    title = None

    metadata = extractMetadata(createParser(file_loc))
    if metadata:
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds
        if metadata.has("width"):
            width = metadata.get("width")
        if metadata.has("height"):
            height = metadata.get("height")
        if metadata.has("title"):
            title = metadata.get("title")

    c_time = time.time()    

    try:
        await client.send_video(
            chat_id=message.chat.id,
            video=file_loc,
            thumb=thumb,
            width=width,
            height=height,
            duration=duration,
            caption=title,
            progress=progress_func,  # Ensure you have a progress_func defined elsewhere in your code
            progress_args=(
                "**Uploading video...**",
                msg,
                c_time
            )
        )
    except Exception as e:
        print(e)
        await msg.edit_text("**Some Error Occurred. See Logs for More Info.**")
        return

    await msg.delete()
    await clean_up(file_loc)

@Client.on_message(filters.command("remove_audio"))
async def handle_remove_audio(client, message):
    if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.document):
        await message.reply_text("Please reply to a video or document message with the /remove_audio command.")
        return

    media = message.reply_to_message.video or message.reply_to_message.document
    downloading_message = await message.reply_text("Downloading media...")

    file_path = await client.download_media(media)
    await downloading_message.edit_text("Download complete. Processing...")

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file_no_audio = tempfile.mktemp(suffix=f"_{base_name}_noaudio.mp4")

    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(executor, remove_audio, file_path, output_file_no_audio)

    if success:
        await upload_video(client, message, output_file_no_audio)
        await message.reply_text("Upload complete.")
    else:
        await message.reply_text("Failed to process the video. Please try again later.")

    os.remove(file_path)
    os.remove(output_file_no_audio)

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

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file_trimmed = tempfile.mktemp(suffix=f"_{base_name}_trimmed.mp4")

    future = executor.submit(trim_video, file_path, start_time, end_time, output_file_trimmed)
    success = future.result()

    if success:
        await upload_video(client, message, output_file_trimmed)
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
