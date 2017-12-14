import discord
from discord import Forbidden
from discord.errors import NotFound
import asyncio
import logging as log
from command_parser import Parser
from command_scheduler import Scheduler
from profanity_filter import ProfanityFilter

client = discord.Client()
log.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=log.DEBUG)

class Bot(Parser, Scheduler, ProfanityFilter):
    def __init__(self, client, *args, **kwargs):
        super(Bot, self).__init__(client, *args, **kwargs)
    

bot = Bot(client)
bot.schedule_periodic(
    bot.check_rss_factory(
        "http://www.daughterofthelilies.com/rss.php",
        "371963209508192276",
        "Hey everyone! A new page just went up: %%%. Enjoy :3",
        "dotl"
    ),
    10 * 60,
    0
)

bot.schedule_periodic(
    bot.check_rss_factory(
        "http://bludragongal.tumblr.com/rss",
        "371963443873447947",
        "Hey everyone! Meg just posted to tumblr: %%%. Go check it out!",
        "meg"
    ),
    10 * 60,
    1
)

bot.schedule_periodic(
    bot.check_rss_factory(
        "http://yokoboo.tumblr.com/rss",
        "371963443873447947",
        "Hey everyone! Yoko just posted to tumblr: %%%. Go check it out!",
        "yoko"
    ),
    10 * 60,
    2
)

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
    log.info("Started all tasks")

@client.event
async def on_message(message):
    
    filtered = bot.filter(message.content)
    if filtered:
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
        
    response = await bot.parse(message)
    
    output = bot.format_embed(message.author, response)
    #print(message.channel.id, message.channel.name)
    if output is not None:
        if bot.is_yes(bot.db[message.author.id, "delete_command"]):
            try:
                await client.delete_message(message)
            except (Forbidden, NotFound):
                pass

        rspmsg = await client.send_message(message.channel, embed=output)
        log.debug("Sent response {0} to author {1} ({2})"\
              .format(response, message.author.name, message.author.id))
        # If this is turned on and you still don't want it
        # deleted, just make main_parser send it from
        # within a method instead of returning something
        if bot.is_yes(bot.db[message.author.id, "delete_response"]):
            asyncio.ensure_future(bot.wait_then_delete(rspmsg, message.author))

with open('oauth2.tok') as file:
    log.info("Starting...")
    client.run(file.read())
