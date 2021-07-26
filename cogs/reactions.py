import discord
from discord.ext import commands
import os  # To check if config.json exists already
import json  # For config.json
import aiohttp  # API doesn't properly work with the removal of animated emojis
import asyncio  # For confirmation prompt timeout exception

# Will not be able to discern whether to display a removed reaction emoji as a png or gif, so use web request to check

# Embed color palette:
#
# Reaction added: 0x00AD25
# Reaction removed: 0xEF1C1C
# Set/enable: 0x60FF7D
# Unset/disable: 0xFF5959
# Error: 0xFFE900

if not os.path.isfile('config.json'):  # If config doesn't exist, create a fresh one
    print('config does not exist, generating')
    with open('config.json', 'w') as config_json:
        template_config = {
            'add_reaction_log_enabled': True,
            'add_reaction_log_id': None,
            'remove_reaction_log_enabled': True,
            'remove_reaction_log_id': None,
            'blacklist_enabled': True,
            'ignored_users': [],  # Using list instead of set due to JSON serialization. Could make custom encoding
            # for theoretical better performance
            'ignored_roles': [],
            'stat_tracking_enabled': True,
            'reactions_added': 0,
            'reactions_removed': 0,
        }
        json.dump(template_config, config_json, indent=4)

with open('config.json') as config_json:  # Load data from config
    try:
        config_data = json.load(config_json)
    except (json.JSONDecodeError, KeyError):
        print('config.json could not be read, aborting launch')
        input()  # Pause before closing
        quit()


def save():  # Save to file
    with open('config.json', 'w') as file:
        json.dump(config_data, file, indent=4)


class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if config_data['stat_tracking_enabled']:
            config_data['reactions_added'] += 1
            save()
        if not config_data['add_reaction_log_enabled']:
            # print('Reaction add log has been disabled, ignoring event')
            return
        add_log_channel = self.bot.get_channel(config_data['add_reaction_log_id'])
        if not add_log_channel:
            if config_data['add_reaction_log_id'] is None:
                print("[ERROR] Add log has not been set, ignoring reaction event\n"
                      ">>> You can set the log with '.addlog <channel id/mention>', or manually in config.json\n"
                      ">>> If done manually; replace 'None' with the channel id, "
                      "and make sure you leave the comma after")
            else:
                print('ERROR: Invalid add log channel id')
            return

        server = self.bot.get_guild(payload.guild_id)
        user = server.get_member(payload.user_id)
        if config_data['blacklist_enabled']:
            ignored_roles_set = set(config_data['ignored_roles'])
            member_roles_set = {x.id for x in user.roles}
            if not member_roles_set.isdisjoint(ignored_roles_set):  # Check if sets have any mutual values
                # print(f'{user} has a blacklisted role, ignoring event')
                return
            if user.id in config_data['ignored_users']:
                # print(f'{user} is blacklisted, ignoring event')
                return
        message_link = f'https://discord.com/channels/{payload.guild_id}/{payload.channel_id}/{payload.message_id}'
        emoji = payload.emoji

        embed = discord.Embed(
            title=f'Reaction Added',
            description=f'{emoji}',
            color=0x00AD25
        )

        if emoji.is_custom_emoji():
            embed.set_thumbnail(url=emoji.url)

        embed.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.avatar_url)
        embed.add_field(name=f'By', value=f'{user.mention}')
        embed.add_field(name=f'In channel', value=f'<#{payload.channel_id}>', inline=True)
        embed.add_field(name='Message link', value=f'[Jump to message!]({message_link})', inline=False)
        await add_log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if config_data['stat_tracking_enabled']:
            config_data['reactions_removed'] += 1
            save()
        if not config_data['remove_reaction_log_enabled']:
            # print('Reaction remove log has been disabled, ignoring event')
            return
        remove_log_channel = self.bot.get_channel(config_data['remove_reaction_log_id'])
        if not remove_log_channel:
            if config_data['remove_reaction_log_id'] is None:
                print("[ERROR] Remove log has not been set, ignoring reaction event\n"
                      ">>> You can set the log with '.removelog <channel id/mention>', or manually in config.json\n"
                      ">>> If done manually; replace 'None' with the channel id, "
                      "and make sure you leave the comma after")
            else:
                print('ERROR: Invalid reaction remove channel id')
            return

        server = self.bot.get_guild(payload.guild_id)
        user = server.get_member(payload.user_id)
        if config_data['blacklist_enabled']:
            ignored_roles_set = set(config_data['ignored_roles'])
            member_roles_set = {x.id for x in user.roles}
            if not member_roles_set.isdisjoint(ignored_roles_set):  # Check if sets have any mutual values
                # print(f'{user} has a blacklisted role, ignoring event')
                return
            if user.id in config_data['ignored_users']:
                # print(f'{user} is blacklisted, ignoring event')
                return
        message_link = f'https://discord.com/channels/{payload.guild_id}/{payload.channel_id}/{payload.message_id}'
        emoji = payload.emoji

        embed = discord.Embed(
            title=f'Reaction Deleted',
            description=f'{emoji}',
            color=0xEF1C1C
        )

        if emoji.is_custom_emoji():
            emoji_url = str(emoji.url)[:-3] + 'gif'
            async with aiohttp.ClientSession() as session:
                async with session.get(emoji_url) as request:
                    if request.status == 200:
                        embed.set_thumbnail(url=emoji_url)
                    else:
                        embed.set_thumbnail(url=emoji.url)

        embed.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.avatar_url)
        embed.add_field(name=f'By', value=f'{user.mention}')
        embed.add_field(name=f'In channel', value=f'<#{payload.channel_id}>', inline=True)
        embed.add_field(name='Message link', value=f'[Jump to message!]({message_link})', inline=False)
        await remove_log_channel.send(embed=embed)

    @commands.group(aliases=['a', 'add'], invoke_without_command=True)
    async def addlog(self, ctx):
        status = 'ON' if config_data['add_reaction_log_enabled'] else 'OFF'  # Status string
        log_id = config_data['add_reaction_log_id']
        if log_id is None:  # Not set yet
            log_text = '**Not set**'
        else:
            log_channel = self.bot.get_channel(log_id)
            log_text = f'<#{log_id}>' if log_channel else '**(Invalid channel)**'
        embed = discord.Embed(
            description=f'(Add log is currently **{status}**)\n'
                        f'(Add log is set to: {log_text})\n\n'
                        f'**Usage:**\n'
                        f'.addlog set <channel id/mention>\n'
                        f'.addlog on\n'
                        f'.addlog off'
        )
        await ctx.send(embed=embed)

    @addlog.command(name='set', aliases=['s'])
    async def addlog_set(self, ctx, channel: discord.TextChannel):  # Valid channel enforced already
        log_id = config_data['add_reaction_log_id']
        if channel.id == log_id:
            embed = discord.Embed(
                title='Add log is already set to that channel',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['add_reaction_log_id'] = channel.id
        save()  # Save changes to file
        embed = discord.Embed(
            description=f'Successfully set add log to {channel.mention}',
            color=0x60FF7D
        )
        await ctx.send(embed=embed)

    @addlog.command(name='on')
    async def addlog_on(self, ctx):
        enabled = config_data['add_reaction_log_enabled']
        if enabled:  # If it's already on
            embed = discord.Embed(
                title='Add log is already on',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['add_reaction_log_enabled'] = True
        save()  # Save changes to file
        embed = discord.Embed(
            description='**Enabled** add log',
            color=0x60FF7D
        )
        await ctx.send(embed=embed)

    @addlog.command(name='off')
    async def addlog_off(self, ctx):
        enabled = config_data['add_reaction_log_enabled']
        if not enabled:  # If it's already off
            embed = discord.Embed(
                title='Add log is already off',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['add_reaction_log_enabled'] = False
        save()  # Save changes to file
        embed = discord.Embed(
            description='**Disabled** add log',
            color=0xFF5959
        )
        await ctx.send(embed=embed)

    @addlog.command(name='clear')
    async def addlog_clear(self, ctx):
        log_id = config_data['add_reaction_log_id']
        if log_id is None:
            embed = discord.Embed(
                title='Add log is already unset',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['add_reaction_log_id'] = None
        save()  # Save changes to file
        embed = discord.Embed(
            description='**Unset add log**',
            color=0xFF5959
        )
        await ctx.send(embed=embed)

    @commands.group(aliases=['r', 'remove'], invoke_without_command=True)
    async def removelog(self, ctx):
        status = 'ON' if config_data['remove_reaction_log_enabled'] else 'OFF'  # Status string
        log_id = config_data['remove_reaction_log_id']
        if log_id is None:  # Not set yet
            log_text = '**Not set**'
        else:
            log_channel = self.bot.get_channel(log_id)
            log_text = f'<#{log_id}>' if log_channel else '**(Invalid channel)**'
        embed = discord.Embed(
            description=f'(Remove log is currently **{status}**)\n'
                        f'(Remove log is set to: {log_text})\n\n'
                        f'**Usage:**\n'
                        f'.removelog set <channel id/mention>\n'
                        f'.removelog on\n'
                        f'.removelog off'
        )
        await ctx.send(embed=embed)

    @removelog.command(name='set', aliases=['s'])
    async def removelog_set(self, ctx, channel: discord.TextChannel):  # Valid channel enforced already
        log_id = config_data['remove_reaction_log_id']
        if channel.id == log_id:
            embed = discord.Embed(
                title='Remove log is already set to that channel',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['remove_reaction_log_id'] = channel.id
        save()  # Save changes to file
        embed = discord.Embed(
            description=f'Successfully set remove log to {channel.mention}',
            color=0x60FF7D
        )
        await ctx.send(embed=embed)

    @removelog.command(name='on')
    async def removelog_on(self, ctx):
        enabled = config_data['remove_reaction_log_enabled']
        if enabled:  # If it's already on
            embed = discord.Embed(
                title='Remove log is already on',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['remove_reaction_log_enabled'] = True
        save()  # Save changes to file
        embed = discord.Embed(
            description='**Enabled** remove log',
            color=0x60FF7D
        )
        await ctx.send(embed=embed)

    @removelog.command(name='off')
    async def removelog_off(self, ctx):
        enabled = config_data['remove_reaction_log_enabled']
        if not enabled:  # If it's already off
            embed = discord.Embed(
                title='Remove log is already off',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['remove_reaction_log_enabled'] = False
        save()  # Save changes to file
        embed = discord.Embed(
            description='**Disabled** remove log',
            color=0xFF5959
        )
        await ctx.send(embed=embed)

    @removelog.command(name='clear')
    async def removelog_clear(self, ctx):
        log_id = config_data['remove_reaction_log_id']
        if log_id is None:
            embed = discord.Embed(
                title='Remove log is already unset',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['remove_reaction_log_id'] = None
        save()  # Save changes to file
        embed = discord.Embed(
            description='**Unset remove log**',
            color=0xFF5959
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['s'])
    async def status(self, ctx):
        # Get add log statuses
        addlog_status = 'ON' if config_data['add_reaction_log_enabled'] else 'OFF'  # Status string
        addlog_id = config_data['add_reaction_log_id']
        if addlog_id is None:  # Not set yet
            addlog_channel_text = '**Not set**'
        else:
            addlog_channel = self.bot.get_channel(addlog_id)
            addlog_channel_text = f'<#{addlog_id}>' if addlog_channel else '**(Invalid channel)**'

        # Get remove log statuses
        removelog_status = 'ON' if config_data['remove_reaction_log_enabled'] else 'OFF'  # Status string
        removelog_id = config_data['remove_reaction_log_id']
        if removelog_id is None:  # Not set yet
            removelog_channel_text = '**Not set**'
        else:
            removelog_channel = self.bot.get_channel(removelog_id)
            removelog_channel_text = f'<#{removelog_id}>' if removelog_channel else '**(Invalid channel)**'

        # Get blacklist statuses
        blacklist_status = 'ON' if config_data['blacklist_enabled'] else 'OFF'  # Status string
        blacklisted_users_length = len(config_data['ignored_users'])
        blacklisted_roles_length = len(config_data['ignored_roles'])

        # Get stats statuses
        stats_status = 'ON' if config_data['stat_tracking_enabled'] else 'OFF'  # Status string

        embed = discord.Embed(
            title='Reaction Log Status',
            description=f'Add log: **{addlog_status}**\n'
                        f'Add log channel: {addlog_channel_text}\n\n'
                        f'Remove log: **{removelog_status}**\n'
                        f'Remove log channel: {removelog_channel_text}\n\n'
                        f'Blacklist: **{blacklist_status}**\n'
                        f'Blacklisted users: **{blacklisted_users_length}**\n'
                        f'Blacklisted roles: **{blacklisted_roles_length}**\n\n'
                        f'Total reactions stats tracking: **{stats_status}**'
        )
        await ctx.send(embed=embed)

    @commands.group(aliases=['bl', 'b'], invoke_without_command=True)
    async def blacklist(self, ctx):
        status = 'ON' if config_data['blacklist_enabled'] else 'OFF'  # Status string
        blacklisted_users_length = len(config_data['ignored_users'])
        blacklisted_roles_length = len(config_data['ignored_roles'])
        embed = discord.Embed(
            description=f'(Blacklist is currently **{status}**)\n'
                        f'(Blacklisted users: **{blacklisted_users_length}**)\n'
                        f'(Blacklisted roles: **{blacklisted_roles_length}**)\n\n'
                        f'**Usage:**\n'
                        f'.blacklist add <user id/mention>\n'
                        f'.blacklist addrole <role id/mention>\n'
                        f'.blacklist remove <user id/mention>\n'
                        f'.blacklist removerole <role id/mention>\n'
                        f'.blacklist list <users/userid/roles/roleid>'
        )
        await ctx.send(embed=embed)

    @blacklist.command(name='add', aliases=['a'])
    async def blacklist_add(self, ctx, user: discord.Member):
        if user.id in config_data['ignored_users']:
            embed = discord.Embed(
                description=f'**{user.name}** is already blacklisted',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['ignored_users'].append(user.id)
        config_data['ignored_users'] = sorted(config_data['ignored_users'])  # Sort by uid
        save()  # Save changes to file
        embed = discord.Embed(
            description=f'Blacklisted **{user.name}**',
            color=0x60FF7D
        )
        await ctx.send(embed=embed)

    @blacklist.command(name='remove', aliases=['r'])
    async def blacklist_remove(self, ctx, user: discord.Member):
        if user.id not in config_data['ignored_users']:
            embed = discord.Embed(
                description=f'**{user.name}** is not blacklisted',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['ignored_users'].remove(user.id)
        save()  # Save changes to file
        embed = discord.Embed(
            description=f'Removed **{user.name}** from blacklist',
            color=0xFF5959
        )
        await ctx.send(embed=embed)

    @blacklist.command(name='addrole', aliases=['ar'])
    async def blacklist_addrole(self, ctx, role: discord.Role):
        if role.id in config_data['ignored_roles']:
            embed = discord.Embed(
                description=f'<@&{role.id}> is already blacklisted',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['ignored_roles'].append(role.id)
        config_data['ignored_roles'] = sorted(config_data['ignored_roles'])  # Sort by role id
        save()  # Save changes to file
        embed = discord.Embed(
            description=f'Blacklisted <@&{role.id}>',
            color=0x60FF7D
        )
        await ctx.send(embed=embed)

    @blacklist.command(name='removerole', aliases=['rr'])
    async def blacklist_removerole(self, ctx, role: discord.Role):
        if role.id not in config_data['ignored_roles']:
            embed = discord.Embed(
                description=f'<@&{role.id}> is not blacklisted',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['ignored_roles'].remove(role.id)
        save()  # Save changes to file
        embed = discord.Embed(
            description=f'Removed <@&{role.id}> from blacklist',
            color=0xFF5959
        )
        await ctx.send(embed=embed)

    @blacklist.group(name='list', aliases=['l'], invoke_without_command=True)
    async def blacklist_list(self, ctx):
        embed = discord.Embed(  # This code is only reached if no valid subcommand was given
            description=f'**Valid lists:** users, userid, roles, roleid',
            color=0xFFE900
        )
        await ctx.send(embed=embed)

    @blacklist_list.command(name='users', aliases=['user', 'u'])
    async def blacklist_list_users(self, ctx):
        blacklist_mentions = [f'<@{x}>' for x in config_data['ignored_users']]
        title = 'Blacklisted Users' if blacklist_mentions else 'There are no blacklisted users'
        embed = discord.Embed(
            title=title,
            description='\n'.join(blacklist_mentions)
        )
        await ctx.send(embed=embed)

    @blacklist_list.command(name='userid', aliases=['uid'])
    async def blacklist_list_userid(self, ctx):
        blacklist_ids = [str(x) for x in config_data['ignored_users']]
        title = 'Blacklisted Users (ID)' if blacklist_ids else 'There are no blacklisted users'
        embed = discord.Embed(
            title=title,
            description='\n'.join(blacklist_ids)
        )
        await ctx.send(embed=embed)

    @blacklist_list.command(name='roles', aliases=['role', 'r'])
    async def blacklist_list_roles(self, ctx):
        blacklist_roles = [f'<@&{x}>' for x in config_data['ignored_roles']]
        title = 'Blacklisted Roles' if blacklist_roles else 'There are no blacklisted roles'
        embed = discord.Embed(
            title=title,
            description='\n'.join(blacklist_roles)
        )
        await ctx.send(embed=embed)

    @blacklist_list.command(name='roleid', aliases=['rid'])
    async def blacklist_list_roleid(self, ctx):
        blacklist_roleids = [str(x) for x in config_data['ignored_roles']]
        title = 'Blacklisted Roles (ID)' if blacklist_roleids else 'There are no blacklisted roles'
        embed = discord.Embed(
            title=title,
            description='\n'.join(blacklist_roleids)
        )
        await ctx.send(embed=embed)

    @blacklist.command(name='on')
    async def blacklist_on(self, ctx):
        enabled = config_data['blacklist_enabled']
        if enabled:  # If it's already on
            embed = discord.Embed(
                title='Blacklist is already on',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['blacklist_enabled'] = True
        save()  # Save changes to file
        embed = discord.Embed(
            description='**Enabled** blacklist',
            color=0x60FF7D
        )
        await ctx.send(embed=embed)

    @blacklist.command(name='off')
    async def blacklist_off(self, ctx):
        enabled = config_data['blacklist_enabled']
        if not enabled:  # If it's already off
            embed = discord.Embed(
                title='Blacklist is already off',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['blacklist_enabled'] = False
        save()  # Save changes to file
        embed = discord.Embed(
            description='**Disabled** blacklist',
            color=0xFF5959
        )
        await ctx.send(embed=embed)

    @blacklist.group(name='clear', invoke_without_command=True)
    async def blacklist_clear(self, ctx):
        embed = discord.Embed(  # This code is only reached if no valid subcommand was given
            description=f'**Valid arguments:** users, roles, all',
            color=0xFFE900
        )
        await ctx.send(embed=embed)

    @blacklist_clear.command(name='users', aliases=['user', 'u'])
    async def blacklist_clear_users(self, ctx):
        if not config_data['ignored_users']:  # It's already empty
            embed = discord.Embed(
                description='User blacklist is already empty',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['ignored_users'].clear()
        save()  # Save changes to file
        embed = discord.Embed(
            description=f'Cleared user blacklist',
            color=0xFF5959
        )
        await ctx.send(embed=embed)

    @blacklist_clear.command(name='roles', aliases=['role', 'r'])
    async def blacklist_clear_roles(self, ctx):
        if not config_data['ignored_roles']:  # It's already empty
            embed = discord.Embed(
                description='Role blacklist is already empty',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['ignored_roles'].clear()
        save()  # Save changes to file
        embed = discord.Embed(
            description=f'Cleared role blacklist',
            color=0xFF5959
        )
        await ctx.send(embed=embed)

    @blacklist_clear.command(name='all')
    async def blacklist_clear_all(self, ctx):
        ignored_users_empty = False if config_data['ignored_users'] else True
        ignored_roles_empty = False if config_data['ignored_roles'] else True
        if ignored_users_empty and ignored_roles_empty:
            embed = discord.Embed(
                description='Both blacklists are already empty',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        if not ignored_users_empty:
            config_data['ignored_users'].clear()
            save()  # Save changes to file
        if not ignored_roles_empty:
            config_data['ignored_roles'].clear()
            save()
        embed = discord.Embed(
            description=f'Cleared blacklists',
            color=0xFF5959
        )
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def stats(self, ctx):
        status = 'ON' if config_data['stat_tracking_enabled'] else 'OFF'  # Status string
        reactions_added = config_data['reactions_added']
        reactions_removed = config_data['reactions_removed']
        embed = discord.Embed(
            description=f'(Stat tracking is currently **{status}**)\n'
                        f'(Reactions added: **{reactions_added}**)\n'
                        f'(Reactions removed: **{reactions_removed}**)\n\n'
                        f'**Usage:**\n'
                        f'.stats\n'
                        f'.stats <on/off>\n'
                        f'.stats clear'
        )
        await ctx.send(embed=embed)

    @stats.command(name='on')
    async def stats_on(self, ctx):
        enabled = config_data['stat_tracking_enabled']
        if enabled:  # If it's already on
            embed = discord.Embed(
                title='Stat tracking is already on',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['stat_tracking_enabled'] = True
        save()  # Save changes to file
        embed = discord.Embed(
            description='**Enabled** stat tracking',
            color=0x60FF7D
        )
        await ctx.send(embed=embed)

    @stats.command(name='off')
    async def stats_off(self, ctx):
        enabled = config_data['stat_tracking_enabled']
        if not enabled:  # If it's already off
            embed = discord.Embed(
                title='Stat tracking is already off',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return
        config_data['stat_tracking_enabled'] = False
        save()  # Save changes to file
        embed = discord.Embed(
            description='**Disabled** stat tracking',
            color=0xFF5959
        )
        await ctx.send(embed=embed)

    @stats.command(name='clear')
    async def stats_clear(self, ctx):
        embed = discord.Embed(
            description=f"Reactions added: **{config_data['reactions_added']}**\n"
                        f"Reactions removed: **{config_data['reactions_removed']}**\n\n"
                        f"**WARNING: this will reset tracked total reactions stats**\n"
                        f"**Continue? (y/n)**",
            color=0x60FF7D
        )
        await ctx.send(embed=embed)

        def check(message):  # Takes message from on_message event. Event specified below (doesn't need the 'on_' part)
            return message.author == ctx.author

        # wait_for returns first event that satisfies check (message event in this case)
        try:
            response_message = await self.bot.wait_for('message', timeout=10, check=check)
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title='Prompt timed out! (10s)',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
            return

        content = response_message.content.lower()  # Lowercase for comparisons
        if content in {'yes', 'y'}:
            config_data['reactions_added'] = 0
            config_data['reactions_removed'] = 0
            save()
            embed = discord.Embed(
                description='**Reset total reactions stats**',
                color=0xFF5959
            )
            await ctx.send(embed=embed)
        elif content in {'no', 'n'}:
            embed = discord.Embed(
                title='**Cancelled**',
                color=0xFFE900
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title='Invalid response. Cancelling',
                color=0xFFE900
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Reactions(bot))
