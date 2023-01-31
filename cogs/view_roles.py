"""Contains the cog for commands for viewing roles."""


import disnake
from disnake.ext import commands

from .. import global_vars
from .. import utils



GLOBALS = global_vars.Globals.get_globals()


class CogViewRoleGeneral(commands.Cog):
    """Contains all commands relating to viewing roles."""

    @GLOBALS.bot.user_command(name='View Roles', guild_ids=GLOBALS.guilds)
    async def view_role_context(self, inter: disnake.UserCommandInteraction):
        await utils.display_roles(inter, display_type = utils.DisplayTypes.ROLE, user = inter.target)


    @GLOBALS.bot.user_command(name='View Role Icons', guild_ids=GLOBALS.guilds)
    async def view_roleicon_context(self, inter):
        await utils.display_roles(inter, display_type = utils.DisplayTypes.ROLE_ICON, user = inter.target)


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
