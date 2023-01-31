"""Contains functions that manage roles."""


import random
import enum
import sqlite3
import json

import disnake

from .. import global_vars
from . import translation



GLOBALS = global_vars.Globals.get_globals()



async def list_specific_role(inter: disnake.UserCommandInteraction, role: disnake.Role):
    await inter.response.defer()
    conn = sqlite3.connect('roles.db')
    cur = conn.cursor()

    roleID = role.id

    sql = f'''SELECT * FROM roles WHERE role LIKE '%{roleID}%' '''
    cur.execute(sql)
    roleItems = cur.fetchall()

    sql2 = f'''SELECT * FROM roles WHERE roleicon LIKE '%{roleID}%' '''
    cur.execute(sql2)
    iconItems = cur.fetchall()

    userRoleList = []
    userIconList = []

    guild_member_ids = [member.id for member in inter.guild.members]

    for i in roleItems:
        user, _, _ = i
        if user in guild_member_ids:
            userObj = await inter.guild.get_or_fetch_member(user)
            userRoleList.append(userObj)

    for i in iconItems:
        user, _, _ = i
        if user in guild_member_ids:
            userObj = await inter.guild.get_or_fetch_member(user)
            userIconList.append(userObj)

    embeds = []

    allUserRoleStr = ''
    if len(userRoleList) > 0:
        for au in userRoleList:
            allUserRoleStr = f'{allUserRoleStr}\n{au.name} ({au.mention})'
            if len(allUserRoleStr) > 4000:
                allUserRoleStr = f'{allUserRoleStr}\n{translation.translation.getLang(inter, "Translation", "LIST_ALL_OVERFLOW").format((len(userRoleList) - userRoleList.index(au)))}'
                break
        embeds.append(disnake.Embed(title=translation.getLang(inter, 'Translation', 'LIST_ROLE').format(role.name), description=allUserRoleStr,
                              color=role.color))

    allUserIconStr = ''
    if len(userIconList) > 0:
        for au in userIconList:
            allUserIconStr = f'{allUserIconStr}\n{au.name} ({au.mention})'
            if len(allUserIconStr) > 4000:
                allUserIconStr = f'{allUserIconStr}\n{translation.getLang(inter, "Translation", "LIST_ALL_OVERFLOW").format((len(userIconList) - userIconList.index(au)))}'
                break
        embeds.append(disnake.Embed(title=translation.getLang(inter, 'Translation', 'LIST_ICON').format(role.name), description=allUserIconStr,
                                    color=role.color))

    if len(embeds) == 0:
        embeds.append(disnake.Embed(title=translation.getLang(inter, 'Translation', 'LIST_ROLE').format(role.name), description=translation.getLang(inter, 'Translation', 'LIST_ROLE_RETURN_NONE'),
                              color=role.color))

    await inter.edit_original_message(embeds=embeds)


def add_user_to_database(user):
    conn = sqlite3.connect('roles.db')
    cur = conn.cursor()

    blank = json.dumps([])

    sql = '''INSERT INTO roles(user, role, roleicon) VALUES(?, ?, ?)'''  # Adds new user, default has no roles.
    cur.execute(sql, [user, blank, blank])
    conn.commit()


def get_user_roles(user, skip=False):
    if user == 9:
        skip = True

    conn = sqlite3.connect('roles.db')
    cur = conn.cursor()

    sql = '''SELECT role, roleicon FROM roles WHERE user IS ?'''
    cur.execute(sql, [user])  # Gets all roles & role icons from the user.

    item = cur.fetchone()
    if not item:
        add_user_to_database(user)
        return get_user_roles(user)

    # user_roles = json.load()
    roles_str, roleIcons_str = item
    roles, roleIcons = json.loads(roles_str), json.loads(roleIcons_str)

    if not skip:
        bl, _ = get_user_roles(9)

        for i in roles:
            if i in bl:
                database_update('remove', user, role=i)
                roles.remove(i)
        for ix in roleIcons:
            if ix in bl:
                database_update('remove', user, role=ix)
                roleIcons.remove(ix)

        bl, _ = get_user_roles(9, skip=True)
        to_blacklist = False
        for i in roles:
            if i in bl:
                to_blacklist = True
        for ix in roleIcons:
            if ix in bl:
                to_blacklist = True

        if to_blacklist:
            database_update("none", user)

    return roles, roleIcons


def database_update(action, user, role=None, roleIcon=None):
    conn = sqlite3.connect('roles.db')
    cur = conn.cursor()

    cur.execute('''SELECT role, roleicon FROM roles WHERE user IS ?''', [user])  # Gets all roles & role icons from the user.

    roles, roleIcons = get_user_roles(user, skip=True)

    if action == 'add':
        if role in roles or roleIcon in roleIcons:
            return 'User already has role!'
        if role:
            roles.append(role)
        if roleIcon:
            roleIcons.append(roleIcon)
    elif action == 'remove':
        if role:
            if role not in roles:
                return 'User does not have that role!'

            roles.remove(role)
        if roleIcon:
            if roleIcon not in roleIcons:
                return 'User does not have that role!'

            roleIcons.remove(roleIcon)
    else:
        return False

    cur.execute('''UPDATE roles SET role = ? WHERE user IS ?''', [json.dumps(roles), user])
    cur.execute('''UPDATE roles SET roleicon = ? WHERE user IS ? ''', [json.dumps(roleIcons), user])
    conn.commit()



class DisplayTypes(enum.Enum):
    """Contains the display types that can be used."""
    ROLE = "Role"
    ROLE_ICON = "RoleIcon"

async def display_roles(
        inter: disnake.UserCommandInteraction,
        display_type: DisplayTypes,
        returnEmbed = False,
        user=False,
        page=1,
        defer=True
    ):
    """Lists a players' roles & role icons and allows them to choose between them."""

    page = max(page, 1)

    if not returnEmbed and defer:
        await inter.response.defer(ephemeral=True)

    if user:
        if isinstance(user, int):
            user_id = user
        else:
            user_id = user.id
            if user_id == inter.author.id:
                user = False
    else:
        user_id = inter.author.id

    roles, roleIcons = get_user_roles(user_id)
    guild = inter.guild

    true_items = []

    shortType = ''

    if display_type == 'Role':
        itemList = roles
        shortType = 'ro'
    else:
        itemList = roleIcons
        shortType = 'ri'
        true_items.append(guild.get_role(GLOBALS.default_role))

    for r in itemList:
        try:
            role = guild.get_role(r)
            if role is None:
                database_update('remove', user_id, role=r)
            else:
                true_items.append(role)
        except Exception as e:
            print(e)

    if page - 1 > (len(true_items)) / 25:
        page = 1

    true_items.sort(reverse=True)
    true_items_shortened = true_items[(page - 1) * 25:(page * 25)]

    aList = []

    if not returnEmbed and not user:
        rarities = translation.getLang(inter, 'Translation', 'RARITY_LIST').split(', ')
        Menu = disnake.ui.Select()
        options = []
        for r in true_items_shortened:
            print(r.name, r.id)
            if r.id == GLOBALS.default_role:
                name = translation.getLang(inter, 'Translation', 'NO_ICON')
                desc = translation.getLang(inter, 'Translation', 'NO_ICON_DESC')
                temp = disnake.SelectOption(label = name, value = f'{shortType}_{r.id}', description = desc)
            else:
                quality = random.choice(rarities)
                level = random.randint(0, 100)
                name = r.name
                temp = disnake.SelectOption(
                    label=r.name,
                    value=f'{shortType}_{r.id}',
                    description=translation.getLang(inter, 'Translation', 'ITEM_RARITY').format(level, quality, r.name)
                )
            options.append(temp)

        Menu.options = options
        Menu.custom_id = 'role_select'
        aList.append(Menu)
    else:
        Menu = None

    roleStrList = ''

    true_length = len(true_items)
    if len(true_items) > 0:
        if true_items[0].id == GLOBALS.default_role:
            true_length = len(true_items)-1

    for i in true_items_shortened:
        if i.id != GLOBALS.default_role:
            roleStrList = f'{roleStrList}\n{i.mention}'
    if len(true_items) > len(true_items_shortened):
        roleStrList = f'{roleStrList}\n**({((page - 1) * 25) + 1}-{(((page - 1) * 25) + 1) + len(true_items_shortened) - 1})**'

        if true_items[-1] == true_items_shortened[-1] and len(true_items) > 25:
            pageDown = disnake.ui.Button(label='<-', custom_id=f'{shortType}_{page - 1}', style=1)
            aList.append(pageDown)
        if true_items[0] == true_items_shortened[0] and len(true_items) > 25:
            pageUp = disnake.ui.Button(label='->', custom_id=f'{shortType}_{page + 1}', style=1)
            aList.append(pageUp)

    if true_length != 1:
        type_plural = translation.getLang(inter, section='Translation', line=f'{display_type.upper()}_PLURAL')
    else:
        type_plural = translation.getLang(inter, section='Translation', line=f'{display_type.upper()}')

    if user_id == 9:
        embTitle = translation.getLang(inter, section='Translation', line='ROLES_LIST_BLACKLIST').format(true_length,
                                                                                             type_plural)
    elif user and not isinstance(user, int):
        embTitle = translation.getLang(inter, section='Translation', line='ROLES_LIST_USER').format(user.name, true_length,
                                                                                        type_plural)
    else:
        embTitle = translation.getLang(inter, section='Translation', line='ROLES_LIST_INVOKER').format(true_length, type_plural)

    embed = disnake.Embed(title=embTitle, description=roleStrList, color=0xD8B400)
    if not returnEmbed:
        embed.set_footer(text=translation.getLang(inter, section='Translation', line='ROLE_FOOTER_INFO').format(
            translation.getLang(inter, section='Translation', line=f'{display_type.upper()}_PLURAL')))
    if len(true_items) != 0 and not returnEmbed and not user:
        embed.set_footer(text=translation.getLang(inter, section='Translation', line='ROLE_FOOTER_DROPDOWN').format(
            translation.getLang(inter, section='Translation', line=f'{display_type.upper()}')))

    if returnEmbed:
        return embed
    elif len(true_items) > 0 and not user:
        print(aList)
        await inter.edit_original_message(components=aList, embed=embed)
    else:
        await inter.edit_original_message(embed=embed)
