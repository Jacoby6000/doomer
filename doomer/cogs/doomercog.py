import datetime
from functools import partial
import traceback
import asyncio
import re
import random
import json
from os import path
import atexit

import discord
from discord.ext import commands
from discord import utils

from doomer.discord_utils import (
    pythonify,
    fix_emoji,
    get_messages,
    format_messages,
    get_emoji_string,
    is_number_str,
    send_message,
    get_channel,
    not_a_number,
    get_nick,
    find_questions_and_answers,
    insert_emoji,
)
from doomer.settings import SETTINGS_DIR, DEFAULT_MODEL_NAME, HELP_FILE, COMMAND_PREFIX


class DoomerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = {
            "auto_reply_rate": 1,
            "auto_react_rate": 0,
            "auto_reply_messages": 10,
            "channel_settings": {
                "auto_reply_rate": {},
                "auto_react_rate": {},
            },
            "default_model_name": DEFAULT_MODEL_NAME,
            "dropout_chance": 0,
        }
        atexit.register(self.save_settings)

        if path.exists(SETTINGS_DIR / "settings.json"):
            with open(SETTINGS_DIR / "settings.json", "r") as infile:
                self.settings.update(pythonify(json.load(infile)))

        self.default_model = self.bot.models[self.settings["default_model_name"]]

    # Helpers

    def build_display_settings(self, ctx):
        display_settings = self.settings.copy()
        new_channel_settings = {}
        for setting, values in display_settings["channel_settings"].items():
            new_channel_settings[setting] = {}
            for channel_id, value in values.items():
                channel = utils.get(ctx.guild.text_channels, id=channel_id)
                if channel:
                    new_channel_settings[setting][channel.name] = value
        display_settings["channel_settings"] = new_channel_settings

        return display_settings

    def sanitize_output(self, text):
        return re.sub(r"[\s^]>", "\n>", fix_emoji(text))

    async def complete_text(self, prompt, max_tokens, stop=None):
        loop = asyncio.get_running_loop()
        max_tokens = int(max_tokens)
        completion = await loop.run_in_executor(
            None,
            partial(
                self.default_model.completion_handler,
                prompt=prompt,
                max_tokens=max_tokens,
                stop=stop,
            ),
        )
        completion_text = self.default_model.parse_completion(
            completion=completion, stop=stop
        )
        return self.sanitize_output(completion_text)

    # Listeners

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if not message.author.bot:
            await asyncio.gather(self.react(message), self.reply(message))

    # Automatic Bot Actions

    def should_act(self, message, rate, on_self_reference=True):
        if message.content.startswith(COMMAND_PREFIX):
            return False

        if on_self_reference:
            if self.bot.user.name.lower() in message.content.lower():
                return True

            for user in message.mentions:
                if user.id == self.bot.user.id:
                    return True
        should_send = random.randint(0, 100) < rate
        return should_send

    async def react(self, message):
        if self.settings["default_model_name"] != "gpt3":
            return

        channel_settings = self.settings["channel_settings"]
        if message.channel.id in channel_settings["auto_react_rate"]:
            auto_react_rate = channel_settings["auto_react_rate"][message.channel.id]
        else:
            auto_react_rate = self.settings["auto_react_rate"]

        if self.should_act(message, auto_react_rate, on_self_reference=False):
            messages = list(
                filter(
                    lambda m: not m.content.startswith(COMMAND_PREFIX),
                    await get_messages(message.channel, 100, filter_doomer=False),
                )
            )
            context = format_messages(messages[-20:], emoji_names=False)
            examples = []
            empties = 0
            has_reacts = False
            for message in messages:
                if len(message.clean_content) == 0:
                    continue
                elif len(message.reactions) == 0 and empties < 10:
                    examples.append([message.clean_content, "none"])
                    empties += 1
                else:
                    for reaction in filter(lambda m: not m.me, message.reactions):
                        has_reacts = True
                        examples.append(
                            [
                                message.clean_content,
                                get_emoji_string(
                                    reaction.emoji, emoji_names=False, colons=False
                                ),
                            ]
                        )

            if has_reacts:
                result = await self.answer(
                    list(
                        map(
                            lambda m: format_messages([m], emoji_names=False),
                            messages[-20:],
                        )
                    ),
                    context,
                    examples,
                    format_messages([message], emoji_names=False),
                    50,
                    temp=0,
                )

                if result != "none":
                    emoji = None
                    try:
                        if is_number_str(result):
                            emoji = self.bot.get_emoji(int(result))
                        else:
                            emoji = result
                        await message.add_reaction(emoji)
                    except Exception as e:
                        print(
                            "".join(
                                traceback.format_exception(
                                    etype=type(e), value=e, tb=e.__traceback__
                                )
                            )
                        )

    async def reply(self, message, force=False):
        channel_settings = self.settings["channel_settings"]
        if message.channel.id in channel_settings["auto_reply_rate"]:
            auto_reply_rate = channel_settings["auto_reply_rate"][message.channel.id]
        else:
            auto_reply_rate = self.settings["auto_reply_rate"]

        if force or self.should_act(message, auto_reply_rate):
            async with message.channel.typing():
                messages = fix_emoji(
                    format_messages(
                        await get_messages(
                            message.channel,
                            self.settings["auto_reply_messages"],
                            filter_bot=False,
                        ),
                    )
                )
                banter = await self.complete_text(
                    messages + "\n**[" + get_nick(self.bot.user) + "]**:",
                    300,
                    stop=["**["],
                )
                await message.channel.send(insert_emoji(message.guild, banter))

    # Help Commands

    @commands.command()
    async def how(self, ctx):
        with open(HELP_FILE, "r") as f:
            help_text = f.read()
        await ctx.send(help_text)

    @commands.command()
    async def info(self, ctx):
        embed = discord.Embed(
            title=f"{ctx.guild.name}",
            description="Pretends to be people saying things and doing stuff.",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.blue(),
        )
        embed.add_field(name="Server created at", value=f"{ctx.guild.created_at}")
        embed.add_field(name="Server Owner", value=f"{ctx.guild.owner}")
        embed.add_field(name="Server Region", value=f"{ctx.guild.region}")
        embed.add_field(name="Server ID", value=f"{ctx.guild.id}")
        await ctx.send(embed=embed)

    # Settings Commands

    @commands.command()
    async def update_settings(self, ctx, setting, value):
        if setting == "default_model_name":
            await ctx.send("Use command update_default_model to change this setting")
            return

        if not value.isnumeric():
            await ctx.send("You must provide a numeric value")
            return

        valid_settings = self.settings.keys()
        if setting in valid_settings:
            self.settings[setting] = int(value)
            self.save_settings()
            await ctx.send(f"Setting {setting} set to value {value}")
        else:
            await ctx.send(f"Setting {setting} is not valid.")

    @commands.command()
    async def update_channel_settings(self, ctx, setting, channel_name, value):
        if not value.isnumeric():
            await ctx.send("You must provide a numeric value")
            return

        channel_settings = self.settings["channel_settings"]
        valid_settings = channel_settings.keys()
        if setting in valid_settings:
            try:
                channel = next(
                    filter(lambda x: x.name == channel_name, ctx.guild.text_channels)
                )
                channel_settings[setting][int(channel.id)] = int(value)
                self.save_settings()
                await ctx.send(
                    f"Setting {setting} set to value {value} for channel {channel_name}"
                )
            except StopIteration:
                await ctx.send(f"Channel {channel_name} not found in guild.")
        else:
            await ctx.send(f"Setting {setting} is not valid.")

    @commands.command()
    async def update_model_settings(self, ctx, setting, value, model_name=None):
        if model_name is None:
            model_name = self.settings["default_model_name"]

        model = self.bot.models.get(model_name)
        if not model:
            await ctx.send(f"Model named {model_name} not found.")
            return

        if setting in model.settings.keys():
            if value.isnumeric():
                value = int(value)
            model.settings[setting] = value
            self.save_settings()
            await ctx.send(f"Setting model {model_name} setting {setting} to {value}")
        else:
            await ctx.send(f"Model {model_name} does not have setting {setting}")

    @commands.command()
    async def set_default_model(self, ctx, model_name):
        available_models = self.bot.models.keys()
        model_name = model_name.lower()
        if model_name in available_models:
            self.default_model = self.bot.models[model_name]
            self.settings["default_model_name"] = model_name
            self.save_settings()
            await ctx.send(f"Default model changed to {model_name}")
        else:
            await ctx.send(
                f"{model_name} is not a valid model. "
                f"Choices are: {', '.join(available_models)}"
            )

    @commands.command()
    async def get_settings(self, ctx):
        await send_message(ctx, json.dumps(self.build_display_settings(ctx), indent=4))

    @commands.command()
    async def get_models(self, ctx):
        await send_message(ctx, ", ".join(self.bot.models.keys()))

    @commands.command()
    async def get_model_settings(self, ctx, model_name=None):
        if model_name is None:
            model_name = self.settings["default_model_name"]

        try:
            model_dict = {
                k: v
                for k, v in self.bot.models[model_name].__dict__.items()
                if k[0] != "_"
            }
            await send_message(ctx, json.dumps(model_dict, indent=4))
        except KeyError:
            await ctx.send(f"Model {model_name} is not a valid model.")

    # Text Generation Commands

    @commands.command()
    async def respond(self, ctx):
        try:
            await self.reply(ctx.message, force=True)
        except Exception as e:
            await send_message(ctx, e)

    @commands.command()
    async def simulate_from(
        self, ctx, channel_name, num_messages, response_length, time_str
    ):
        try:
            async with ctx.channel.typing():
                channel = await get_channel(ctx, channel_name)
                if not channel:
                    return
                time = datetime.datetime.fromisoformat(time_str)
                messages = fix_emoji(
                    format_messages(
                        await get_messages(channel, int(num_messages), time)
                    )
                )
                banter = await self.complete_text(messages, response_length)
                await send_message(ctx, banter)
        except Exception as e:
            print(
                "".join(
                    traceback.format_exception(
                        etype=type(e), value=e, tb=e.__traceback__
                    )
                )
            )
            await send_message(ctx, e)

    @commands.command()
    async def simulate(self, ctx, channel_name, num_messages, response_length):
        try:
            async with ctx.channel.typing():
                channel = await get_channel(ctx, channel_name)
                if not channel:
                    return
                messages = fix_emoji(
                    format_messages(await get_messages(channel, int(num_messages)))
                )
                banter = await self.complete_text(messages, response_length)
                await send_message(ctx, banter)
        except Exception as e:
            print(
                "".join(
                    traceback.format_exception(
                        etype=type(e), value=e, tb=e.__traceback__
                    )
                )
            )
            await send_message(ctx, e)

    @commands.command()
    async def complete(self, ctx, length, *text: str):
        in_str = fix_emoji(" ".join(text))
        if length.isnumeric():
            try:
                async with ctx.channel.typing():
                    message = await self.complete_text(in_str, length)
                    await send_message(ctx, in_str + message)
            except Exception as e:
                print(
                    "".join(
                        traceback.format_exception(
                            etype=type(e), value=e, tb=e.__traceback__
                        )
                    )
                )
                await send_message(ctx, e)
        else:
            async with ctx.channel.typing():
                await not_a_number(ctx, length)

    @commands.command()
    async def answer_as_v2(self, ctx, channel_name, user_name, tokens, *question: str):
        if tokens.isnumeric():
            try:
                async with ctx.channel.typing():
                    question = fix_emoji(" ".join(question))
                    channel = await get_channel(ctx, channel_name)
                    async_shit = await asyncio.gather(
                        get_messages(channel, 10),
                        get_messages(channel, 50, from_user=user_name),
                    )
                    # context_messages = format_messages(async_shit[0])
                    user_messages = format_messages(async_shit[1])
                    name = get_nick(async_shit[1][0].author)
                    context_messages = ""

                    await send_message(
                        ctx,
                        await self.complete_text(
                            user_messages
                            + "\n"
                            + context_messages
                            + "\n**["
                            + name
                            + "]**:",
                            tokens,
                            stop=["**["],
                        ),
                    )
            except Exception as e:
                print(
                    "".join(
                        traceback.format_exception(
                            etype=type(e), value=e, tb=e.__traceback__
                        )
                    )
                )
                await send_message(ctx, e)
        else:
            await not_a_number(ctx, tokens)

    @commands.command()
    async def answer_as(self, ctx, channel_name, user_name, tokens, *question: str):
        if tokens.isnumeric():
            try:
                async with ctx.channel.typing():
                    question = fix_emoji(" ".join(question))
                    channel = await get_channel(ctx, channel_name)
                    async_shit = await asyncio.gather(
                        get_messages(channel, 10),
                        get_messages(channel, 200, from_user=user_name),
                        get_messages(
                            channel, 5, other_filter=find_questions_and_answers
                        ),
                    )
                    context_messages = async_shit[0]
                    user_messages = list(map(lambda m: m.clean_content, async_shit[1]))
                    examples = list(
                        map(
                            lambda ms: list(map(lambda m: m.clean_content, ms)),
                            async_shit[2],
                        )
                    )

                    await send_message(
                        ctx,
                        await self.answer(
                            user_messages,
                            format_messages(context_messages),
                            examples,
                            question,
                            tokens,
                        ),
                    )
            except Exception as e:
                print(
                    "".join(
                        traceback.format_exception(
                            etype=type(e), value=e, tb=e.__traceback__
                        )
                    )
                )
                await send_message(ctx, e)
        else:
            await not_a_number(ctx, tokens)

    def save_settings(self):
        SETTINGS_DIR.mkdir(exist_ok=True)
        with open(SETTINGS_DIR / "settings.json", "w") as f:
            json.dump(self.settings, f)

        for model_name, model in self.bot.models.items():
            with open(SETTINGS_DIR / f"{model_name}.json", "w") as f:
                json.dump(model.settings, f)


def setup(bot):
    bot.add_cog(DoomerCog(bot))
