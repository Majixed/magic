magic
=====

.. raw:: html

    <div align="center">
    <img src="https://img.shields.io/github/languages/top/Majixed/magic" alt="top-language">
    </div>

A personal discord.py utility bot built on iOS, for iOS.

How to use
----------

To get started, install the `a-Shell <https://github.com/holzschu/a-shell>`_ terminal emulator from the App Store on an iPad with support for Split View. It comes with ``python3`` pre-installed. If you want to make use of the ``pdftex`` and ``luatex`` modules, run ``luatex`` in the terminal:

.. code:: sh

    $ luatex

This will install the pdfTeX and LuaTeX extensions to a-Shell. Type ``y`` at the prompt and wait for it to install.

Clone this repository and make it your current working directory:

.. code:: sh

    $ lg2 clone https://github.com/Majixed/magic
    $ cd magic

Install dependencies:

.. code:: sh

   $ pip install -r requirements.txt

Add your bot token to a ``.env`` file in the same directory:

.. code:: sh

    $ echo "TOKEN=<your bot's token>" > .env

To use the TeX commands, create `this <https://www.icloud.com/shortcuts/a406c5e667944bfea3059f41cd44e655>`_ shortcut in the iOS Shortcuts app. This will convert the output pdf of TeX to a png image which can be uploaded to the discord channel.

Open the a-Shell terminal and Shortcuts app in Split View, so that the shortcut can run when a TeX command is invoked.

Before starting the bot for the first time, you must edit these variables in ``conf/var.py``:

- Replace the emoji IDs in the ``emo_del``, ``emo_left`` and ``emo_right`` variables with the ID of your own custom emojis, or a default emoji of your choosing

Finally, start up the bot:

.. code:: sh

    $ ./magic

Make sure you have given the bot the privileged Message Content intent in the `Discord Developer Portal <https://discord.com/developers/>`_, otherwise it may not be able to respond to the prefix and some features may not work.

The bot's default prefix is ``-``, you can change it by editing the ``prefix`` variable in ``conf/var.py``. Run ``-help`` to get a list of all its commands.

If you have any suggestions or queries, feel free to open an issue.
