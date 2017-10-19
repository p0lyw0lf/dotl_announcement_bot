from .shell import Shell
from .variables import VariableCommands
from doclite import Database

from feedparser import parse
import asyncio


class RSSChecker(Shell, VariableCommands):
    def __init__(self, client):
        super().__init__(client)

    def check_rss_factory(self, url, channel, message_template):
        
        def check_rss():
            feed = feedparser.parse(url)
            item = feed["items"][0] # Most recent
            if item["date"] != self.db["last_updated"]:
                self.db["last_parsed"] = item["date"]
                await self.send_simple_message(
                    message_template.replace("%%%", item["link"]),
                    channel
                )
            
        return check_rss
