from datetime import datetime
from pytz import timezone
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import Config
from aiohttp import web
from plugins import web_server
from plugins import start

class Bot(Client):

    def __init__(self):
        super().__init__(
            name="Audio-_edit_bot",
            API_ID=Config.API_ID,
            API_HASH=Config.API_HASH,
            BOT_TOKEN=Config.BOT_TOKEN,
            workers=4,
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username  
        self.uptime = Config.BOT_UPTIME     
        if Config.WEBHOOK:
            app = web.AppRunner(await web_server())
            await app.setup()       
            await web.TCPSite(app, "0.0.0.0", 8080).start()     
        print(f"{me.first_name} Is Started.....✨️")

Bot().run()
