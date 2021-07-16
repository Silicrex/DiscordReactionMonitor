import discord
from discord.ext import commands
import time  # For ping command


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
        embed.add_field(name='blacklist', value='bl, b', inline=False)
        embed.add_field(name='blacklist list', value='blacklist l', inline=False)
        embed.add_field(name='blacklist listid', value='blacklist id', inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title='Bot Commands'
        )
        embed.add_field(name='Utility', inline=False, value='**help**\n'
                                                            '- Displays command info\n'
                                                            '**alias**\n'
                                                            '- Displays command aliases\n'
                                                            '**ping**\n'
                                                            '- Pong')
        embed.add_field(name='Reactions', inline=True, value='**status**\n'
                                                             '- Shows current reaction log settings\n'
                                                             '**addlog\n'
                                                             'removelog**\n'
                                                             '- Shows corresponding log\'s settings\n'
                                                             '**addlog set <channel id/mention>**\n'
                                                             '**removelog set <channel id/mention>**\n'
                                                             '- Sets corresponding log to given channel\n'
                                                             '**addlog <on/off>**\n'
                                                             '**removelog <on/off>**\n'
                                                             '- Turns corresponding log on/off\n'
                                                             '**addlog clear**\n'
                                                             '**removelog clear**\n'
                                                             '- Unsets corresponding log channel')
        embed.add_field(name='Reactions (cont)', inline=True, value='**blacklist**\n'
                                                                    '- Shows blacklist help\n'
                                                                    '**blacklist <add/remove> <user id/mention>**\n'
                                                                    '- Adds/removes given user to/from ignore list\n'
                                                                    '**blacklist list**\n'
                                                                    '- Shows user ignore list in mentions\n'
                                                                    '**blacklist listid**\n'
                                                                    '- Shows user ignore list in user IDs\n'
                                                                    '**blacklist clear**\n'
                                                                    '- Wipes the blacklist')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
