import discord
import datetime
import logging
import openai
import sys
import traceback 
import asyncio
import re
import random
import pandas as pd
import json
import atexit

from discord_utils import *
from discord.ext import commands
from collections import deque
from functools import partial
from os import path

        
class DoomerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = {}
        self.settings["temperature"] = 100
        self.settings["presence_penalty"] = 0
        self.settings["frequency_penalty"] = 0
        self.settings["auto_reply_rate"] = 1
        self.settings["auto_reply_rate_channels"] = {}
        self.settings["auto_react_rate"] = 1
        self.settings["auto_react_rate_channels"] = {}

        with open("docs/usage.md", "r") as usage:
            self.help_text = ''.join(usage.readlines())

        if path.exists("settings.json"):
            with open("settings.json", "r") as infile:
                self.settings.update(json.load(infile))

        print(json.dumps(self.settings, indent=4))

    def update_auto_reply_rate(self, name, value):
        result = None
        if name in self.settings["auto_reply_rate_channels"]:
            result = self.settings["auto_reply_rate_channels"][name]

        self.settings["auto_reply_rate_channels"][name] = value

        return result

    def update_auto_react_rate(self, name, value):
        result = None
        if name in self.settings["auto_react_rate_channels"]:
            result = self.settings["auto_react_rate_channels"][name]

        self.settings["auto_react_rate_channels"][name] = value

        return result

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')

    @commands.command()
    async def how(self, ctx):
        await ctx.send(self.help_text)

    @commands.command()
    async def info(self, ctx):
        embed = discord.Embed(title=f"{ctx.guild.name}", description="Pretends to be people saying things and doing stuff.", timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        embed.add_field(name="Server created at", value=f"{ctx.guild.created_at}")
        embed.add_field(name="Server Owner", value=f"{ctx.guild.owner}")
        embed.add_field(name="Server Region", value=f"{ctx.guild.region}")
        embed.add_field(name="Server ID", value=f"{ctx.guild.id}")
        await ctx.send(embed=embed)

    @commands.command()
    async def get_settings(self, ctx):
        await send_message(ctx, json.dumps(self.settings, indent=4))

    @commands.command()
    async def presence_penalty(self, ctx, n):
        if n.isnumeric():
            cur_presence_penalty = self.settings["presence_penalty"]
            self.settings["presence_penalty"] = int(n)
            await ctx.send("Changing presence_penalty from `"+str(cur_presence_penalty)+"` to `"+n + "`")
        else:
            await not_a_number(ctx, n)

    @commands.command()
    async def frequency_penalty(self, ctx, n):
        if n.isnumeric():
            cur_frequency_penalty = self.settings["frequency_penalty"]
            self.settings["frequency_penalty"] = int(n)
            await ctx.send("Changing frequency_penalty from `"+str(cur_frequency_penalty)+"` to `"+n + "`")
        else:
            await not_a_number(ctx, n)

    @commands.command()
    async def temperature(self, ctx, n):
        if n.isnumeric():
            cur_temp = self.settings["temperature"]
            self.settings["temperature"] = int(n)
            await ctx.send("Changing temperature from `"+str(cur_temp)+"` to `"+n+"`")
        else:
            await not_a_number(ctx, n)
    
    @commands.command()
    async def auto_reply_rate(self, ctx, n):
        if n.isnumeric():
            cur_reply_rate = self.settings["auto_reply_rate"]
            self.settings["auto_reply_rate"] = int(n)
            await ctx.send("Changing auto_reply_rate from `"+str(cur_reply_rate)+"` to `"+n+"`")
        else:
            await not_a_number(ctx, n)
    
    @commands.command()
    async def auto_react_rate(self, ctx, n):
        if n.isnumeric():
            cur_react_rate = self.settings["auto_react_rate"]
            self.settings["auto_react_rate"] = int(n)
            await ctx.send("Changing auto_react_rate from `"+str(cur_react_rate)+"` to `"+n+"`")
        else:
            await not_a_number(ctx, n)
    
    @commands.command()
    async def auto_reply_rate_in(self, ctx, channel_name, n):
        if n.isnumeric():
            channel = await get_channel(ctx, channel_name)
            cur_reply_rate = self.update_auto_reply_rate(channel.name, int(n))
            if cur_reply_rate == None:
                cur_reply_rate = self.settings["auto_reply_rate"]

            await ctx.send(
                "Changing auto_reply_rate from `"+str(cur_reply_rate)+"` to `"+n+"` in channel `" + channel.name + "`."
            )
        else:
            await not_a_number(ctx, n)
    
    @commands.command()
    async def auto_react_rate_in(self, ctx, channel_name, n):
        if n.isnumeric():
            channel = await get_channel(ctx, channel_name)
            cur_react_rate = self.update_auto_react_rate(channel.name, int(n))
            if cur_react_rate == None:
                cur_react_rate = self.settings["auto_react_rate"]

            await ctx.send(
                "Changing auto_react_rate from `"+str(cur_react_rate)+"` to `"+n+"` in channel `" + channel.name + "`."
            )
        else:
            await not_a_number(ctx, n)
    
    @commands.command()
    async def respond(self, ctx):
        try: 
            await self.reply(ctx.message, force=True)
        except Exception as e:
            print(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
            await send_message(ctx, e)

    @commands.command()
    async def simulate_from(self, ctx, channel_name, num_messages, response_length, time_str):
        try: 
            async with ctx.channel.typing():
                channel = await get_channel(ctx, channel_name)
                if not channel:
                    return
                time = datetime.datetime.fromisoformat(time_str)
                messages = fix_emoji(format_messages(await get_messages(channel, int(num_messages), time)))
                print(messages)
                banter = await self.complete_text(messages, response_length)
                await send_message(ctx, banter)
        except Exception as e:
            print(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
            await send_message(ctx, e)

    @commands.command()
    async def simulate(self, ctx, channel_name, num_messages, response_length):
        try: 
            async with ctx.channel.typing():
                channel = await get_channel(ctx, channel_name)
                if not channel:
                    return
                messages = fix_emoji(format_messages(await get_messages(channel, int(num_messages))))
                print(messages)
                banter = await self.complete_text(messages, response_length)
                await send_message(ctx, banter)
        except Exception as e:
            print(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
            await send_message(ctx, e)

    @commands.command()
    async def complete(self, ctx, length, *text: str):
        in_str = fix_emoji(' '.join(text))
        if length.isnumeric():
            try: 
                async with ctx.channel.typing():
                    message = await self.complete_text(in_str, length)
                    await send_message(ctx, in_str + message)
            except Exception as e:
                print(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
                await send_message(ctx, e)
        else:
            async with ctx.channel.typing():
                await not_a_number(ctx, n)

    @commands.command()
    async def complete_no_repeat(self, ctx, length, *text: str):
        in_str = fix_emoji(' '.join(text))
        async with ctx.channel.typing():
            message = await self.complete_text(in_str, length)
            await send_message(ctx, message)
    
    @commands.command()
    async def answer_as_v2(self, ctx, channel_name, user_name, tokens, *question: str):
        if tokens.isnumeric():
            try: 
                async with ctx.channel.typing():
                    question = fix_emoji(' '.join(question))
                    channel = await get_channel(ctx, channel_name)
                    async_shit = await asyncio.gather(
                        get_messages(channel, 10), 
                        get_messages(channel, 50, from_user=user_name)
                    )
                    #context_messages = format_messages(async_shit[0])
                    user_messages = format_messages(async_shit[1])
                    name = get_nick(async_shit[1][0].author)
                    context_messages = ""

                    await send_message(ctx, await self.complete_text(user_messages + "\n" + context_messages + "\n**[" + name + "]**:", tokens, stop=["**["]))
            except Exception as e:
                print(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
                await send_message(ctx, e)
        else:
            await not_a_number(ctx, tokens) 

    
    @commands.command()
    async def answer_as(self, ctx, channel_name, user_name, tokens, *question: str):
        if tokens.isnumeric():
            try: 
                async with ctx.channel.typing():
                    question = fix_emoji(' '.join(question))
                    channel = await get_channel(ctx, channel_name)
                    async_shit = await asyncio.gather(
                        get_messages(channel, 10), 
                        get_messages(channel, 200, from_user=user_name),
                        get_messages(channel, 5, other_filter=find_questions_and_answers)
                    )
                    context_messages = async_shit[0]
                    user_messages = list(map(lambda m: m.clean_content, async_shit[1]))
                    examples = list(map(lambda ms: list(map(lambda m: m.clean_content, ms)), async_shit[2]))

                    await send_message(ctx, await self.answer(user_messages, format_messages(context_messages), examples, question, tokens))
            except Exception as e:
                print(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
                await send_message(ctx, e)
        else:
            await not_a_number(ctx, tokens) 

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if not message.author.bot: 
            await asyncio.gather(
                self.react(message),
                self.reply(message)
            )
    
    def should_act(self, message, rate, on_self_reference=True):
        if message.content.startswith(">"):
            return False

        if on_self_reference:
            if self.bot.user.name.lower() in message.content.lower():
                return True

            for user in message.mentions:
                if user.id == self.bot.user.id:
                    return True

        should_send = random.randint(0,100) < rate
        return should_send

    async def react(self, message):
        auto_react_rate = self.settings["auto_react_rate"]
        if message.channel.name in self.settings["auto_react_rate_channels"]:
            auto_react_rate = self.settings["auto_react_rate_channels"][message.channel.name]

        if self.should_act(message, auto_react_rate, on_self_reference=False):
            messages = list(filter(lambda m: not m.content.startswith(">"), await get_messages(message.channel, 100, filter_doomer=False)))
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
                        examples.append([message.clean_content, get_emoji_string(reaction.emoji, emoji_names=False)])

            if has_reacts:
                result = await self.answer(list(map(lambda m: format_messages([m], emoji_names=False), messages[-20:])), context, examples, format_messages([message], emoji_names=False), 50, temp=0)

                if result != "none":
                    emoji = None
                    try: 
                        if is_number_str(result):
                            emoji = self.bot.get_emoji(int(result))
                        else: 
                            emoji = result
                        await message.add_reaction(emoji)
                    except Exception as e:
                        print(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))

    async def reply(self, message, force=False):
        auto_reply_rate = self.settings["auto_reply_rate"]
        if message.channel.name in self.settings["auto_reply_rate_channels"]:
            auto_reply_rate = self.settings["auto_reply_rate_channels"][message.channel.name]

        if force or self.should_act(message, auto_reply_rate):
            async with message.channel.typing():
                messages = fix_emoji(format_messages(await get_messages(message.channel, int(30), filter_doomer=False)))
                print(messages)
                banter = await self.complete_text(messages + "\n**[" + self.bot.user.name + "]**:", 300, stop=["**["])
                await message.channel.send(banter)

    
    async def complete_text(self, string, length, stop=None):
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None, 
            partial(
                openai.Completion.create,
                engine="davinci", 
                prompt=string, 
                max_tokens=int(length),
                frequency_penalty=hundo_to_float(self.settings["frequency_penalty"]), 
                temperature=hundo_to_float(self.settings["temperature"]), 
                presence_penalty=hundo_to_float(self.settings["presence_penalty"]),
                stop=stop
            )
        )
        return re.sub(r'[\s^]>', '\n>', fix_emoji(response.choices[0].text))

    async def answer(self, docs, context_messages, examples, question, tokens, temp=None):
        loop = asyncio.get_running_loop()
        if temp == None:
            temp = self.settings["temperature"]

        response = await loop.run_in_executor(
            None, 
            partial(
                openai.Answer.create,
                search_model="ada",
                model="davinci", 
                question=question, 
                examples_context=context_messages,
                examples=examples,
                documents=docs,
                max_tokens=int(tokens),
                max_rerank=10,
                stop=["\n"],
                temperature=hundo_to_float(temp),
            )
        )
        return fix_emoji(response.answers[0])

    def save_settings(self):
        with open('settings.json', 'w') as outfile:
            print(json.dumps(self.settings, indent=4))
            json.dump(self.settings, outfile)
