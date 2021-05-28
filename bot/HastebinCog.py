import json
import discord
import requests
import sys

from discord_utils import *
from discord.ext import commands

class HastebinCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hastebin(self, ctx, msgs):
        if msgs.isnumeric():
            messages = await get_messages(ctx.channel, int(msgs), filter_doomer=False)
            link = send_to_hastebin(format_messages(messages[1:], emphasize_names=False))
            await ctx.channel.send(link)
        else:
            not_a_number(msgs)


def send_to_hastebin(string):
    hastebin_url = "https://hastebin.com"
    response = requests.post(hastebin_url + "/documents", headers={"content-type": "application/json"}, data=string.encode('utf-8'))
    print(json.dumps(response.text, indent=4))
    return "%s/%s\n" % (hastebin_url, json.loads(response.text)['key'])
