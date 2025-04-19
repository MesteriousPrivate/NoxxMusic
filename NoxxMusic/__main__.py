import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from NoxxMusic import LOGGER, app, userbot
from NoxxMusic.core.call import Champu
from NoxxMusic.misc import sudo
from NoxxMusic.plugins import ALL_MODULES
from NoxxMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("ᴀssɪsᴛᴀɴᴛ ᴄʟɪᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇs ɴᴏᴛ ᴅᴇғɪɴᴇᴅ, ᴇxɪᴛɪɴɢ...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("NoxxMusic.plugins" + all_module)
    LOGGER("NoxxMusic.plugins").info("sᴜᴄᴄᴇssғᴜʟʟʏ ɪᴍᴘᴏʀᴛᴇᴅ ᴍᴏᴅᴜʟᴇs...")
    await userbot.start()
    await Champu.start()
    try:
        await Champu.stream_call("https://telegra.ph/file/58cc6ef6d0a2a720ea6e3.mp4")
    except NoActiveGroupCall:
        LOGGER("NoxxMusic").error(
            "ᴘʟᴇᴀsᴇ ᴛᴜʀɴ ᴏɴ ᴛʜᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ ᴏғ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ\ᴄʜᴀɴɴᴇʟ.\n\nsᴛᴏᴘᴘɪɴɢ ʙᴏᴛ..."
        )
        exit()
    except:
        pass
    await Champu.decorators()
    LOGGER("NoxxMusic").info(
        "\x4e\x6f\x78\x78\x4d\x75\x73\x69\x63\x20\x42\x6f\x74\x20\x68\x61\x73\x20\x62\x65\x65\x6e\x20\x73\x75\x63\x63\x65\x73\x73\x66\x75\x6c\x6c\x79\x20\x73\x74\x61\x72\x74\x65\x64\x2e\x0a\x0a\x40\x4e\x6f\x78\x78\x4e\x65\x74\x77\x6f\x72\x6b"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("NoxxMusic").info("sᴛᴏᴘᴘɪɴɢ ɴᴏxx ᴍᴜsɪᴄ ʙᴏᴛ...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
