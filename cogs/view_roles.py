"""Contains the cog for viewing roles."""


import disnake
from disnake.ext import commands

from .. import global_vars



global_vars = global_vars.Globals.get_globals()


class CogViewRole(commands.Cog):
    """Contains all commands relating to viewing roles."""

    @global_vars.bot.user_command(name='View Roles', guild_ids=global_vars.guilds)
    async def view_role_context(self, inter: disnake.UserCommandInteraction):
        await _roles(inter, type = 'Role', user = inter.target)


    @global_vars.bot.user_command(name='View Role Icons', guild_ids=global_vars.guilds)
    async def view_roleicon_context(self, inter):
        await _roles(inter, type='Icon', user=inter.target)
