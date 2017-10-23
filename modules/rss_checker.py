from .shell import Shell
from .variables import VariableCommands
from doclite import Database

import feedparser
import asyncio
import requests


class RSSChecker(VariableCommands):
    def __init__(self, client, *args, **kwargs):
        super(RSSChecker, self).__init__(client, *args, **kwargs)

    def check_rss_factory(self, url, channel, message_template, tag):
        dbitem = ("last_link_"+tag,)
        async def check_rss():
            feed = feedparser.parse(url)
            item = feed["items"][0] # Most recent
            if item["link"] != self.db[dbitem]:
                self.db[dbitem] = item["link"]
                for channel_obj in self.client.get_all_channels():
                    # Inefficient, but only gets called once every 30 min anyway
                    if channel_obj.id == channel:
                        await self.send_simple_message(
                            message_template.replace("%%%", item["link"]),
                            channel_obj
                        )
            
        return check_rss
