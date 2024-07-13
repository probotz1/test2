from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery, Message, InputMediaPhoto

from plugins import start
from config import Config, Txt  

@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    await madflixbotz.add_user(client, message)                
    button = InlineKeyboardMarkup([[
      InlineKeyboardButton('📢 Updates', url='https://t.me/Anime_Warrior_Tamil'),
      InlineKeyboardButton('💬 Support', url='https://t.me/+NITVxLchQhYzNGZl')
    ],[
      InlineKeyboardButton('⚙️ Help', callback_data='help'),
      InlineKeyboardButton('💙 About', callback_data='about')
    ],[
        InlineKeyboardButton("🧑‍💻 Developer 🧑‍💻", url='https://t.me/speedwolf')
    ]])

@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data 
    user_id = query.from_user.id  
    
    if data == "home":
        await query.message.edit_text(
            text=Txt.START_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton('📢 Updates', url='https://t.me/Anime_warrior_Tamil'),
                InlineKeyboardButton('💬 Support', url='https://t.me/+NITVxLchQhYzNGZl')
                ],[
                InlineKeyboardButton('⚙️ Help', callback_data='help'),
                InlineKeyboardButton('💙 About', callback_data='about')
                ],[
                InlineKeyboardButton("🧑‍💻 Developer 🧑‍💻", url='https://t.me/speedwolf')
                ]])
        )

    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT.format(client.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton('👉 Owner', url='https://t.me/Anime_Warrior_Tamil')
                ],[
                InlineKeyboardButton('🎵 remove_audio', callback_data='remove_audio'),
                InlineKeyboardButton('✏️ trim_video', callback_data='trim_video')
                ],[
                InlineKeyboardButton('🏠 Home', callback_data='home'),
                InlineKeyboardButton('👈 Back', callback_data='home')
                ]])
       )

    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✖️ Close", callback_data="close"),
                InlineKeyboardButton("🔙 Back", callback_data="home")
            ]])          
        )
    
    
    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
            await query.message.continue_propagation()
        except:
            await query.message.delete()
            await query.message.continue_propagation()
