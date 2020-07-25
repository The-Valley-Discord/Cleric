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

#Discord Crisis bot instance
discordbot = commands.Bot(command_prefix=discord_prefix)

#Discord commands
#@discordbot.event
#async def on_ready():
#    await discordbot.loop.create_task(follow_ups())

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
            await ctx.channel.edit(name=newname)
        elif reaction.emoji == '🚑':
            newname = re.sub(r'^ticket-', 'crisis-', newname)
            await ctx.channel.edit(name=newname)
            text = "Please take a moment to complete this screening. Once finished, let us know the results so that we can better support you. A member of the <@&736615019172593778> will be with you as soon as possible."
            await ctx.channel.send("https://www.mdcalc.com/phq-9-patient-health-questionnaire-9")
            await ctx.channel.send(text)

        await msg.delete()

    await discordbot.process_commands(ctx)

@discordbot.command()
async def ping(ctx):
    qualified = False
    if mod_role in [r.name for r in ctx.message.author.roles]:
        qualified = True
    if qualified == True:
        await ctx.send(embed=await build_embed('discord log', 'Ping', 'Pong!'))

@discordbot.command()
async def crisis(ctx, user=None):
    if ctx.channel.category_id == int(help_category):
        newname = ctx.channel.name
        newname = re.sub(r'^.*?-', 'crisis-', newname)
        await ctx.channel.edit(name=newname)
        text = "Please take a moment to complete this screening. Once finished, let us know the results so that we can better support you. A member of the <@&736615019172593778> will be with you as soon as possible."
        await ctx.channel.send("https://www.mdcalc.com/phq-9-patient-health-questionnaire-9")
        await ctx.channel.send(text)

@discordbot.command()
async def qpr(ctx, user, score, time, *plan):
    datetime = ctx.message.created_at
    print(datetime)
    plan = re.sub(r"[()]", "", str(plan))
    plan = re.sub(r"[',']", " ", plan)

    timevalue = re.sub(r"[a-z]$", "", time)
    print(timevalue)
    unit = re.sub(r"\d", "", time)
    print(unit)

    unitname = None
    if unit == 'd':
        if timevalue == "1":
            unitname = "day"
        else:
            unitname = "days"
    elif unit == 'm':
        if timevalue == "1":
            unitname = "minute"
        else:
            unitname = "minutes"
    elif unit == 's':
        if timevalue == "1":
            unitname = "second"
        else:
            unitname = "seconds"

    screening = {
        'user': user,
        'score': score,
        'plan': plan,
        'reminderunit': unit,
        'remindervalue': timevalue,
        'creation': str(datetime)
    }
    print(screening)

    screening_id = await get_newest_id()

    await create_screening(screening)
    if plan == '':
        text = str('user = ' + user + '\n score = ' + score + '\n reminder = ' + timevalue + " " + unitname + "\n screening id = " + screening_id)
    else:
        text = str('user = ' + user + '\n score = ' + score + '\n reminder = ' + timevalue + " " + unitname + "\n plan = " + plan + "\n screening id = " + str(screening_id))
    msg = await ctx.channel.send(embed=await build_embed('discord log', 'QPR', text))

@discordbot.command()
async def screening(ctx, id):
     screening = await fetch_screening(id)
     print(screening[0])
     user = screening[0][1]
     score = screening[0][2]
     plan = screening[0][6]
     unit = screening[0][4]
     timevalue = screening[0][5]
     created = screening[0][3]
     text = str('user = ' + user + '\n score = ' + score + '\n reminder = ' + timevalue + "" + unit + "\n plan = " + plan + "\n created on = " + created)
     await ctx.channel.send(embed=await build_embed('discord log', 'QPR', text))

@discordbot.command()
async def history(ctx, user):
    screenings = await fetch_user(user)
    if str(screenings) != "[]":
        text = str(user + " has the following records:")
        await ctx.channel.send(embed=await build_embed('discord log', 'History', text))
        for item in screenings:
            text = str("Screening ID: " + str(item[0]) + "\n Creation Date: " + item[3])
            await ctx.channel.send(embed=await build_embed('discord log', 'History', text))
    else:
        text = str("There are no records for " + user)
        await ctx.channel.send(embed=await build_embed('discord log', 'History', text))

@discordbot.command()
async def discharge(ctx, id):
        await delete_screening(id)
        text = str("Screening removed from database.")
        await ctx.channel.send(embed=await build_embed('discord log', 'Discharge', text))

async def build_embed(mode, title, data):
    if mode == 'discord log':
        embed = discord.Embed(color=0x00cc99, description=data)

    return embed

async def follow_ups():
    while True:
        await reminders()
        await asyncio.sleep(60)

async def reminders():
    

# sqlite3 functions
async def create_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect('cleric.db')
        print("Connected to cleric.db")
    except Error as e:
        print(e)

    return conn

async def get_newest_id():
    try:
        conn = await create_connection()
        cursor = conn.cursor()
        sql = 'SELECT max(id) FROM screenings'
        cursor.execute(sql)
        max_id = cursor.fetchone()[0]
        cursor.close()

        max_id += 1

        return max_id

    except conn.Error as error:
        print("Failed to write single row to sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

async def create_screening(screening):
    try:
        conn = await create_connection()
        cursor = conn.cursor()
        columns = ', '.join(str('`'+x+'`').replace('/', '_') for x in screening.keys())
        values = ', '.join(str("'"+x+"'").replace('/', '_') for x in screening.values())
        sql = "INSERT INTO %s ( %s ) VALUES ( %s );" % ('screenings', columns, values)
        print(sql)
        cursor.execute(sql)
        cursor.close()
    except conn.Error as error:
        print("Failed to write single row to sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

async def delete_screening(id):
    try:
        conn = await create_connection()
        cursor = conn.cursor()
        sql = str("DELETE FROM screenings where `id` = '" + id + "';")
        print(sql)
        cursor.execute(sql)
        cursor.close()
    except conn.Error as error:
        print("Failed to remove single row to sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

async def fetch_screening(id):
    try:
        conn = await create_connection()
        cursor = conn.cursor()
        sql = """SELECT * from screenings WHERE id = ( %s ) """ % (id)
        print(sql)
        cursor.execute(sql)
        screening = cursor.fetchall()
        cursor.close()

        return screening
    except conn.Error as error:
        print("Failed to write single row to sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

async def fetch_user(user):
    try:
        conn = await create_connection()
        cursor = conn.cursor()
        sql = """SELECT * from screenings WHERE user = ( "%s" ); """ % (user)
        print(sql)
        cursor.execute(sql)
        screenings = cursor.fetchall()
        cursor.close()
        print(screenings)
        return screenings
    except conn.Error as error:
        print("Failed to read from sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

discordbot.run(dtoken)
