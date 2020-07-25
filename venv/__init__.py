import asyncio
import discord
import os
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
    if ctx.author.id == 557628352828014614 and '<@&736018880996048926>' in ctx.content:
        text = str('Please select the type of support you are currently seeking by reacting to this message according to your needs.\n\n' + '<:heart:736045005596000337>: Peer Support\n\n' + '<:ambulance:736044831985369188>: Crisis Support\n\n')
        await ctx.channel.send(embed=await build_embed('discord log', 'Triage', text))

    await discordbot.process_commands(ctx)

@discordbot.command()
async def triage(ctx):
    text = str('Please select the type of support you are currently seeking by reacting to this message according to your needs.\n\n' + '<:heart:736045005596000337>: Peer Support\n\n' + '<:ambulance:736044831985369188>: Crisis Support\n\n')
    await ctx.send(embed=await build_embed('discord log', 'Triage', text))

@discordbot.command()
async def ping(ctx):
    qualified = False
    if mod_role in [r.name for r in ctx.message.author.roles]:
        qualified = True
    if qualified == True:
        await ctx.send(embed=await build_embed('discord log', 'Ping', 'Pong!'))

async def build_embed(mode, title, data):
    if mode == 'stream':
        #get game information
        with open('game.json', 'r') as json_file:
            game_info = json_file.readline()
        game_string = game_info[1:-1]
        game_data = json.loads(game_string)
        #turn info into usable variables
        #create channel link
        link = str('http://www.twitch.tv/' + data['user_name'])
        #get and format stream preview
        thumb = data['thumbnail_url']
        thumb = re.sub('\-{width}x{height}.jpg$', '.jpg', thumb)
        #get and format box art
        boxart = game_data['box_art_url']
        boxart = re.sub('\-{width}x{height}.jpg$', '.jpg', boxart)
        # open and load streamer connections
        streamers = await fetch_all_streamers()
        # turn info into usable variables
        #get discord account info for streamer
        for item in streamers:
            if  item['channel'] == str(data['user_name'].lower()):
                user_id = int(item['discord'])
                streamer_pic = str(item['channelpic'])
        user = await discordbot.fetch_user(user_id)
        author = user.display_name
        icon = user.avatar_url
        #build the embed
        embed = discord.Embed(title=data['title'], url=link,color=0xCC99FF, type='rich')
        embed.add_field(name='Game', value=game_data['name'], inline=True)
        embed.set_thumbnail(url=boxart)
        embed.set_image(url=thumb)
        embed.set_author(name=str(data['user_name']), icon_url=streamer_pic)
        footer_text = str(author + ' is streaming on Twitch as ' + str(data['user_name']))
        embed.set_footer(text=footer_text, icon_url=icon)

    if mode == 'discord log':
        embed = discord.Embed(color=0x00cc99, description=data)

    return embed

discordbot.run(dtoken)
