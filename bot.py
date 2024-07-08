import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
from pyrogram import Client, filters
from aiohttp import web
from plugins import web_server
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_BOT_TOKEN

app = Flask(__name__)

# Telegram bot setup
bot = Client("my_bot", api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH, bot_token=TELEGRAM_BOT_TOKEN)

# Thread pool for async processing
executor = ThreadPoolExecutor(max_workers=4)

def run_command(command):
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

def remove_audio(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, '-c', 'copy', '-an', output_file]
    run_command(command)

def trim_video(input_file, start_time, end_time, output_file):
    command = [
        'ffmpeg', '-i', input_file,
        '-ss', start_time,
        '-to', end_time,
        '-c', 'copy',
        output_file
    ]
    run_command(command)

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

    executor.submit(remove_audio, file_path, output_file_no_audio).result()

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

    executor.submit(trim_video, file_path, start_time, end_time, output_file_trimmed).result()

    client.send_video(chat_id=message.chat.id, video=output_file_trimmed)

@app.route('/process', methods=['POST'])
def process_request():
    data = request.json
    input_file = data['input_file']
    output_file = data['output_file']
    action = data['action']

    if action == 'remove_audio':
        executor.submit(remove_audio, input_file, output_file).result()
    elif action == 'trim_video':
        start_time = data['start_time']
        end_time = data['end_time']
        executor.submit(trim_video, input_file, start_time, end_time, output_file).result()
    else:
        return jsonify({"error": "Invalid action"}), 400

    return jsonify({"status": "success", "output_file": output_file})

async def web_server():
    async def handle(request):
        return web.Response(text="Hello, world")

    app = web.Application()
    app.add_routes([web.get('/', handle)])
    return app

async def start_web_server():
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    PORT = int(os.getenv('PORT', 8080))
    await web.TCPSite(app, bind_address, PORT).start()

if __name__ == "__main__":
    from argparse import ArgumentParser
    import asyncio

    parser = ArgumentParser(description="Run the bot or the web server.")
    parser.add_argument('mode', choices=['bot', 'web'], help="Run mode: bot or web")

    args = parser.parse_args()

    if args.mode == 'bot':
        bot.run()
    elif args.mode == 'web':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_web_server())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()
