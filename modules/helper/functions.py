import os
import subprocess
import ast
import json

from discord.ext import commands


# Condition check for reaction buttons
def reaction_check(msg_id, author, emoji):
    def check(reaction, user):
        return (
            reaction.message.id == msg_id
            and user == author
            and str(reaction.emoji) == emoji
        )

    return check


# TeX compile routine
def compile_tex(user_id, code, script):
    with open(f"tex/inputs/{user_id}.tmp", "w") as f_input:
        f_input.write(code)
    subprocess.run(f"tex/scripts/{script} {user_id}", shell=True)
    if os.path.isfile(f"tex/staging/{user_id}/{user_id}.error"):
        with open(f"tex/staging/{user_id}/{user_id}.error", "r") as f_err:
            err_out = f_err.read()
        return err_out


# Codeblock detection for pdftex and luatex
def detect_codeblock(code, langs: list):
    if "```" in code:
        lines = code.splitlines()
        codeblock = False
        final_code = []
        for line in lines:
            if "```" in line:
                splits = line.split("```")
                for split in splits:
                    if codeblock and split not in langs:
                        final_code.append(f"{split}")
                    codeblock = not codeblock
                if codeblock:
                    final_code.append("")
                codeblock = not codeblock
            elif codeblock:
                final_code.append(line)
        code = "\n".join(final_code).rstrip("\n")
    return code


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
