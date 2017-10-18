import discord
from discord import Forbidden
from discord.errors import NotFound
import asyncio
from command_parser import Parser

client = discord.Client()

main_parser = Parser(client)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    # response should be an Embed
    response = await main_parser.parse(message)
    output = main_parser.format_embed(message.author, response)
    if output is not None:
        if main_parser.is_yes(main_parser.db[message.author.id, "delete_command"]):
            try:
                await client.delete_message(message)
            except (Forbidden, NotFound):
                pass
            
        rspmsg = await client.send_message(message.channel, embed=output)
        # If this is turned on and you still don't want it
        # deleted, just make main_parser send it from
        # within a method instead of returning something
        if main_parser.is_yes(main_parser.db[message.author.id, "delete_response"]):
            asyncio.ensure_future(main_parser.wait_then_delete(rspmsg, message.author))

with open('oauth2.tok') as file:
    client.run(file.read())
