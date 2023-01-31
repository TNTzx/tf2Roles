"""Contains the cog for commands that can manage what roles can be assigned."""


import disnake
from disnake.ext import commands

from .. import global_vars
from .. import utils



GLOBALS = global_vars.Globals.get_globals()


class CogRoleManagement(commands.Cog):
    """Contains all commands for managing what roles can be assigned."""

    @GLOBALS.bot.slash_command(description='Assigns a role to a user.', name='giverole', guild_ids=GLOBALS.get_guild_ids())
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, inter: disnake.UserCommandInteraction, member: disnake.Member, role: disnake.Role):
        roles_to_add = [role.id]
        if role.name == '@everyone':
            await inter.response.send_message(
                utils.getLang(inter, section='Translation', line='GIVE_ROLE_FAILED_EVERYONE'),
                ephemeral=True
            )
            return

        bl_role, _ = utils.get_user_roles(9)
        if role.id in bl_role:
            await inter.response.send_message(
                utils.getLang(inter, section='Translation', line='GIVE_ROLE_FAILED_BLACKLIST'),
                ephemeral=True
            )
            return

        user_roles, _ = utils.get_user_roles(member.id)
        if role.id in user_roles:
            await inter.response.send_message(
                utils.getLang(
                    inter, section='Translation', line='GIVE_ROLE_FAILED_EXISTS'
                ).format(member.mention, role.mention),
                ephemeral=True
            )
            return

        await inter.response.send_message(
            utils.getLang(inter, section='Translation', line='GIVE_ROLE_SUCCESS').format(member.mention, role.mention)
        )

        # TODO should change this algorithm
        for role_to_add in roles_to_add:
            for master_role in GLOBALS.masterRoles:
                primary, secondary = master_role
                if primary == role_to_add:
                    roles_to_add.append(secondary)

        for role_to_add in roles_to_add:
            utils.database_update("add", user=member.id, role=role_to_add)


    @GLOBALS.bot.slash_command(description='Removes a role from a user.', name='removerole', guild_ids=GLOBALS.get_guild_ids())
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, inter: disnake.UserCommandInteraction, member: disnake.Member, role: disnake.Role):
        if role.name == '@everyone':
            await inter.response.send_message(
                utils.getLang(inter, section='Translation', line='REMOVE_ROLE_FAILED_EVERYONE'),
                ephemeral=True
            )
            return

        user_roles, _ = utils.get_user_roles(member.id)
        if role.id not in user_roles:
            await inter.response.send_message(
                utils.getLang(
                    inter, section='Translation', line='REMOVE_ROLE_FAILED_MISSING'
                ).format(member.mention, role.mention),
                ephemeral=True
            )
            return

        if inter.locale == 'ko':
            message_str = utils.getLang(inter, section='Translation', line='REMOVE_ROLE_SUCCESS').format(member.mention, role.mention)
        else:
            message_str = utils.getLang(inter, section='Translation', line='REMOVE_ROLE_SUCCESS').format(role.mention, member.mention)
        await inter.response.send_message(message_str)
        utils.database_update("remove", user=member.id, role=role.id)
        await member.remove_roles(role, reason=f'Role removed by {inter.author} ({inter.author.id})')


    @GLOBALS.bot.slash_command(description='Gives an icon to a user.', name='giveicon', guild_ids=GLOBALS.get_guild_ids())
    @commands.has_permissions(manage_roles=True)
    async def addroleicon(self, inter: disnake.UserCommandInteraction, member: disnake.Member, role: disnake.Role):
        if role.name == '@everyone':
            await inter.response.send_message(
                utils.getLang(inter, section='Translation', line='GIVE_ROLE_FAILED_EVERYONE'),
                ephemeral=True
            )
            return

        _, bl_role = utils.get_user_roles(9)
        if role.id in bl_role:
            await inter.response.send_message(
                utils.getLang(inter, section='Translation', line='GIVE_ROLE_FAILED_BLACKLIST'),
                ephemeral=True
            )
            return

        _, user_icons = utils.get_user_roles(member.id)
        if role.id in user_icons:
            await inter.response.send_message(
                utils.getLang(
                    inter, section='Translation', line='GIVE_ROLE_FAILED_EXISTS'
                ).format(member.mention, role.mention),
                ephemeral=True
            )
            return

        await inter.response.send_message(
            utils.getLang(inter, section='Translation', line='GIVE_ICON_SUCCESS').format(member.mention, role.mention)
        )
        utils.database_update("add", user=member.id, roleIcon=role.id)


    @GLOBALS.bot.slash_command(description='Removes an icon from a user.', name='removeicon', guild_ids=GLOBALS.get_guild_ids())
    @commands.has_permissions(manage_roles=True)
    async def removeroleicon(self, inter: disnake.UserCommandInteraction, member: disnake.Member, role: disnake.Role):
        if role.name == '@everyone':
            await inter.response.send_message(
                utils.getLang(inter, section='Translation', line=f'REMOVE_ROLE_FAILED_EVERYONE'),
                ephemeral=True
            )
            return

        _, user_icons = utils.get_user_roles(member.id)
        if role.id not in user_icons:
            await inter.response.send_message(
                utils.getLang(
                    inter, section='Translation', line=f'REMOVE_ROLE_FAILED_MISSING'
                ).format(member.mention, role.mention),
                ephemeral=True
            )
            return

        if inter.locale == 'ko':
            message_str = utils.getLang(inter, section='Translation', line='REMOVE_ROLE_SUCCESS').format(member.mention, role.mention)
        else:
            message_str = utils.getLang(inter, section='Translation', line='REMOVE_ROLE_SUCCESS').format(role.mention, member.mention)
        await inter.response.send_message(message_str)
        utils.database_update("remove", user=member.id, roleIcon=role.id)
        await member.remove_roles(role, reason=f'Role removed by {inter.author} ({inter.author.id})')
