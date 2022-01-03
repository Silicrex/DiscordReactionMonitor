import discord
from discord.ext import commands
import os
import console_interaction

# Process of adding new commands:
# 1. Create in cog
# 2. Document in utility.py
# 3. Document aliases in utility.py alias command
# Can alternatively go by discord.py's built-in commands for description/aliases/etc.


intents = discord.Intents.default()  # For API permissions
intents.members = True
bot = commands.Bot(command_prefix='.', case_insensitive=True, intents=intents, help_command=None)


@bot.check
async def globally_block_dms(ctx):  # Bot should not be usable in DMs
    if ctx.guild is None:
        raise commands.NoPrivateMessage
    else:
        return True


# @bot.check
# async def require_manage_guild(ctx):  # All commands require Manage Server permission
#     if not ctx.author.guild_permissions.manage_guild:
#         raise commands.MissingPermissions(['manage_guild'])
#     else:
#         return True


@bot.command()
@commands.is_owner()  # Owner-only command
async def load(ctx, extension):  # Loading a cog from a Python file; input is file name without file extension
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'Loaded {extension}')


@bot.command()
@commands.is_owner()  # Owner-only command
async def unload(ctx, extension):  # Unloading a cog from a Python file; input is file name without file extension
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f'Unloaded {extension}')


@bot.command()
@commands.is_owner()  # Owner-only command
async def reload(ctx, extension):  # Reloading a cog from a Python file; easy update without restarting
    bot.reload_extension(f'cogs.{extension}')
    await ctx.send(f'Reloaded {extension}')


for filename in os.listdir('./cogs'):  # Load all cogs
    if filename.endswith('.py') and not filename.startswith('_'):  # If file starts with _ then ignore
        bot.load_extension(f'cogs.{filename[:-3]}')  # File extension not needed, remove ".py"

token = console_interaction.get_bot_token()  # Load bot token

try:
    bot.run(token)
except discord.LoginFailure:
    print('Login failed. Is the token valid?', end='\n\n')
    if console_interaction.get_console_confirmation('Should I overwrite the token?'):
        print()  # Newline
        console_interaction.write_token()
        print('Token updated. Restart application to retry')
        input()  # Pause to show message
    else:
        quit()
