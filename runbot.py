import datetime
import traceback
import logging as log

import discord
from discord import Forbidden
from discord.errors import NotFound
import asyncio

from command_parser import Parser
from command_scheduler import Scheduler
from profanity_filter import ProfanityFilter

client = discord.Client()
log.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=log.INFO)

class Bot(Parser, Scheduler, ProfanityFilter):
    def __init__(self, client, *args, **kwargs):
        super(Bot, self).__init__(client, *args, **kwargs)

bot = Bot(client)
bot.schedule_periodic(
    bot.check_rss, 
    (
        "http://www.daughterofthelilies.com/rss.php",
        "371963209508192276",
        "Hey everyone! A new page just went up: %%%. Enjoy :3",
        "dotl"
    ),
    {'pin_message': True},
    10 * 60, # 10 min
    0
)

bot.schedule_periodic(
    bot.check_rss, 
    (
        "http://bludragongal.tumblr.com/rss",
        "371963443873447947",
        "Hey everyone! Meg just posted to tumblr: %%%. Go check it out!",
        "meg"
    ),
    {},
    10 * 60, # 10 min
    1
)

bot.schedule_periodic(
    bot.check_rss, 
    (
        "http://yokoboo.tumblr.com/rss",
        "371963443873447947",
        "Hey everyone! Yoko just posted to tumblr: %%%. Go check it out!",
        "yoko"
    ), 
    {},
    10 * 60, # 10 min
    2
)

bot.schedule_periodic(
    bot.commit_dbs,
    tuple(),
    {},
    1 * 60 * 60, # 1 hour
    3
)

bot.schedule_periodic(
    bot.check_roles,
    (
        "368564065733312523", # server id
        "387319441865703424", # new role id
        datetime.timedelta(weeks=2)
    ),
    {},
    1 * 24 * 60 * 60, # 1 day
    4
)

unfiltered_commands = {"filter_word", "unfilter_word"}

@client.event
async def on_ready():
    log.info('------')
    log.info('Logged in as')
    log.info(client.user.name)
    log.info(client.user.id)
    log.info('------')
    await bot.start_task(0)
    await bot.start_task(1)
    await bot.start_task(2)
    await bot.start_task(3)
    await bot.start_task(4)
    log.info("Started all tasks")
    await bot.client.change_presence(game=discord.Game(name=bot.special_begin+'help'))
    log.info("Started up successfully")

@client.event
async def on_message(message):
    # REAALY would prefer not to do this b/c people can get
    # around filter using commands that have effects inside them but idk
    command, response = await bot.parse(message)
 
    filtered = bot.filter(message.content)
    if filtered and command not in unfiltered_commands:
        try:
            await client.delete_message(message)
            # we don't want to hit the limit
            for x in range(0, len(filtered), 2048):
                await client.send_message(
                    message.channel,
                    embed=bot.format_embed(message.author, filtered[x:x+2048])
                )
        except (Forbidden, NotFound) as err:
            log.warn("Did not successfully filter message from {0} ({1})."\
                     .format(message.author.name, message.author.id))
            log.warn(str(err))
            pass

        return
        
    if discord.utils.find(lambda user: user.id == client.user.id, message.mentions) and\
    'good' in message.content.lower():
        await bot.send_simple_message("Thank you!~", message.channel)
        
    
    #print(message.channel.id, message.channel.name)
    if response is not None:
        if bot.is_yes(bot.db[message.author.id, "delete_command"]):
            try:
                await client.delete_message(message)
            except (Forbidden, NotFound):
                pass

        await client.send_typing(message.channel)
        
        if isinstance(message.channel, discord.PrivateChannel) and \
           type(response) == str:
            rspmsg = await client.send_message(message.channel, response)
        else:
            output = bot.format_embed(message.author, response)
            rspmsg = await client.send_message(message.channel, embed=output)

        log.debug("Sent response {0} to author {1} ({2})"\
              .format(response, message.author.name, message.author.id))
        # If this is turned on and you still don't want it
        # deleted, just make main_parser send it from
        # within a method instead of returning something
        if bot.is_yes(bot.db[message.author.id, "delete_response"]):
            asyncio.ensure_future(bot.wait_then_delete(rspmsg, message.author))

if __name__ == "__main__":
    file = open('oauth2.tok')
    tok = file.read()
    file.close()
    log.info("Starting...")
    client.run(tok)

