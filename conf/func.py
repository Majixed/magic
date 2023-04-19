import json

from discord.ext import commands


def get_admins():
    with open("admins.json", "r") as json_read:
        admin_data = json.load(json_read)
    admin_list = admin_data["botAdmin"]
    return admin_list


def check_admin(ctx):
    bot_admin = get_admins()
    return ctx.author.id in bot_admin


is_admin = commands.check(check_admin)
