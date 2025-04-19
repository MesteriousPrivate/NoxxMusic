import time
import random

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from NoxxMusic import app
from NoxxMusic.misc import _boot_, SUDOERS
from NoxxMusic.plugins.sudo.sudoers import sudoers_list
from NoxxMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
    get_assistant,
)
from NoxxMusic.utils.decorators.language import LanguageStart
from NoxxMusic.utils.formatters import get_readable_time
from NoxxMusic.utils.inline import alive_panel, help_pannel, private_panel, start_panel
from config import BANNED_USERS, VIDEO_URLS
from strings import get_string


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = help_pannel(_)
            return await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} just started the bot to check <b>sudolist</b>.\n\n<b>User ID :</b> <code>{message.from_user.id}</code>\n<b>Username :</b> @{message.from_user.username}",
                )
            return
        if name[0:3] == "inf":
            m = await message.reply_text("🔎")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                    ],
                ]
            )
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} just started the bot to check <b>track information</b>.\n\n<b>User ID :</b> <code>{message.from_user.id}</code>\n<b>Username :</b> @{message.from_user.username}",
                )
    else:
        # Select a random video URL
        random_video = random.choice(VIDEO_URLS)

        # Reply with random video
        await message.reply_video(
            video=random_video,
            caption=_["start_2"].format(message.from_user.mention, app.mention),
            reply_markup=InlineKeyboardMarkup(private_panel(_)),
        )
        if await is_on_off(2):
            sender_id = message.from_user.id
            sender_name = message.from_user.first_name
            return await app.send_message(
                config.LOGGER_ID,
                f"{message.from_user.mention} has started the bot.\n\n**User ID:** {sender_id}\n**Username:** {sender_name}",
            )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def testbot(client, message: Message, _):
    try:
        # Select a random video URL
        random_video = random.choice(VIDEO_URLS)

        # Get the alive panel and uptime
        out = alive_panel(_)
        uptime = int(time.time() - _boot_)

        # Send the random video
        await message.reply_video(
            video=random_video,
            caption=_["start_7"].format(client.mention, get_readable_time(uptime)),
            reply_markup=InlineKeyboardMarkup(out),
        )

        # Add the chat to the served chat list
        return await add_served_chat(message.chat.id)

    except Exception as e:
        print(f"Error: {e}")


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    chat_id = message.chat.id
    # Handle new chat members
    for member in message.new_chat_members:
        try:
            language = await get_lang(chat_id)
            _ = get_string(language)

            # If bot itself joins the chat
            if member.id == client.id:
                random_video = random.choice(VIDEO_URLS)
                userbot = await get_assistant(chat_id)
                out = alive_panel(_)
                await message.reply_video(
                    video=random_video,
                    caption=_["start_8"],
                    reply_markup=InlineKeyboardMarkup(out),
                )

            # Handle owner joining
            if member.id in config.OWNER_ID:
                return await message.reply_text(
                    _["start_3"].format(client.mention, member.mention)
                )

            # Handle SUDOERS joining
            if member.id in SUDOERS:
                return await message.reply_text(
                    _["start_4"].format(client.mention, member.mention)
                )
            return

        except Exception as e:
            print(f"Error: {e}")
            return
