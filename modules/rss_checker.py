from .shell import Shell
from .variables import VariableCommands
from doclite import Database

import feedparser
import asyncio
import logging as log

class RSSChecker(VariableCommands):
    def __init__(self, client, *args, **kwargs):
        super(RSSChecker, self).__init__(client, *args, **kwargs)

    def is_announceable(self, item):
        if not item.has_key("tags"): # welp, guess we'll post it
            return True
        for tag in item["tags"]:
            if tag["term"][0:4].upper() == "DOTL":  # catch "dotl fanart", etc
                return True
        return False

    async def check_rss(self, url, channel, message_template, tag, pin_message=False):
        feed = feedparser.parse(url)
        item = feed["items"][0] # Most recent
        dbitem = ("last_link_"+tag,)
        # check announceable first, in case tag is added after it's posted
        if self.is_announceable(item) and item["link"] != self.db[dbitem]:
            self.db[dbitem] = item["link"]
            message = await self.send_simple_message(
                message_template.replace("%%%", item["link"]),
                self.client.get_channel(channel)
            )
            if pin_message: await self.client.pin_message(message)
            
