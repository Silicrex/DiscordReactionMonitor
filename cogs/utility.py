import discord
from discord.ext import commands
import time


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} ready')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            print(f'Invalid command by {ctx.author} in {ctx.channel}: {error.args[0]}')
        elif isinstance(error, commands.NoPrivateMessage):
            print(f'Attempted DM use by {ctx.author}: {error.args[0]}')
        elif isinstance(error, commands.MissingPermissions):
            print(f'{ctx.author} does not have permission:\n'
                  f'Permission: {error.args[0]}\n'
                  f'Message: {ctx.message.content}')
        elif isinstance(error, commands.ChannelNotFound):
            embed = discord.Embed(
                title='Invalid channel',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(
                title='Invalid user',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
        else:
            print('- [Error]')
            print('Class:', error.__class__)
            print('Args:', error.args)
            print('- [Context]')
            print('Server:', ctx.guild)
            print('Channel:', ctx.channel)
            print('User:', ctx.author)
            print('Message:', ctx.message.content)
            print('Message ID:', ctx.message.id)
            raise error

    @commands.command()
    async def ping(self, ctx):
        start_time = time.monotonic()  # Start monotonic clock
        sent_message = await ctx.send('Pong!')  # Send message
        time_difference = time.monotonic() - start_time
        await sent_message.edit(content='Pong! {:.0f} ms'.format(time_difference * 1000))  # Edit time diff in as ms

    @commands.command()
    async def alias(self, ctx):
        embed = discord.Embed(
            title='Command aliases'
        )
        embed.add_field(name='addlog', value='add, a', inline=False)
        embed.add_field(name='removelog', value='remove, r', inline=False)
        embed.add_field(name='status', value='s', inline=False)
        embed.add_field(name='blacklist', value='bl, b'
                                                '\n\nSubcommands\n'
                                                'list: l\n'
                                                'listid: id', inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
