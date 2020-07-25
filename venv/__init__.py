import asyncio
import discord
import os
import re
import sqlite3
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path  # python3 only

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

#Get variables
dtoken = os.environ.get('DISCORD_TOKEN')
server = os.environ.get('DISCORD_SERVER')
mod_role = os.environ.get('MOD_ROLE')
help_category = os.environ.get('HELP_CATEGORY')
discord_prefix = os.environ.get('DISCORD_PREFIX')

#Discord Vassal bot instance
discordbot = commands.Bot(command_prefix=discord_prefix)

#Discord commands
@discordbot.event
async def on_message(ctx):
    if ctx.author.id == 557628352828014614 and '<@&736419760778117220>' in ctx.content:
        text = str('Please select the type of support you are currently seeking by reacting to this message according to your needs.\n\n' + '<:heart:736045005596000337>: Peer Support\n\n' + '<:ambulance:736044831985369188>: Crisis Support\n\n')
        msg = await ctx.channel.send(embed=await build_embed('discord log', 'Triage', text))
        await msg.add_reaction("\U00002764")
        await msg.add_reaction("\U0001F691")
        await asyncio.sleep(1)

        def check(reaction, user):
            return str(reaction.emoji) in ['❤', '🚑']

        reaction, user = await discordbot.wait_for('reaction_add', check=check)

        print(reaction.emoji)
        newname = ctx.channel.name

        if reaction.emoji == '❤':
            newname = re.sub(r'^ticket-', 'peer-', newname)
            print(newname)
            await ctx.channel.edit(name=newname)
        elif reaction.emoji == '🚑':
            newname = re.sub(r'^ticket-', 'crisis-', newname)
            await ctx.channel.edit(name=newname)
        else:
            print("this means nothing.")

        await msg.delete()

    await discordbot.process_commands(ctx)

@discordbot.command()
async def ping(ctx):
    qualified = False
    if mod_role in [r.name for r in ctx.message.author.roles]:
        qualified = True
    if qualified == True:
        await ctx.send(embed=await build_embed('discord log', 'Ping', 'Pong!'))

async def build_embed(mode, title, data):
    if mode == 'discord log':
        embed = discord.Embed(color=0x00cc99, description=data)

    return embed

discordbot.run(dtoken)
