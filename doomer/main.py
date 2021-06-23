from os import getenv
from pathlib import Path

import openai
import discord
from discord.ext import commands
from cogwatch import watch

COGS_PATH =  'doomer/cogs'

class DoomerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        commands.Bot.__init__(self, command_prefix=">", intents=intents)

    @watch(path=str(COGS_PATH), preload=True, default_logger=False)
    async def on_ready(self):
        print("Running...")

    async def on_message(self, message):
        if message.author.bot:
            return

        await self.process_commands(message)
        

def start():
    bot = DoomerBot()
    openai.api_key = getenv('OPENAI_API_KEY')
    bot.run(getenv("DISCORD_API_KEY"))

start()
