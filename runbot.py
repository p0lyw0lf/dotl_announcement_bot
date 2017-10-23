import discord
from discord import Forbidden
from discord.errors import NotFound
import asyncio
from command_parser import Parser
from command_scheduler import Scheduler
from profanity_filter import ProfanityFilter

client = discord.Client()

class Bot(Parser, Scheduler, ProfanityFilter):
    def __init__(self, client, *args, **kwargs):
        super(Bot, self).__init__(client, *args, **kwargs)
    

bot = Bot(client)
bot.schedule_periodic(
    bot.check_rss_factory(
        "http://www.daughterofthelilies.com/rss.php",
        "370421266735169537",
        "Hey @everyone! A new page just went up: %%%. Enjoy :3",
        "dotl"
    ),
    10 * 60,
    0
)

bot.schedule_periodic(
    bot.check_rss_factory(
        "http://bludragongal.tumblr.com/rss",
        "370421266735169537",
        "Hey @everyone! Meg just posted to tumblr: %%%. Go check it out!",
        "meg"
    ),
    10 * 60,
    1
)

bot.schedule_periodic(
    bot.check_rss_factory(
        "http://yokoboo.tumblr.com/rss",
        "370421266735169537",
        "Hey @everyone! Yoko just posted to tumblr: %%%. Go check it out!",
        "yoko"
    ),
    10 * 60,
    2
)

@client.event
async def on_ready():
    print('------')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await bot.start_task(0)
    await bot.start_task(1)
    await bot.start_task(2)
    print("Started all tasks")

@client.event
async def on_message(message):
    
    filtered = bot.filter(message.content)
    if filtered:
        try:
            await client.delete_message(message)
            await client.send_message(
                message.channel,
                embed=bot.format_embed(message.author, {"You said:": filtered})
            )
        except (Forbidden, NotFound):
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
        # If this is turned on and you still don't want it
        # deleted, just make main_parser send it from
        # within a method instead of returning something
        if bot.is_yes(bot.db[message.author.id, "delete_response"]):
            asyncio.ensure_future(bot.wait_then_delete(rspmsg, message.author))

with open('oauth2.tok') as file:
    print("Starting...")
    client.run(file.read())
