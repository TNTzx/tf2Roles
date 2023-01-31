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
