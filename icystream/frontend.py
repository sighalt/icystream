import multiprocessing
import asyncio
import logging
from flask import Flask, request
from icystream.protocol import UrlPush

web_app = Flask(__name__)
loop = asyncio.get_event_loop()
logger = logging.getLogger(__file__)


@web_app.route("/", methods=["GET", "POST"])
def enter_youtube_url():

    if request.method == "POST":
        url = request.form["yt_url"]
        url_as_bytes = url.encode("utf-8")
        url_push = loop.create_connection(lambda: UrlPush(url_as_bytes),
                                          "127.0.0.1",
                                          5554)
        loop.run_until_complete(url_push)
        logger.info("Enqueued url '%s'" % url)

    return """<body><form method="POST">
                <input name="yt_url" type="text" />
                <input type="submit" />
              </form></body>"""


class WebInterface(multiprocessing.Process):

    def __init__(self, bind_ip="0.0.0.0", bind_port=8080):
        super().__init__()
        self.bind_ip = bind_ip
        self.bind_port = bind_port

    def run(self):
        web_app.run(host=self.bind_ip, port=self.bind_port)
