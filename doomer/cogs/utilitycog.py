from datetime import datetime

import pandas as pd
from discord.ext import commands

from doomer.settings import DATA_DIR


class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def get_message_history(self, ctx, n_messages=None):
        await ctx.send("Getting messages")
        all_messages = []
        for channel in ctx.guild.text_channels:
            messages = await channel.history(limit=n_messages).flatten()
            all_messages.append(messages)
        all_messages_flat = [i for s in all_messages for i in s]
        amfd = [
            {
                "author": message.author,
                "channel": message.channel,
                "created_at": message.created_at,
                "content": message.content,
                "type": message.type,
            }
            for message in all_messages_flat
        ]
        df = pd.DataFrame(amfd)
        DATA_DIR.mkdir(exist_ok=True)
        df.to_csv(
            DATA_DIR
            / f"{ctx.guild.id}_{round(datetime.now().timestamp())}_messages.csv",
            index=False,
        )
        await ctx.send("Finished getting messages.")


def setup(bot):
    bot.add_cog(UtilityCog(bot))
