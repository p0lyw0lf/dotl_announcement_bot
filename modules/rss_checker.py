from .shell import Shell
from .variables import VariableCommands
from doclite import Database

from feedparser import parse
import asyncio


class RSSChecker(VariableCommands):
    def __init__(self, client):
        super().__init__(client)

    def check_rss_factory(self, url, channel, message_template):
        
        async def check_rss():
            print("Function actually called")
            feed = feedparser.parse(url)
            item = feed["items"][0] # Most recent
            print("Got here")
            if item["date"] != self.db[("last_updated",)]:
                self.db[("last_updated",)] = item["date"]
                for channel_obj in self.client.get_all_channels():
                    # Inefficient, but only gets called once every 30 min anyway
                    if channel_obj.id == channel:
                        print("Should send")
                        await self.send_simple_message(
                            message_template.replace("%%%", item["link"]),
                            channel_obj
                        )
            
        return check_rss
