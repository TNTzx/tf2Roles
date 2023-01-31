import json
import sqlite3
import random

import disnake
from disnake.ext import commands



@bot.slash_command(description='Shows All Role Assignments', name='listroles', guild_ids=guilds)
@commands.has_permissions(manage_roles=True)
async def listall(inter, role: disnake.Role = None):
    if role:
        return await list_specific_role(inter, role)

    await inter.response.defer()

    conn = sqlite3.connect('roles.db')
    cur = conn.cursor()

    sql = '''SELECT * FROM roles'''
    cur.execute(sql)

    items = cur.fetchall()
    allRoles = []
    allIcons = []
    user_count = 0

    sql2 = '''SELECT COUNT(*) FROM roles'''
    cur.execute(sql2)
    user_total, = cur.fetchone()
    
    guild_member_ids = [member.id for member in inter.guild.members]

    for i in items:
        user, temp1, temp2 = i
        if user in guild_member_ids:
            temp1 = json.loads(temp1)
            temp2 = json.loads(temp2)
            for t1 in temp1:
                allRoles.append(t1)
            for t2 in temp2:
                allIcons.append(t2)
            user_count += 1

    roleCount = {}
    iconCount = {}

    for rl in allRoles:
        if rl not in roleCount:
            roleCount[rl] = 0
        roleCount[rl] += 1

    for ri in allIcons:
        if ri not in iconCount:
            iconCount[ri] = 0
        iconCount[ri] += 1

    roleCount = sorted(roleCount.items(), key=lambda x: [x[1], inter.guild.get_role(x[0])], reverse=True)
    iconCount = sorted(iconCount.items(), key=lambda x: [x[1], inter.guild.get_role(x[0])], reverse=True)

    color = 0x000000
    color2 = 0x000000

    roleStr = ''
    roleIconStr = ''
    roleClr = False
    for i in roleCount:
        temprole = inter.guild.get_role(i[0])
        roleStr = f'{roleStr}\n{temprole.mention}: **{i[1]}**'
        if not roleClr:
            color = temprole.color
            roleClr = True

    roleClr = False

    for i in iconCount:
        temprole = inter.guild.get_role(i[0])
        roleIconStr = f'{roleIconStr}\n{inter.guild.get_role(i[0]).mention}: **{i[1]}**'
        if not roleClr:
            color2 = temprole.color
            roleClr = True

    embed = disnake.Embed(title=getLang(inter, 'Translation', 'LIST_ALL_ROLES'), description=roleStr)
    embed.color = color
    embed.set_footer(text=getLang(inter, 'Translation', 'LIST_ALL_ROLES_FOOTER'))
    embed2 = disnake.Embed(title=getLang(inter, 'Translation', 'LIST_ALL_ICONS'), description=roleIconStr)
    embed2.color = color2
    embed2.set_footer(text=getLang(inter, 'Translation', 'LIST_ALL_ICONS_FOOTER').format(user_count, user_total))

    await inter.edit_original_message(embeds=[embed, embed2])


@bot.slash_command(name='store', description='Stores all your eligible roles & icons in your Roler Mobster Inventory')
@commands.cooldown(1, 86400, commands.BucketType.user)
async def store(inter):
    await dongulate(inter, user=inter.author)


@bot.slash_command(name='dongulate', description='Adds all valid roles to a user.', guild_ids=guilds)
@commands.has_permissions(manage_roles=True)
async def dongulate(inter, user: disnake.User):
    await inter.response.defer()
    roleIDs, roleIconIDs = get_user_roles(0)
    roles_to_add = []
    roleIcons_to_add = []

    addedRoles = []

    userRoles = user.roles

    dupeRole = None

    for r in userRoles:

        if r.id == 538179836531834906:
            dupeRole = r
            r = inter.guild.get_role(538496816845553704)
        for i in masterRoles:
            pri, sec = i
            if pri == r.id:
                print(pri, sec)
                role = inter.guild.get_role(sec)
                if role not in userRoles:
                    userRoles.append(role)

        if r.id in roleIDs:
            roles_to_add.append(r)
            addedRoles.append(r.id)
            database_update('add', user.id, role=r.id)
        if r.id in roleIconIDs:
            roleIcons_to_add.append(r)
            database_update('add', user.id, roleIcon=r.id)

    if dupeRole:
        roles_to_add.append(dupeRole)

    await user.remove_roles(*roles_to_add[1:], reason='All valid roles added to user inventory.')
    await user.remove_roles(*roleIcons_to_add[1:], reason='All valid role icons added to user inventory.')
    await inter.edit_original_message(content=getLang(inter, 'Translation', 'DONGULATE_SUCCESS').format(user.mention))


@bot.slash_command(name='blacklist', description='Adds a role to the blacklist, forbidding it from being assigned.',
                   guild_ids=guilds)
@commands.has_permissions(manage_roles=True)
async def blacklist(inter, role: disnake.Role):
    roleIDs, roleIconIDs = get_user_roles(9)
    roleA, roleIconA = get_user_roles(0)
    if role.id in roleIDs or role.id in roleIconIDs:
        database_update('remove', 9, role=role.id)
        await inter.response.send_message(
            content=getLang(inter, 'Translation', 'BLACKLIST_REMOVE_SUCCESS').format(role.name),
            ephemeral=True)
    else:
        database_update('add', 9, role=role.id)
        await inter.response.send_message(getLang(inter, 'Translation', 'BLACKLIST_ADD_SUCCESS').format(role.name),
                                          ephemeral=True)
        if role.id in roleA:
            database_update("remove", 0, role=role.id)
        elif role.id in roleIconA:
            database_update("remove", 0, role=role.id)


@bot.slash_command(name='assignrole', description='Adds or removes a role from the Dongulatable roles.',
                   guild_ids=guilds)
@commands.has_permissions(manage_roles=True)
async def assign_role(inter, role: disnake.Role):
    roleIDs, trash = get_user_roles(0)
    bl_r, trash = get_user_roles(9)
    if role.id in bl_r:
        await inter.response.send_message(
            content=getLang(inter, 'Translation', 'DONGULATE_ASSIGN_FAILED_BLACKLIST').format(role.name),
            ephemeral=True)
        return

    if role.id in roleIDs:
        database_update('remove', 0, role=role.id)
        await inter.response.send_message(
            content=getLang(inter, 'Translation', 'DONGULATE_ASSIGN_REMOVED_SUCCESS').format(role.name),
            ephemeral=True)
    else:
        database_update('add', 0, role=role.id)
        await inter.response.send_message(
            getLang(inter, 'Translation', 'DONGULATE_ASSIGN_ADDED_SUCCESS').format(role.name), ephemeral=True)


@bot.slash_command(name='viewblacklist', description='Lists all blacklisted roles and role icons.', guild_ids=guilds)
@commands.has_permissions(manage_roles=True)
async def vw_bl(inter, page:int=1):
    user = 9
    await inter.response.defer()
    embed1 = await _roles(inter, 'Role', returnEmbed=True, user=user, page=page)
    embed2 = await _roles(inter, 'Icon', returnEmbed=True, user=user, page=page)
    await inter.edit_original_message(embeds=[embed1, embed2])


@bot.slash_command(name='show', description='Shows off your role inventory publicly!', guild_ids=guilds)
async def showoff(inter):
    await inter.response.defer()
    user = inter.author
    embed1 = await _roles(inter, 'Role', returnEmbed=True, user=user)
    embed2 = await _roles(inter, 'Icon', returnEmbed=True, user=user)
    await inter.edit_original_message(embeds=[embed1, embed2])


@bot.slash_command(name='assignicon', description='Adds or removes a role from the Dongulatable roles.',
                   guild_ids=guilds)
@commands.has_permissions(manage_roles=True)
async def assign_role_icon(inter, role: disnake.Role):
    trash, roleIconIDs = get_user_roles(0)
    bl_r, trash = get_user_roles(9)
    if role.id in bl_r:
        await inter.response.send_message(
            content=getLang(inter, 'Translation', 'DONGULATE_ASSIGN_FAILED_BLACKLIST').format(role.name),
            ephemeral=True)
        return
    if role.id in roleIconIDs:
        database_update('remove', 0, roleIcon=role.id)
        await inter.response.send_message(
            content=getLang(inter, 'Translation', 'DONGULATE_ASSIGN_REMOVED_SUCCESS_ICON').format(role.name),
            ephemeral=True)
    else:
        database_update('add', 0, roleIcon=role.id)
        await inter.response.send_message(
            getLang(inter, 'Translation', 'DONGULATE_ASSIGN_ADDED_SUCCESS_ICON').format(role.name), ephemeral=True)


@bot.listen("on_dropdown")
async def on_role_select(inter):
    await inter.response.defer(ephemeral=True)
    if inter.data.custom_id == 'role_select':
        raw_id = inter.data.values[0]
        role_id = int(raw_id[3:])
        type = raw_id[:2]

        if type == 'ro':
            type = 'role'
        else:
            type = 'roleIcon'

        role = inter.guild.get_role(role_id)
        member = inter.author
        memberRoleIDs = [role.id for role in member.roles]

        roleList = []

        roleIDs, roleIconIDs = get_user_roles(member.id)
        true_roles = []

        if type == 'role':
            true_roles = roleIDs
        else:
            true_roles = roleIconIDs

    for r in true_roles:
        if r in memberRoleIDs:
            roleList.append(inter.guild.get_role(r))

    if role_id != default_role and role in roleList:
        try:
            roleList.remove(role)
        except Exception as e:
            await inter.send(embed=disnake.Embed(
                title=getLang(inter, 'Translation', 'EQUIP_ROLE_FAILED_BAD_ROLE_TITLE').format(role.name),
                description=getLang(inter, 'Translation', 'EQUIP_ROLE_FAILED_BAD_ROLE'),
                color=0x0e0e0e), ephemeral=True)
            return

    try:
        await member.add_roles(role, reason=f'Role Assignment by {member.name}')
    except disnake.Forbidden as e:
        await inter.response.send_message(
            getLang(inter, 'Translation', 'EQUIP_ROLE_FAILED_ERROR_GENERIC'),
            ephemeral=True)
        return

    try:
        await member.remove_roles(*roleList, reason=f'Role Assignment by {member.name}')
    except disnake.Forbidden as e:
        await inter.followup.send(
            getLang(inter, 'Translation', 'REMOVE_ROLE_FAILED_ERROR_GENERIC'),
            ephemeral=True)
        return

    if role_id != default_role:
        embed = disnake.Embed(title='Role Selected',
                              description=getLang(inter, 'Translation', 'EQUIP_ROLE_SUCCESS').format(role.mention),
                              color=role.color)
    else:
        embed = disnake.Embed(title='Icon Removed',
                              description=getLang(inter, 'Translation', 'ICON_REMOVE_SUCCESS').format(role.mention),
                              color=role.color)
    await inter.followup.send(embed=embed, ephemeral=True)


@bot.slash_command(name='equipall',
                   description='Equips all of your roles at once. (If you have a lot of roles, this may take some time!)',
                   guilds_ids=guilds)
async def equipall(inter):
    await inter.response.defer(ephemeral=True)
    roles, icons = get_user_roles(inter.author.id)
    all_roles = roles + icons
    role_list = []

    for r in all_roles:
        if r not in [role.id for role in inter.author.roles]:
            role_list.append(inter.guild.get_role(r))
    try:
        await inter.author.add_roles(*role_list)
        await inter.edit_original_message(
            content=getLang(inter, 'Translation', 'EQUIP_ALL_ROLE_SUCCESS').format(len(all_roles)))
    except Exception as e:
        await inter.edit_original_message(content=getLang(inter, 'Translation', 'EQUIP_ALL_ROLE_FAILED_ERROR_GENERIC'))


@bot.listen("on_button_click")
async def on_page_click(inter):
    custom_id = inter.data.custom_id
    if custom_id[0:2] == 'ro':
        longvariablethatdoesnothing, pageNo = custom_id.split("_")
        await _roles(inter, type='Role', page=int(pageNo))
        if custom_id[0:2] == 'ri':
            longvariablethatdoesnothing, pageNo = custom_id.split("_")
            await _roles(inter, type='Icon', page=int(pageNo))


#@bot.listen()
async def on_slash_command_error(ctx, error):
    if isinstance(error, disnake.ext.commands.MissingPermissions):
        await ctx.send(getLang(ctx, 'Translation', 'COMMAND_FAILED_BAD_PERMISSIONS'), ephemeral=True)
        return
    elif isinstance(error, disnake.ext.commands.CommandOnCooldown):
        await ctx.send(getLang(ctx, 'Translation', 'COMMAND_FAILED_COOLDOWN'), ephemeral=True)
        return
    await ctx.send(
        getLang(ctx, 'Translation', 'COMMAND_FAILED_UNKNOWN_ERROR').format(error))
    print(error)


bot.run(open('token.txt', 'r').read())
