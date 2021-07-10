import discord
from discord.ext import commands
import os
import console_interaction


bot = commands.Bot(command_prefix='.')


@bot.command()
@commands.is_owner()  # Owner-only command
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'Loaded {extension}')


@bot.command()
@commands.is_owner()  # Owner-only command
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f'Unloaded {extension}')


@bot.command()
@commands.is_owner()  # Owner-only command
async def reload(ctx, extension):
    bot.reload_extension(f'cogs.{extension}')
    await ctx.send(f'Reloaded {extension}')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

token = console_interaction.get_bot_token()
try:
    bot.run(token)
except discord.LoginFailure:
    print('Login failed. Is the token valid?')
    input()  # Pause before exiting
