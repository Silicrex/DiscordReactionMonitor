import discord
from discord.ext import commands
import console_interaction


bot = commands.Bot(command_prefix='.')
token = console_interaction.get_bot_token()
try:
    bot.run(token)
except discord.LoginFailure:
    print('Login failed. Is the token valid?')
    input()  # Pause before exiting
