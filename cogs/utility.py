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
        elif isinstance(error, commands.MissingRequiredArgument):
            msg = ctx.message.content
            command = str(self.bot.get_command(msg[1:]))  # Remove prefix, convert aliases to full command
            help_dict = get_help_dict()
            embed = get_help_embed(help_dict, command)
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
        embed.add_field(name='addlog set', value='addlog s', inline=False)
        embed.add_field(name='removelog', value='remove, r', inline=False)
        embed.add_field(name='removelog set', value='removelog s', inline=False)
        embed.add_field(name='status', value='s', inline=False)
        embed.add_field(name='blacklist', value='bl, b', inline=False)
        embed.add_field(name='blacklist add', value='blacklist a', inline=False)
        embed.add_field(name='blacklist remove', value='blacklist r', inline=False)
        embed.add_field(name='blacklist list', value='blacklist l', inline=False)
        embed.add_field(name='blacklist listid', value='blacklist id', inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx, *, arg1=None):
        if arg1 is None:  # Then print general help
            embed = get_general_help_embed()
            await ctx.send(embed=embed)
        else:
            arg1 = str(self.bot.get_command(arg1))  # Convert aliases to full command
            help_dict = get_help_dict()
            if arg1 in help_dict:
                embed = get_help_embed(help_dict, arg1)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title='Invalid command/subcommand',
                    color=0xFFE900
                )
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))


def get_general_help_embed():
    embed = discord.Embed(
        title='Bot Commands',
        description='<> = Parameter\n'
                    '() = optional\n'
                    '/ = pick between'
    )

    utility_module = get_help_dict('utility')
    utility_fields = []
    for key, value in utility_module.items():  # Create utility text
        utility_fields.append(f"**- {value['title']}**\n"
                              f"{value['description']}")
    utility_text = '\n'.join(utility_fields)

    reactions_module = get_help_dict('reactions')
    reactions_fields = []
    for key, value in reactions_module.items():  # Create reactions text
        reactions_fields.append(f"**- {value['title']}**\n"
                                f"{value['description']}")
    reactions_text = '\n'.join(reactions_fields)

    embed.add_field(name='\\> Utility', value=utility_text, inline=True)
    embed.add_field(name='\\> Reactions', value=reactions_text, inline=True)
    return embed


def get_help_embed(help_dict, arg):
    value = help_dict[arg]
    embed = discord.Embed(
        title=value['title'],
        description=f"{value['description']}\n\n"
                    f"**Example:** {value['example']}\n"
                    f"**Aliases:** {value['alias'] if value['alias'] else 'None'}"
    )
    return embed


def get_help_dict(module=None):
    # <> = parameter value
    # () = optional
    # / = either or
    utility = {
        'help':
            {
                'title': 'help (<command or subcommand>)',
                'description': 'Displays general command info; or specific info if command is supplied',
                'example': 'help addlog set',
                'alias': []
            },
        'alias':
            {
                'title': 'alias',
                'description': 'Displays command/subcommand aliases',
                'example': 'alias',
                'alias': []
            },
        'ping':
            {
                'title': 'ping',
                'description': 'Pong! Pings the bot',
                'example': 'ping',
                'alias': []
            },
    }
    reactions = {
        'status':
            {
                'title': 'status',
                'description': 'Shows current reaction log settings',
                'example': 'status',
                'alias': ['s']
            },
        'addlog':
            {
                'title': 'addlog (set/on/off/clear)',
                'description': 'Shows add log help/settings; or manages add log',
                'example': 'addlog',
                'alias': ['add', 'a']
            },
        'removelog':
            {
                'title': 'removelog (set/on/off/clear)',
                'description': 'Shows remove log help/settings; or manages remove log',
                'example': 'removelog',
                'alias': ['remove', 'r']
            },
        'blacklist':
            {
                'title': 'blacklist (add/remove/clear/list/listid)',
                'description': 'Shows blacklist (reaction log ignore list) help/settings; or manages blacklist',
                'example': 'blacklist',
                'alias': []
            },
    }
    # Subcommands --------------------------------
    addlog = {
        'addlog set':
            {
                'title': 'addlog set <channel id/mention>',
                'description': 'Sets the add log to the given channel; takes ID or mention',
                'example': 'addlog set #reaction-log',
                'alias': ['s']
            },
        'addlog on':
            {
                'title': 'addlog on',
                'description': 'Enables add log',
                'example': 'addlog on',
                'alias': []
            },
        'addlog off':
            {
                'title': 'addlog off',
                'description': 'Disables add log',
                'example': 'addlog off',
                'alias': []
            },
        'addlog clear':
            {
                'title': 'addlog clear',
                'description': 'Removes channel set to add log',
                'example': 'addlog clear',
                'alias': []
            },
    }
    removelog = {
        'removelog set':
            {
                'title': 'removelog set <channel id/mention>',
                'description': 'Sets the remove log to the given channel; takes ID or mention',
                'example': 'removelog set #reaction-log',
                'alias': ['s']
            },
        'removelog on':
            {
                'title': 'removelog on',
                'description': 'Enables remove log',
                'example': 'removelog on',
                'alias': []
            },
        'removelog off':
            {
                'title': 'removelog off',
                'description': 'Disables remove log',
                'example': 'removelog off',
                'alias': []
            },
        'removelog clear':
            {
                'title': 'removelog clear',
                'description': 'Removes channel set to remove log',
                'example': 'removelog clear',
                'alias': []
            },
    }
    blacklist = {
        'blacklist add':
            {
                'title': 'blacklist add <user ID/mention>',
                'description': 'Adds user to reaction log ignore list; takes ID or mention',
                'example': 'blacklist add @Somebody',
                'alias': ['a']
            },
        'blacklist remove':
            {
                'title': 'blacklist remove <user ID/mention>',
                'description': 'Removes user from reaction log ignore list; takes ID or mention',
                'example': 'blacklist remove @Somebody',
                'alias': ['r']
            },
        'blacklist list':
            {
                'title': 'blacklist list',
                'description': 'Displays reaction log ignore list via embed mentions',
                'example': 'blacklist list',
                'alias': ['l']
            },
        'blacklist listid':
            {
                'title': 'blacklist listid',
                'description': 'Displays reaction log ignore list via user IDs',
                'example': 'blacklist listid',
                'alias': ['id']
            },
        'blacklist clear':
            {
                'title': 'blacklist clear',
                'description': 'Clears the reaction log ignore list',
                'example': 'blacklist clear',
                'alias': []
            },
    }
    locals_copy = locals()
    if module:  # If a specific module has been given
        return locals_copy[module]  # Return that specific dictionary
    else:  # No module specified, return dict of all commands
        full_help_dict = {}
        for symbol in locals_copy:  # Combine all the dictionaries in the function scope
            obj = locals_copy[symbol]  # Object associated to the symbol
            if isinstance(obj, dict):  # If it's a dictionary, append it in
                full_help_dict.update(obj)
        return full_help_dict
