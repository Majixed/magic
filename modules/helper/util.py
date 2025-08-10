import subprocess
import ast
import json


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
    fg = "ffffff"
    bg = "1a1a1e"
    user_id = str(user_id)

    try:
        with open("tex/config/texconfig.json", "r") as cfg:
            config_data = json.load(cfg)
            try:
                fg = config_data[user_id]["fg"]
                bg = config_data[user_id]["bg"]
            except KeyError:
                pass
    except FileNotFoundError:
        pass

    DOC_CLASS = "\\documentclass[12pt, bgcolor={}, textcolor={}, minpagewidth=110pt]{{texit}}".format(
        bg, fg
    )

    with open(f"tex/inputs/{user_id}.tmp", "w") as f_input:
        f_input.write(code)
    output = subprocess.run(
        f"tex/scripts/{script} {user_id} '{DOC_CLASS}'",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True,
    )
    if output.stdout:
        err_out = output.stdout
        return err_out


user_locks = {}


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
