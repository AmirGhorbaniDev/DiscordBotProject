import discord
from discord.ext import commands
import sqlite3
from datetime import datetime

# Bot setup
intents = discord.Intents.default()
intents.members = True  # Required to detect member joins
intents.messages = True  # Required to log messages
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
conn.commit()


@bot.event
async def on_ready():
    print(f"{bot.user.name} is online!")


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


# Kick command (for admins)
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"{member.name} has been kicked. Reason: {reason}")


# Ban command (for admins)
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member.name} has been banned. Reason: {reason}")


# Fetch messages from the database
@bot.command()
async def fetch_logs(ctx, limit: int = 10):
    cursor.execute("SELECT username, message_content, timestamp FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    logs = "\n".join([f"[{row[2]}] {row[0]}: {row[1]}" for row in rows])
    await ctx.send(f"**Last {limit} Messages:**\n{logs}")


# Run the bot (replace with your bot token)
bot.run("YOUR_BOT_TOKEN")
