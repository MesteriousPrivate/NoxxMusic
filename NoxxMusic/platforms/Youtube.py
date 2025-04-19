import asyncio
import os
import re
from typing import Union

from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from yt_dlp import YoutubeDL

import config
from NoxxMusic.utils.database import is_on_off
from NoxxMusic.utils.formatters import time_to_seconds


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]")
        self.cookies_file = "NoxxMusic/cookies.txt" if os.path.exists("NoxxMusic/cookies.txt") else None

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None, use_cookies=False):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        ytdl_opts = {
            "format": "best[height<=?720][width<=?1280]",
            "quiet": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
        }
        
        if use_cookies and self.cookies_file:
            ytdl_opts["cookiefile"] = self.cookies_file

        try:
            with YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                return (1, info["url"])
        except Exception as e:
            if not use_cookies and self.cookies_file and ("age restricted" in str(e).lower() or "private" in str(e).lower()):
                return await self.video(link, videoid, use_cookies=True)
            return (0, str(e))

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        
        cmd = f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"
        if self.cookies_file:
            cmd = f"yt-dlp --cookies {self.cookies_file} -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"
            
        playlist = await shell_cmd(cmd)
        try:
            result = playlist.split("\n")
            for key in result:
                if key == "":
                    result.remove(key)
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None, use_cookies=False):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        ytdl_opts = {
            "quiet": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
        }
        
        if use_cookies and self.cookies_file:
            ytdl_opts["cookiefile"] = self.cookies_file

        try:
            with YoutubeDL(ytdl_opts) as ydl:
                formats_available = []
                r = ydl.extract_info(link, download=False)
                for format in r["formats"]:
                    try:
                        str(format["format"])
                    except:
                        continue
                    if not "dash" in str(format["format"]).lower():
                        try:
                            format["format"]
                            format["filesize"]
                            format["format_id"]
                            format["ext"]
                            format["format_note"]
                        except:
                            continue
                        formats_available.append(
                            {
                                "format": format["format"],
                                "filesize": format["filesize"],
                                "format_id": format["format_id"],
                                "ext": format["ext"],
                                "format_note": format["format_note"],
                                "yturl": link,
                            }
                        )
                return formats_available, link
        except Exception as e:
            if not use_cookies and self.cookies_file and ("age restricted" in str(e).lower() or "private" in str(e).lower()):
                return await self.formats(link, videoid, use_cookies=True)
            raise e

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link
        loop = asyncio.get_running_loop()

        def _dl(use_cookies=False):
            ydl_opts = {
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
            }
            
            if use_cookies and self.cookies_file:
                ydl_opts["cookiefile"] = self.cookies_file

            if songvideo:
                ydl_opts.update({
                    "format": f"{format_id}+140",
                    "outtmpl": f"downloads/{title}",
                    "merge_output_format": "mp4",
                })
            elif songaudio:
                ydl_opts.update({
                    "format": format_id,
                    "outtmpl": f"downloads/{title}.%(ext)s",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }],
                })
            elif video:
                ydl_opts["format"] = "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])"
            else:
                ydl_opts["format"] = "bestaudio/best"

            ydl_opts["outtmpl"] = ydl_opts.get("outtmpl", "downloads/%(id)s.%(ext)s")
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                path = ydl.prepare_filename(info)
                if not os.path.exists(path):
                    ydl.download([link])
                return path

        try:
            # First try without cookies
            downloaded_file = await loop.run_in_executor(None, _dl)
            direct = True
        except Exception as e:
            if self.cookies_file and ("age restricted" in str(e).lower() or "private" in str(e).lower()):
                # Retry with cookies if available
                downloaded_file = await loop.run_in_executor(None, lambda: _dl(use_cookies=True))
                direct = True
            else:
                if await is_on_off(config.YTDOWNLOADER):
                    raise e
                # Fallback to streaming if download fails
                proc = await asyncio.create_subprocess_exec(
                    "yt-dlp",
                    *(["--cookies", self.cookies_file] if self.cookies_file else []),
                    "-g",
                    "-f",
                    "best[height<=?720][width<=?1280]" if video else "bestaudio/best",
                    f"{link}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                if stdout:
                    downloaded_file = stdout.decode().split("\n")[0]
                    direct = None
                else:
                    raise Exception(stderr.decode())

        return downloaded_file, direct