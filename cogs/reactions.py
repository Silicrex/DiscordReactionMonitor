import discord
from discord.ext import commands
import os
import json


if not os.path.isfile('config.json'):  # If config doesn't exist, create a fresh one
    print('config does not exist, generating')
    with open('config.json', 'w') as file:
        template_config = {
            'add_reaction_log_id': None,
            'remove_reaction_log_id': None,
            'ignored_users': {}
        }
        json.dump(template_config, file, indent=4)


with open('config.json') as file:  # Load data from config
    try:
        config_data = json.load(file)
        add_reaction_log_id = config_data['add_reaction_log_id']
        remove_reaction_log_id = config_data['remove_reaction_log_id']
        ignored_users = config_data['ignored_users']
    except (json.JSONDecodeError, KeyError):
        print('config.json could not be read, aborting')
        input()  # Pause before closing
        quit()


class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        
def setup(bot):
    bot.add_cog(Reactions(bot))
