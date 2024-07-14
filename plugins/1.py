import tempfile
from pyrogram import Client, filters
from concurrent.futures import ThreadPoolExecutor
from utils.helpers import remove_audio, trim_video
from utils.progress import progress_for_pyrogram

executor = ThreadPoolExecutor(max_workers=4)

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
        client.send_video(chat_id=message.chat.id, video=output_file_no_audio, progress=progress_for_pyrogram)
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
        client.send_video(chat_id=message.chat.id, video=output_file_trimmed, progress=progress_for_pyrogram)
    else:
        message.reply_text("Failed to process the video. Please try again later.")

app = Client("my_bot")
app.run()
