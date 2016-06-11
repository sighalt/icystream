import asyncio

from collections import deque


class YoutubeQueue(object):

    def __init__(self):
        self.queue = deque()

    async def get_next(self):
        while True:
            try:
                return self.queue.popleft()
            except IndexError:
                await asyncio.sleep(1)

    def append(self, url):
        self.queue.append(url)
