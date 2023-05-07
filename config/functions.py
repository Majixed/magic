import ast
import json

from discord.ext import commands


# Helper function for eval command
def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

# Decorator for admin check
def get_admins():
    with open("admins.json", "r") as data:
        admin_data = json.load(data)
    admin_list = admin_data["botAdmin"]
    return admin_list

def check_admin(ctx):
    bot_admin = get_admins()
    return ctx.author.id in bot_admin


is_admin = commands.check(check_admin)
