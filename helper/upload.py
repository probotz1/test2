import time

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

from helper.tools import clean_up
from helper.progress import progress_func

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def upload_audio(client, message, file_loc):

    msg = await message.edit_text(
        text="**Uploading extracted stream...**",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Progress", callback_data="progress_msg")]])
    )

    title = None
    artist = None
    thumb = None
    duration = 0

    metadata = extractMetadata(createParser(file_loc))
    if metadata and metadata.has("title"):
        title = metadata.get("title")
    if metadata and metadata.has("artist"):
        artist = metadata.get("artist")
    if metadata and metadata.has("duration"):
        duration = metadata.get("duration").seconds

    c_time = time.time()    

    try:
        await client.send_audio(
            chat_id=message.chat.id,
            audio=file_loc,
            thumb=thumb,
            title=title,
            performer=artist,
            duration=duration,
            progress=progress_func,
            progress_args=(
                "**Uploading extracted stream...**",
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


async def upload_subtitle(client, message, file_loc):

    msg = await message.edit_text(
        text="**Uploading extracted subtitle...**",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Progress", callback_data="progress_msg")]])
    )

    c_time = time.time() 

    try:
        await client.send_document(
            chat_id=message.chat.id,
            document=file_loc,
            caption="**@kashirbots**",
            progress=progress_func,
            progress_args=(
                "**Uploading extracted subtitle...**",
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
            progress=progress_func,
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
