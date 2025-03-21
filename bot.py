import discord
from discord import app_commands
import os
import asyncio
from dotenv import load_dotenv
from config import config
from commands import register_commands
from utils import Utils

# Load environment variables
load_dotenv()

# Create a bot instance
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class CoinKongBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.utils = Utils()
        
    async def setup_hook(self):
        # This is called when the bot is starting up
        await register_commands(self)
        
bot = CoinKongBot()

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print(f"Bot is {'PAUSED' if config['isPaused'] else 'ACTIVE'}")
    
    # Sync commands with Discord
    await bot.tree.sync()
    print("Synced application commands")

# Run the bot with the token from environment variables
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise ValueError("No token found. Make sure DISCORD_BOT_TOKEN is set in your environment variables.")
    
    asyncio.run(bot.start(token))
