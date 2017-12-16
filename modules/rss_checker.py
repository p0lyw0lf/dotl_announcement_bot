from .shell import Shell
from .variables import VariableCommands
from doclite import Database

import feedparser
import asyncio


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

    def check_rss_factory(self, url, channel, message_template, tag):
        dbitem = ("last_link_"+tag,)
        async def check_rss():
            feed = feedparser.parse(url)
            item = feed["items"][0] # Most recent
            # check announceable first, in case tag is added after it's posted
            if self.is_announceable(item) and item["link"] != self.db[dbitem]:
                self.db[dbitem] = item["link"]
                await self.send_simple_message(
                    message_template.replace("%%%", item["link"]),
                    self.client.get_channel(channel)
                )
            
        return check_rss
