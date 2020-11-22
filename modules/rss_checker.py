from .shell import Shell
from .variables import VariableCommands
from doclite import Database

import feedparser
import asyncio
import logging as log
import datetime
from discord import Forbidden, HTTPException

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

    async def check_rss(self, url, channel, message_template, tag, pin_message=False, mention_role=None):
        feed = feedparser.parse(url)
        item = feed["items"][0] # Most recent
        dbitem = ("last_link_"+tag,)
        # check announceable first, in case tag is added after it's posted
        if self.is_announceable(item) and item["link"] != self.db[dbitem]:
            log.info("new: " + str(item["link"]) + " old: " + str(self.db[dbitem]))
            self.db[dbitem] = item["link"]
            channel_obj = self.client.get_channel(channel)
            
            formatted_message = message_template.replace("%page%", item["link"])
            if not (mention_role is None):
                formatted_message = formatted_message.replace(
                    "%mention%",
                    channel_obj.guild.get_role(mention_role).mention
                )
            message = await self.send_simple_message(
                formatted_message,
                self.client.get_channel(channel)
            )
            if pin_message: await message.pin()

    async def delete_previous_pins(self, channel, cutoff_age):
        """
        It is recommened you schedule this function once a day
        if you set pin_message=True in check_rss
        """

        curtime = datetime.datetime.utcnow()
        
        pins = await self.client.get_channel(channel).pins()

        # Filter so we only unpin messages we sent cutoff_age ago
        # Could compare direct user objects, but I don't trust that...
        my_old_pins = filter(
            lambda p: (p.created_at + cutoff_age < curtime) and \
            (p.author.id == self.client.user.id),
            pins
        )

        for message in my_old_pins:
            try:
                await message.unpin()
            except (Forbidden, HTTPException):
                log.warn("Could not unpin message {} ({})".format(message.id, message.timestamp))
        
        
        
