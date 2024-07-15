import os, time

class Config(object):
    #Audio-_edit_bot client Config 
    API_ID = os.getenv("API_ID", "21740783")
    API_HASH = os.getenv("API_HASH", "a5dc7fec8302615f5b441ec5e238cd46")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "7496680438:AAHyEZDGnIoARpfywrzQOhB27un9pja49p4")

    #port to run web server
    PORT = int(os.getenv('PORT', "8080"))

    # database config
    DB_NAME = os.environ.get("DB_NAME","Speedwolf1")     
    DB_URL  = os.environ.get("DB_URL","mongodb+srv://Speedwolf1:speedwolf24689@cluster0.rgfywsf.mongodb.net/")


    # other configs
    BOT_UPTIME  = time.time()
    START_PIC   = os.environ.get("START_PIC", "https://graph.org/file/5ba316e179b39faa71904.jpg")

    # wes response configuration     
    WEBHOOK = bool(os.environ.get("WEBHOOK", "True"))

    
class Txt(object):
    
    START_TXT = """Hello Friends i am The Advance 📹Video Editor bot i have special Features like "Audio remover" and "video trimmer" 
    
</a>"\n Bot Is Made By @Anime_Warrior_Tamil"</b>"""
    
    ABOUT_TXT = """<b>╭───────────⍟
├🤖 ᴍy ɴᴀᴍᴇ : {}
├🖥️ Dᴇᴠᴇʟᴏᴩᴇʀꜱ : <a href=https://t.me/IllegalDeveloperBot>**ɪʟʟᴇɢᴀʟ ᴅᴇᴠᴇʟᴏᴘᴇʀ**</a> 🕷
├👨‍💻 Pʀᴏɢʀᴀᴍᴇʀ : **ᴋᴜɴᴀʟ ꜱɪɴɢʜ**
╰───────────────⍟ """

    HELP_TXT = """
🌌 <b><u>Hᴏᴡ Tᴏ Sᴇᴛ Tʜᴜᴍʙɴɪʟᴇ</u></b>
  
<b>•»</b> /start Tʜᴇ Bᴏᴛ Aɴᴅ Sᴇɴᴅ Aɴy Pʜᴏᴛᴏ Tᴏ Aᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟy Sᴇᴛ Tʜᴜᴍʙɴɪʟᴇ.
<b>•»</b> /audio_remove Uꜱᴇ Tʜɪꜱ Cᴏᴍᴍᴀɴᴅ Tᴏ Dᴇʟᴇᴛᴇ Yᴏᴜʀ Oʟᴅ Tʜᴜᴍʙɴɪʟᴇ.
<b>•»</b> /video_trim Uꜱᴇ Tʜɪꜱ Cᴏᴍᴍᴀɴᴅ Tᴏ Vɪᴇᴡ

Exᴀᴍᴩʟᴇ:- /set_caption 📕 Fɪʟᴇ Nᴀᴍᴇ: {filename}
💾 Sɪᴢᴇ: {filesize}
⏰ Dᴜʀᴀᴛɪᴏɴ: {duration}

✏️ <b><u>Hᴏᴡ Tᴏ Rᴇɴᴀᴍᴇ A Fɪʟᴇ</u></b>

<b>•»</b> Sᴇɴᴅ Aɴy Fɪʟᴇ Aɴᴅ Tyᴩᴇ Nᴇᴡ Fɪʟᴇ Nɴᴀᴍᴇ \nAɴᴅ Aᴇʟᴇᴄᴛ Tʜᴇ Fᴏʀᴍᴀᴛ [ document, video, audio ].           

ℹ️ 𝗔𝗻𝘆 𝗢𝘁𝗵𝗲𝗿 𝗛𝗲𝗹𝗽 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 :- <a href=https://t.me/IllegalDeveloperBot>𝘽𝙤𝙩 𝘿𝙚𝙫𝙚𝙡𝙤𝙥𝙚𝙧</a>
"""

#⚠️ Dᴏɴ'ᴛ Rᴇᴍᴏᴠᴇ Oᴜʀ Cʀᴇᴅɪᴛꜱ @ILLGELA_DEVELOPER🙏🥲
    DEV_TXT = """hiiiiiiiiiii"""
    
    PROGRESS_BAR = """\n
<b>📁 Size</b> : {1} | {2}
<b>⏳️ Done</b> : {0}%
<b>🚀 Speed</b> : {3}/s
<b>⏰️ ETA</b> : {4} """



#This bot was created by Awt botz
