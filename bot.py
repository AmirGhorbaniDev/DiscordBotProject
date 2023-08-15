import discord
from discord.ext import commands, tasks
import sqlite3
from datetime import datetime, timedelta
import asyncio

# Bot setup
intents = discord.Intents.default()
intents.members = True  # Enable member-related events
intents.messages = True  # Enable message-related events
intents.reactions = True  # Enable reaction-related events
bot = commands.Bot(command_prefix="!", intents=intents)

# Database setup
conn = sqlite3.connect("discord_bot.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    username TEXT,
    message_content TEXT,
    channel_name TEXT,
    timestamp TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    username TEXT,
    reminder_text TEXT,
    remind_at TEXT
)
""")
conn.commit()


@bot.event
async def on_ready():
    print(f"{bot.user.name} is online!")
    check_reminders.start()


# Welcome message for new members
@bot.event
async def on_member_join(member):
    welcome_message = f"Welcome to the server, {member.name}!"
    await member.send(welcome_message)
    print(f"Sent welcome message to {member.name}")


# Log all messages sent in the server
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore bot's own messages

    # Save message to the database
    cursor.execute("""
    INSERT INTO messages (user_id, username, message_content, channel_name, timestamp)
    VALUES (?, ?, ?, ?, ?)
    """, (str(message.author.id), message.author.name, message.content, message.channel.name, str(datetime.now())))
    conn.commit()

    await bot.process_commands(message)  # Ensure other commands are processed


# Bot info command
@bot.command()
async def botinfo(ctx):
    embed = discord.Embed(title="Bot Info", description="Details about the bot", color=discord.Color.blue())
    embed.add_field(name="Name", value=bot.user.name)
    embed.add_field(name="Servers", value=f"{len(bot.guilds)} servers")
    await ctx.send(embed=embed)


# Create a poll
@bot.command()
async def poll(ctx, question: str, *options):
    if len(options) < 2:
        await ctx.send("You need at least two options to create a poll!")
        return
    if len(options) > 10:
        await ctx.send("You can have a maximum of 10 options.")
        return

    embed = discord.Embed(title="Poll", description=question, color=discord.Color.green())
    emoji_numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    for i, option in enumerate(options):
        embed.add_field(name=f"{emoji_numbers[i]} {option}", value="\u200b", inline=False)

    poll_message = await ctx.send(embed=embed)
    for i in range(len(options)):
        await poll_message.add_reaction(emoji_numbers[i])


# Set a reminder
@bot.command()
async def remind(ctx, time: int, unit: str, *, reminder_text: str):
    if unit not in ["seconds", "minutes", "hours"]:
        await ctx.send("Invalid time unit! Use 'seconds', 'minutes', or 'hours'.")
        return

    remind_at = datetime.now()
    if unit == "seconds":
        remind_at += timedelta(seconds=time)
    elif unit == "minutes":
        remind_at += timedelta(minutes=time)
    elif unit == "hours":
        remind_at += timedelta(hours=time)

    cursor.execute("""
    INSERT INTO reminders (user_id, username, reminder_text, remind_at)
    VALUES (?, ?, ?, ?)
    """, (str(ctx.author.id), ctx.author.name, reminder_text, str(remind_at)))
    conn.commit()

    await ctx.send(f"Reminder set! I'll remind you in {time} {unit}.")


# Task to check for reminders
@tasks.loop(seconds=30)
async def check_reminders():
    now = datetime.now()
    cursor.execute("SELECT id, user_id, reminder_text FROM reminders WHERE remind_at <= ?", (str(now),))
    reminders = cursor.fetchall()

    for reminder in reminders:
        user = bot.get_user(int(reminder[1]))
        if user:
            await user.send(f"⏰ Reminder: {reminder[2]}")
        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder[0],))
        conn.commit()

# Assign role based on reaction
@bot.command()
async def reactrole(ctx, role: discord.Role, emoji: str, *, message: str):
    embed = discord.Embed(title="React to Get Role", description=message, color=discord.Color.purple())
    react_message = await ctx.send(embed=embed)
    await react_message.add_reaction(emoji)

    @bot.event
    async def on_raw_reaction_add(payload):
        if payload.message_id == react_message.id and str(payload.emoji) == emoji:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            if member:
                await member.add_roles(role)
                await member.send(f"You have been given the '{role.name}' role!")

