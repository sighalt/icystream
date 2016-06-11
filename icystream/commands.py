import asyncio
import logging
import argparse
from icystream.protocol import YoutubeIcy, UrlReceive
from icystream.frontend import WebInterface

__author__ = 'sighalt'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)


def startup():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--with-webinterface", action="store_true",
                           default=False)
    argparser.add_argument("--stream-port", type=int, default=5555)
    argparser.add_argument("--webinterface-port", type=int, default=8080)
    args = argparser.parse_args()

    loop = asyncio.get_event_loop()
    icy_server = loop.create_server(YoutubeIcy, '0.0.0.0', args.stream_port)
    url_receive_server = loop.create_server(UrlReceive, '0.0.0.0', 5554)
    loop.run_until_complete(icy_server)
    loop.run_until_complete(url_receive_server)

    if args.with_webinterface:
        web_interface = WebInterface(bind_port=args.webinterface_port)
        web_interface.start()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        if args.with_webinterface:
            web_interface.terminate()

        loop.close()
