from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from NoxxMusic import app
from NoxxMusic.misc import SUDOERS

# 🔹 /send - Message or Media Send to Specific Chat
@app.on_message(filters.command("send") & SUDOERS)
async def send_message(client, message):
    if len(message.command) < 3 and not message.reply_to_message:
        await message.reply_text("❌ ᴜsᴀɢᴇ: /send <username or group_id> <message> (ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇssᴀɢᴇ)")
        return

    target = message.command[1]  # Chat ID or Username
    msg_content = " ".join(message.command[2:]) if len(message.command) > 2 else None
    reply_msg = message.reply_to_message  # Reply to any message

    try:
        bot_member = await client.get_chat_member(chat_id=target, user_id=client.me.id)
        if bot_member.status in ["left", "kicked"]:
            await message.reply_text("❌ ɪ ᴀᴍ ɴᴏᴛ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜɪs ɢʀᴏᴜᴘ.")
            return

        if reply_msg:
            # If replying to a media message, send without forward tag
            sent_message = await reply_msg.copy(chat_id=target)
        else:
            # Send text message
            sent_message = await client.send_message(chat_id=target, text=msg_content)

        # Create URL for the message
        chat_id = sent_message.chat.id
        message_id = sent_message.id
        message_url = f"https://t.me/c/{str(chat_id)[4:]}/{message_id}"

        # Inline Buttons
        view_button = InlineKeyboardButton("🔗 ɢʀᴏᴜᴘ", url=f"https://t.me/{target}")
        mention_button = InlineKeyboardButton("📨 ᴍᴇssᴀɢᴇ", url=message_url)
        reply_markup = InlineKeyboardMarkup([[view_button, mention_button]])

        await message.reply_text("✅ ᴍᴇssᴀɢᴇ sᴇɴᴛ!", reply_markup=reply_markup)

    except Exception as e:
        await message.reply_text(f"❌ ᴇʀʀᴏʀ: {e}")

# 🔹 /send_all - Broadcast to All Users and Groups
@app.on_message(filters.command("send_all") & SUDOERS)
async def broadcast_message(client, message):
    if not message.reply_to_message:
        await message.reply_text("❌ ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ᴍᴇᴅɪᴀ.")
        return

    reply_msg = message.reply_to_message
    all_users = [1786683163]  # Replace with actual user IDs or fetch from database
    all_groups = ["-1002321189618"]  # Replace with actual group IDs

    total_sent = 0
    failed = 0

    for chat_id in all_users + all_groups:
        try:
            await reply_msg.copy(chat_id=chat_id)
            total_sent += 1
        except Exception:
            failed += 1

    await message.reply_text(f"✅ ᴍᴇssᴀɢᴇ ʙʀᴏᴀᴅᴄᴀsᴛᴇᴅ!\n🎯 Sᴜᴄᴄᴇss: {total_sent}\n❌ Fᴀɪʟᴇᴅ: {failed}")
