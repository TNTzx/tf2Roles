"""Contains the cog for commands for viewing a user's available roles."""


import disnake
from disnake.ext import commands

from .. import global_vars
from .. import utils



GLOBALS = global_vars.Globals.get_globals()


class CogViewUserRoles(commands.Cog):
    """Contains all commands relating to viewing a user's roles."""

    @GLOBALS.bot.slash_command(
        description='Allows you to manage your active role, or view the roles of other users.',
        name='roles',
        guild_ids=GLOBALS.get_guild_ids()
    )
    async def roles(self, inter: disnake.UserCommandInteraction, member: disnake.Member = None, page: int = 1):
        await utils.display_roles(inter, display_type='Role', user=member, page=page)


    @GLOBALS.bot.slash_command(
        description='Allows you to manage your active role icon, or view the role icons of other users.',
        name='icons',
        guild_ids=GLOBALS.get_guild_ids()
    )
    async def roleicons(self, inter: disnake.UserCommandInteraction, member: disnake.Member = None, page: int = 1):
        await utils.display_roles(inter, display_type='Icon', user=member, page=page)
