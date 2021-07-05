import discord
from discord.ext import commands
import time


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} ready')

    @commands.command()
    async def ping(self, ctx):
        start_time = time.monotonic()
        sent_message = await ctx.send('Pong!')
        time_difference = time.monotonic() - start_time
        await sent_message.edit(content='Pong! {:.0f} ms'.format(time_difference * 1000))


def setup(bot):
    bot.add_cog(Utility(bot))
