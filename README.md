# Discord Bot Project

A feature-rich Discord bot with multiple functionalities, including message logging, welcome messages, polls, role assignment, reminders, and moderation tools.

## Features
- **Welcome Messages**: Automatically sends a direct message to new members when they join the server.
- **Message Logging**: Logs all server messages in an SQLite database for analysis and auditing.
- **Poll Creation**: Users can create polls with up to 10 options.
- **Reminder System**: Users can set reminders with a custom message and time.
- **Role Assignment**: Admins can set up reaction-based role assignment for users.
- **Moderation Tools**: Includes `!kick` and `!ban` commands for admins.
- **Bot Info**: Displays bot details such as server count and name.
- **Fetch Logs**: Retrieves the last N logged messages from the database.

---

## Setup Instructions

### Prerequisites
1. **Python 3.8+**: Ensure Python is installed on your machine.
2. **Discord Bot Token**: Create a bot at the [Discord Developer Portal](https://discord.com/developers/applications) and get the token.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/AmirGhorbaniDev/DiscordBotProject.git
   cd DiscordBotProject
## Install the required dependencies:

pip install discord.py

# Set up the SQLite database (if not already created):

python -c "
import sqlite3;
conn = sqlite3.connect('discord_bot.db');
cursor = conn.cursor();
cursor.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, user_id TEXT, username TEXT, message_content TEXT, channel_name TEXT, timestamp TEXT)');
cursor.execute('CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY, user_id TEXT, username TEXT, reminder_text TEXT, remind_at TEXT)');
conn.commit(); conn.close();
"
# Add your bot token:

# Replace YOUR_BOT_TOKEN in bot.py with your actual bot token.
# Run the bot:
python bot.py

## Usage
# Commands
!botinfo: Displays information about the bot.
!poll <question> <option1> <option2> ...: Creates a poll with up to 10 options.
!remind <time> <unit> <message>: Sets a reminder (units: seconds, minutes, hours).
!reactrole <role> <emoji> <message>: Sets up a reaction role.
!fetch_logs <limit>: Fetches the last N logged messages.
Moderation:
!kick @user <reason>: Kicks a user from the server.
!ban @user <reason>: Bans a user from the server.

## Project Structure

DiscordBotProject/
├── bot.py           # Main bot script
├── discord_bot.db   # SQLite database (created at runtime)
├── README.md        # Project documentation
└── requirements.txt # Dependencies
