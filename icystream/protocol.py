import asyncio
import logging
from uuid import uuid4

import mutagen.mp3
import os
import youtube_dl
from icystream import settings
from icystream.playlist import YoutubeQueue

__author__ = 'sighalt'

logger = logging.getLogger(__file__)
youtube_q = YoutubeQueue()


class UrlReceive(asyncio.Protocol):

    def __init__(self):
        self.queue = youtube_q

    def data_received(self, data):
        url = data.decode("utf-8")
        self.queue.append(url)


class UrlPush(asyncio.Protocol):

    def __init__(self, url):
        self.url = url

    def connection_made(self, transport):
        transport.write(self.url)


class YoutubeIcy(asyncio.Protocol):

    def __init__(self):
        self.transport = None
        self.peer_host = None
        self.peer_port = None
        self.queue = youtube_q

    def connection_made(self, transport):
        self.transport = transport
        self.peer_host, self.peer_port = self.transport.get_extra_info('peername')
        logger.debug("Connection from: %s" % self.peer_host)

    def data_received(self, data):
        logger.debug("Got data: '%s'" % data)
        self.send_headers()
        asyncio.ensure_future(self.stream())

    def send_headers(self):
        """
        * icy-name is the name of the stations
        * icy-genre is the genre that the station resides in
        * icy-pub is basically a switch to either allow the server to publish \
            itself in the directory or not (1 meaning yes and 0 meaning no)
        * icy-br is the bitrate of the stream
        * icy-url is the homepage for the stream
        :return:
        """
        self.transport.write(
            b"HTTP/1.0 200 OK\r\n"
            b"Content-Type: audio/mpeg\r\n"
            b"icy-name: Icystream\r\n"
            b"icy-genre: YouTube\r\n"
            b"icy-pub: 1\r\n"
            b"icy-br: 128\r\n"
            b"icy-url: http://www.sighalt.de/\r\n"
            b"\r\n"
        )
        logger.debug("Sent headers to %s" % self.peer_host)

    async def stream(self):
        while True:
            url = await self.queue.get_next()
            mp3_file = self.download_mp3_from_youtube(url)

            self.send_mp3(mp3_file)
            mp3_duration = self.get_mp3_duration(mp3_file)

            if mp3_duration > 10:
                time_to_suspend = mp3_duration - 10
                logging.info("Waiting for %d seconds" % time_to_suspend)

                await asyncio.sleep(time_to_suspend)

    def get_mp3_duration(self, mp3_file):
        audio = mutagen.mp3.MP3(mp3_file)

        return audio.info.length

    def download_mp3_from_youtube(self, url):
        outfile_format = self.get_outfile_format()
        outfile_name = self.get_outfile_name(outfile_format)

        if not os.path.exists(outfile_name):
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': outfile_format,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        return outfile_name

    def send_mp3(self, filename, start=0):
        with open(filename, "rb") as mp3:
            logger.debug("Sending mp3 file started.")

            mp3.seek(start)
            self.transport.write(mp3.read())

            logger.debug("Sending mp3 file finished.")

    def get_outfile_format(self):
        filebase = str(uuid4())
        filename = filebase + ".%(ext)s"

        return os.path.join(settings.DATA_DIR, filename)

    def get_outfile_name(self, format):
        return format % {"ext": "mp3"}
