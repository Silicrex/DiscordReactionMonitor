import discord
from discord.ext import commands
import os
import console_interaction


bot = commands.Bot(command_prefix='.')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

token = console_interaction.get_bot_token()
try:
    bot.run(token)
except discord.LoginFailure:
    print('Login failed. Is the token valid?')
    input()  # Pause before exiting
