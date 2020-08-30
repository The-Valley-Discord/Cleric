import asyncio
import discord
import datetime
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
help_role = os.environ.get('HELP_ROLE')
crisis_role = os.environ.get('CRISIS_ROLE')
help_category = os.environ.get('HELP_CATEGORY')
discord_prefix = os.environ.get('DISCORD_PREFIX')

#Discord Crisis bot instance
discordbot = commands.Bot(command_prefix=discord_prefix)

#Discord commands
@discordbot.event
async def on_ready():
    await discordbot.loop.create_task(follow_ups())

@discordbot.event
async def on_message(ctx):
    if ctx.author.id == 557628352828014614 and '<@&679856667592228939>' in ctx.content:
        text = str('Please select the type of support you are currently seeking by reacting to this message according to your needs.\n\n'
                   + '<:heart:736045005596000337> General Help - Do you need some general advice? Choose this if you need help with something that does not fit in the other categories. \n\n'
                   + '<:question:736973684505575545> Questioning - Are you confused about your identity? Choose this for help regarding questions related to gender, sexuality, or other areas of your identity you may be confused about. \n\n'
                   + '<:ear:736973653325119578> Vent - Do you just need a listening ear, or a void to scream into? Choose this option if you just want to let it all out without any expectation of resolving things. ***Helpers only respond to vent tickets if they are pinged by you*** \n\n'
                   + '<:ambulance:736044831985369188> Crisis - Are you currently having thoughts of self harm or suicide? Please choose this option to immediately escalate this ticket to the Crisis Team. \n\n')
        msg = await ctx.channel.send(embed=await build_embed('discord log', 'Triage', text))
        await msg.add_reaction("\U00002764")
        await msg.add_reaction("\U00002753")
        await msg.add_reaction("\U0001F442")
        await msg.add_reaction("\U0001F691")
        await asyncio.sleep(1)

        def check(reaction, user):
            return str(reaction.emoji) in ['❤', '👂', '❓', '🚑']

        reaction, user = await discordbot.wait_for('reaction_add', check=check)

        print(reaction.emoji)
        newname = ctx.channel.name

        if reaction.emoji == '❤':
            text = "Please take a moment to describe what you need help with and a helper will be with you as soon as possible."
            await ctx.channel.send(text)
        elif reaction.emoji == '👂':
            newname = re.sub(r'^help-', 'vent-', newname)
            await ctx.channel.edit(name=newname)
            text = "This is now a vent ticket. If you would like to speak with a helper, please ping the role, otherwise feel free to use this space to vent as you wish."
            await ctx.channel.send(text)
        elif reaction.emoji == '❓':
            newname = re.sub(r'^help-', 'questioning-', newname)
            await ctx.channel.edit(name=newname)
            text = "Please take a moment to describe what you need help with and a helper will be with you as soon as possible."
            await ctx.channel.send(text)
        elif reaction.emoji == '🚑':
            newname = re.sub(r'^help-', 'crisis-', newname)
            await ctx.channel.edit(name=newname)
            text = "Please take a moment to complete this screening. Once finished, let us know the results so that we can better support you. A member of the <@&744583962210599116> will be with you as soon as possible."
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

discordbot.remove_command('help')
@discordbot.command()
async def help(ctx):
    text =  "**Information and Commands:**\n" \
            "Cleric is a bot designed for triage of help tickets and tracking of crisis screenings. \n\n" \
            "**crisis** - transfer an open ticket to the crisis team. **ONLY USE THIS IN TICKETS** \n" \
            "**qpr (user mention) (score) (time before followup i.e., 7d) (safety plan)** - use this command to log a screening after it is complete \n" \
            "**history (user mention)** - check screening history for a user \n" \
            "**screening (screening id)** - look up information for a specific screening \n" \
            "**discharge (screening id)** - remove a screening from a user's history"
    await ctx.send(embed=await build_embed('discord log', 'Help', text))

@discordbot.command()
async def crisis(ctx, user=None):
    qualified = False
    if mod_role in [r.name for r in ctx.message.author.roles] or help_role in [r.name for r in ctx.message.author.roles]:
        qualified = True
    if ctx.channel.category_id == int(help_category) and qualified == True:
        newname = ctx.channel.name
        newname = re.sub(r'^.*?-', 'crisis-', newname)
        await ctx.channel.edit(name=newname)
        text = "Please take a moment to complete this screening. Once finished, let us know the results so that we can better support you. A member of the <@&744583962210599116> will be with you as soon as possible."
        await ctx.channel.send("https://www.mdcalc.com/phq-9-patient-health-questionnaire-9")
        await ctx.channel.send(text)

@discordbot.command()
async def qpr(ctx, user, score, time, *plan):
    qualified = False
    if mod_role in [r.name for r in ctx.message.author.roles] or crisis_role in [r.name for r in ctx.message.author.roles]:
        qualified = True
    if qualified == True:
        created = datetime.datetime.now()
        duedate = None
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
                duedate = created + datetime.timedelta(days=int(timevalue))
            else:
                unitname = "days"
                duedate = created + datetime.timedelta(days=int(timevalue))
        elif unit == 'm':
            if timevalue == "1":
                unitname = "minute"
                duedate = created + datetime.timedelta(minutes=int(timevalue))
            else:
                unitname = "minutes"
                duedate = created + datetime.timedelta(minutes=int(timevalue))
        elif unit == 's':
            if timevalue == "1":
                unitname = "second"
                duedate = created + datetime.timedelta(seconds=int(timevalue))
            else:
                unitname = "seconds"
                duedate = created + datetime.timedelta(seconds=int(timevalue))

        screening = {
            'user': user,
            'score': score,
            'plan': plan,
            'reminderunit': unit,
            'remindervalue': timevalue,
            'creation': str(created),
            'duedate': str(duedate),
            'reminded': 'false',
            'by': str(ctx.message.author.id)
        }
        print(screening)

        screening_id = await get_newest_id()

        await create_screening(screening)


        await ctx.channel.send("The following record has been created:")
        msg = await ctx.channel.send(embed=await build_embed('screening', 'QPR', screening_id))

@discordbot.command()
async def screening(ctx, id):
    qualified = False
    if mod_role in [r.name for r in ctx.message.author.roles] or crisis_role in [r.name for r in ctx.message.author.roles]:
        qualified = True
    if qualified == True:
        await ctx.channel.send(embed=await build_embed('screening', 'Screening', id))

@discordbot.command()
async def history(ctx, user):
    qualified = False
    if mod_role in [r.name for r in ctx.message.author.roles] or crisis_role in [r.name for r in ctx.message.author.roles]:
        qualified = True
    if qualified == True:
        screenings = await fetch_user(user)
        if str(screenings) != "[]":
            text = str(user + " has the following records:")
            await ctx.channel.send(embed=await build_embed('discord log', 'History', text))
            for item in screenings:
                await ctx.channel.send(embed=await build_embed('screening', 'History', item[0]))
        else:
            text = str("There are no records for " + user)
            await ctx.channel.send(embed=await build_embed('discord log', 'History', text))

@discordbot.command()
async def discharge(ctx, id):
    qualified = False
    if mod_role in [r.name for r in ctx.message.author.roles]:
        qualified = True
    if qualified == True:
        await delete_screening(id)
        text = str("Screening removed from database.")
        await ctx.channel.send(embed=await build_embed('discord log', 'Discharge', text))

async def build_embed(mode, title, data):
    if mode == 'discord log':
        embed = discord.Embed(color=0x00cc99, description=data)
    elif mode == 'screening':
        screening = await fetch_screening(data)
        print(screening)
        user = screening[0][1]
        score = screening[0][2]
        plan = screening[0][6]
        unit = screening[0][4]
        timevalue = screening[0][5]
        created = screening[0][3]
        facilatator = screening[0][9]

        date = datetime.datetime.strptime(created, '%Y-%m-%d %H:%M:%S.%f').strftime('%m-%d-%y at %H:%M')

        text =  str('Participant: ' + user + '\n Screener: <@!' + facilatator + '> \n PHQ9 score: ' + score + "\n Screening date: " + str(date) + "\n Plan for progress: " + plan)
        embed = discord.Embed(color=0x00cc99, description=text)
        footer_text = str('Information for screening #' + str(data))
        embed.set_footer(text=footer_text)


    return embed

async def follow_ups():
    while True:
        await reminders()
        await asyncio.sleep(60)

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
        conn.execute(
            f"INSERT INTO screenings({','.join(screening.keys())}) VALUES({','.join(['?' for v in screening.values()])})",
            tuple(screening.values())
        )
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
        conn.execute(
            "DELETE FROM screenings where id=:id",{"id": id}
        )
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
        screening = conn.execute(
            "SELECT * FROM screenings WHERE id=:id", {"id": id}
        ).fetchall()

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
        screenings = conn.execute(
            "SELECT * FROM screenings WHERE user=:user", {"user": user}
        ).fetchall()

        return screenings
    except conn.Error as error:
        print("Failed to read from sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

async def reminders():
    try:
        conn = await create_connection()
        cursor = conn.cursor()
        sql = """SELECT * from screenings WHERE reminded = "false" """
        print(sql)
        cursor.execute(sql)
        reminders = cursor.fetchall()
        cursor.close()
        print(reminders)
        now = datetime.datetime.now()
        print(now)

        for item in reminders:
            if datetime.datetime.strptime(item[7], '%Y-%m-%d %H:%M:%S.%f') < now:
                await set_reminder_status(item[0])

    except conn.Error as error:
        print("Failed to read from sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

async def set_reminder_status(id):
    try:
        conn = await create_connection()
        conn.execute(
            "UPDATE screenings SET reminded = true WHERE id=:id", {"id": id}
        )

        channel = discordbot.get_channel(680210208496418847)
        screening = await fetch_screening(id)
        user = screening[0][1]
        score = screening[0][2]
        plan = screening[0][6]
        unit = screening[0][4]
        timevalue = screening[0][5]
        created = screening[0][3]

        await channel.send(content="<@&744583962210599116> the following screening requires a followup.", embed=await build_embed('screening', 'Follow Up', id))
    except conn.Error as error:
        print("Failed to write to a row from sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

discordbot.run(dtoken)
