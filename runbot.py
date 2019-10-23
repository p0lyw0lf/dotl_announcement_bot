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


PAGEUPDATE_ROLE = 636331098733019166

bot = Bot(client)
bot.schedule_periodic(
    bot.check_rss, 
    (
        "http://www.daughterofthelilies.com/rss.php",
        371963209508192276,
        "Hey everyone %mention%! A new page just went up: %page%. Enjoy :3",
        "dotl"
    ),
    {'pin_message': True, 'mention_role': PAGEUPDATE_ROLE},
    10 * 60, # 10 min
    'dotl_rss'
)

bot.schedule_periodic(
    bot.check_rss, 
    (
        "http://bludragongal.tumblr.com/rss",
        371963443873447947,
        "Hey everyone! Meg just posted to tumblr: %page%. Go check it out!",
        "meg"
    ),
    {},
    10 * 60, # 10 min
    'meg_rss'
)

bot.schedule_periodic(
    bot.check_rss, 
    (
        "http://yokoboo.tumblr.com/rss",
        371963443873447947,
        "Hey everyone! Yoko just posted to tumblr: %page%. Go check it out!",
        "yoko"
    ), 
    {},
    10 * 60, # 10 min
    'yoko_rss'
)

bot.schedule_periodic(
    bot.commit_dbs,
    tuple(),
    {},
    1 * 60 * 60, # 1 hour
    'commit_dbs'
)

bot.schedule_periodic(
    bot.check_roles,
    (
        368564065733312523, # server id
        datetime.timedelta(weeks=2), # time to become a member
        datetime.timedelta(days=1) # time to get unmuted
    ),
    {},
    1 * 24 * 60 * 60, # 1 day
    'check_roles'
)

bot.schedule_periodic(
    bot.delete_previous_pins,
    (
        371963209508192276,
        datetime.timedelta(weeks=8),
    ),
    {},
    1 * 24 * 60 * 60, # 1 day
    'delete_previous_pins'
)

unfiltered_commands = {"filter", "filter_word", "unfilter", "unfilter_word"}

@client.event
async def on_ready():
    log.info('------')
    log.info('Logged in as')
    log.info(client.user.name)
    log.info(client.user.id)
    log.info('------')
    await bot.start_task('dotl_rss')
    await bot.start_task('meg_rss')
    await bot.start_task('yoko_rss')
    await bot.start_task('delete_previous_pins')
    await bot.start_task('commit_dbs')
    await bot.start_task('check_roles')
    await bot.register_all_memes()
    log.info("Started all tasks")
    await bot.client.change_presence(activity=discord.Game(name=bot.special_begin+'help'))
    log.info("Started up successfully")

@client.event
async def on_message(message):
    # REAALY would prefer not to do this b/c people can get
    # around filter using commands that have effects inside them but idk
    try:
        command, response = await bot.parse(message)
    except ValueError:
        log.error("The message \"{}\" broke the bot!".format(message))
        command, response = None, None
 
    filtered = bot.filter(message.content)
    if filtered and command not in unfiltered_commands:
        try:
            await message.delete()
            # we don't want to hit the limit
            for x in range(0, len(filtered), 2048):
                await message.channel.send(
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
                await message.delete()
            except (Forbidden, NotFound):
                pass

        await message.channel.trigger_typing()
        
        if isinstance(message.channel, discord.abc.PrivateChannel) and \
           type(response) == str:
            rspmsg = await message.channel.send(response)
        else:
            output = bot.format_embed(message.author, response)
            if isinstance(output, list):
                rspmsg = []
                for output_obj in output:
                    rspmsg.append(await message.channel.send(embed=output_obj))
            else:
                rspmsg = await message.channel.send(embed=output)

        log.debug("Sent response {0} to author {1} ({2})"\
              .format(response, message.author.name, message.author.id))
        # If this is turned on and you still don't want it
        # deleted, just make main_parser send it from
        # within a method instead of returning something
        if bot.is_yes(bot.db[message.author.id, "delete_response"]):
            if isinstance(rspmsg, list):
                for msg in rspmsg:
                    asyncio.ensure_future(bot.wait_then_delete(msg, message.author))
            else:
                asyncio.ensure_future(bot.wait_then_delete(rspmsg, message.author))

if __name__ == "__main__":
    file = open('oauth2.tok')
    tok = file.read()
    file.close()
    log.info("Starting...")
    client.run(tok)

