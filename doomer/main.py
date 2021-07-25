import openai
import discord
from discord.ext import commands
from cogwatch import watch

from doomer.language_models import GPT2TransformersLanguageModel, GPT3LanguageModel
from doomer import settings


class DoomerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        self.models = self.initialize_models()
        commands.Bot.__init__(
            self, command_prefix=settings.COMMAND_PREFIX, intents=intents
        )

    def initialize_models(self):
        print("Initializing Models...")
        models = {
            "gpt2": GPT2TransformersLanguageModel(
                tokenizer_name="gpt2",
                model_name="gpt2",
            ),
        }
        if settings.OPENAI_API_KEY:
            models["gpt3"] = GPT3LanguageModel(model_name="gpt3")
        return models

    @watch(path=settings.COGS_PATH, preload=True, default_logger=False)
    async def on_ready(self):
        print("Running...")

    async def on_message(self, message):
        if message.author.bot:
            return

        await self.process_commands(message)


def start():
    bot = DoomerBot()
    if settings.OPENAI_API_KEY:
        openai.api_key = settings.OPENAI_API_KEY
    bot.run(settings.DISCORD_API_KEY)


if __name__ == "__main__":
    start()
