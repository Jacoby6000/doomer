import openai
import atexit
import discord

from os import getenv
from discord.ext import commands
from DoomerCog import DoomerCog
from HastebinCog import HastebinCog
        

def start():
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix='>', description="This is not a helper bot", intents=intents)
    doomer = DoomerCog(bot)
    hastebin = HastebinCog(bot)

    bot.add_cog(doomer)
    bot.add_cog(hastebin)
    atexit.register(lambda: doomer.save_settings())
    openai.api_key = getenv('OPENAI_API_KEY')
    bot.run(getenv("DISCORD_API_KEY"))

start()
