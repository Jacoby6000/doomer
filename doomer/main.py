from os import getenv

import openai
import discord
from discord.ext import commands
from cogwatch import watch
from dotenv import load_dotenv

from doomer.language_models import GPT2TransformersLanguageModel, GPT3LanguageModel
from doomer import settings

COGS_PATH = "doomer/cogs"
load_dotenv(settings.DOTENV_PATH)


class DoomerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        self.models = self.initialize_models()
        commands.Bot.__init__(self, command_prefix=">", intents=intents)

    def initialize_models(self):
        print("Initializing Models...")
        return {
            "gpt3": GPT3LanguageModel(model_name="gpt3"),
            "gpt2": GPT2TransformersLanguageModel(
                tokenizer_name="gpt2",
                model_name="gpt2",
            ),
        }

    @watch(path=COGS_PATH, preload=True, default_logger=False)
    async def on_ready(self):
        print("Running...")

    async def on_message(self, message):
        if message.author.bot:
            return

        await self.process_commands(message)


def start():
    bot = DoomerBot()
    openai.api_key = getenv("OPENAI_API_KEY")
    bot.run(getenv("DISCORD_API_KEY"))


if __name__ == "__main__":
    start()
