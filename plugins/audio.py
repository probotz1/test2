import os
import tempfile
import subprocess
import sys
import math
import time
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
from pyrogram import Client, filters
from plugins import start
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from pyrogram.file_id import FileId

app = Flask(__name__)

# Thread pool for async processing
executor = ThreadPoolExecutor(max_workers=4)

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode('utf-8')}", file=sys.stderr)
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
        '-c', 'copy',
        output_file
    ]
    success, _ = run_command(command)
    return success

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

def progress_for_pyrogram(current, total, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 10) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff)
        estimated_total_time = round(elapsed_time * total / current)
        estimated_remaining_time = estimated_total_time - elapsed_time

        progress = "[{0}{1}] {2}%\n".format(
            ''.join(['█' for i in range(math.floor(percentage / 5))]),
            ''.join(['░' for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2))
        
        tmp = progress + "{0} of {1}\nSpeed: {2}/s\nETA: {3}".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            TimeFormatter(estimated_remaining_time)
        )
        
        message.edit_text(tmp)

def humanbytes(size):
    if not size:
        return ""
    power = 2 ** 10
    n = 0
    Dic_powerN = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {Dic_powerN[n]}"

def TimeFormatter(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    tmp = (
        (f"{str(days)}d, " if days else "") +
        (f"{str(hours)}h, " if hours else "") +
        (f"{str(minutes)}m, " if minutes else "") +
        (f"{str(seconds)}s" if seconds else "")
    )

    return tmp.strip(", ")

async def convert(file_path):
    await message.reply_text("Converting file...")

@client.on_message(filters.video | filters.document)
async def handle_media(client, message):
    media = message.video or message.document
    if not media:
        return

    buttons = [
        [InlineKeyboardButton("Remove Audio", callback_data=f"remove_audio|{media.file_id}")],
        [InlineKeyboardButton("Trim Video", callback_data=f"trim_video|{media.file_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text("What do you want to do with this file?", reply_markup=reply_markup)

@client.on_callback_query(filters.regex(r"^(remove_audio|trim_video)\|"))
async def handle_callback_query(client, callback_query):
    data = callback_query.data.split('|')
    action = data[0]
    file_id = data[1]

    media = await client.get_messages(callback_query.message.chat.id, callback_query.message.message_id)
    file = media.reply_to_message.video or media.reply_to_message.document

    downloading_message = await callback_query.message.reply_text("Downloading media...")

    file_path = await client.download_media(file, progress=progress_for_pyrogram, progress_args=(downloading_message, time.time()))
    await downloading_message.edit_text("Download complete. Processing...")

    if action == "remove_audio":
        output_file_no_audio = tempfile.mktemp(suffix=".mp4")
        future = executor.submit(remove_audio, file_path, output_file_no_audio)
        success = future.result()

        if success:
            await client.send_document(chat_id=callback_query.message.chat.id, document=output_file_no_audio)
            await callback_query.message.reply_text("Upload complete.")
        else:
            await callback_query.message.reply_text("Failed to process the video. Please try again later.")

    elif action == "trim_video":
        await callback_query.message.reply_text("Please specify the start and end times in the format: /trim_video <start_time> <end_time>\nExample: /trim_video 00:00:10 00:00:20")

@client.on_message(filters.command("trim_video"))
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

    file_path = await client.download_media(media, progress=progress_for_pyrogram, progress_args=(downloading_message, time.time()))
    await downloading_message.edit_text("Download complete. Processing...")

    output_file_trimmed = tempfile.mktemp(suffix=".mp4")

    future = executor.submit(trim_video, file_path, start_time, end_time, output_file_trimmed)
    success = future.result()

    if success:
        await client.send_document(chat_id=message.chat.id, document=output_file_trimmed)
        await message.reply_text("Upload complete.")
    else:
        await message.reply_text("Failed to process the video. Please try again later.")
