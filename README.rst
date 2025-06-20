magic
=====

.. raw:: html

    <div align="center">
    <img src="https://img.shields.io/github/languages/top/Majixed/magic" alt="top-language">
    </div>

A personal discord.py utility bot for Linux.

How to use
----------

Ensure you have at least ``python3.9``. Bot functionality is not guaranteed with earlier versions of python.

Clone this repository and make it your current working directory:

.. code:: sh

    git clone https://github.com/Majixed/magic && cd ./magic/

Install dependencies:

.. code:: sh

    pip install -r requirements.txt

Add your bot token to a ``.env`` file in the same directory:

.. code:: sh

    echo "TOKEN=<your bot's token>" > .env

To use the TeX commands, install a distribution of TeX Live from the `TUG Website <https://tug.org/texlive/acquire-netinstall.html>`_ (recommended) or your Linux distro's package manager.

There are two more prerequisites required for this feature, ``imagemagick``, which provides the ``magick`` and ``identify`` commands, and ``ghostscript``. To install on Ubuntu:

.. code:: sh

    sudo apt install ghostscript imagemagick

Copy ``config/config-example.py`` as ``config/config.py`` in the same directory. This will be the configuration file. You may edit the values in this file if you wish:

.. code:: sh

    mv config/config-example.py config/config.py

Finally, start up the bot:

.. code:: sh

    ./magic

Make sure you have given the bot the privileged Message Content intent in the `Discord Developer Portal <https://discord.com/developers/>`_, otherwise it may not be able to respond to the prefix and some features may not work.

The bot's default prefix is ``-``, you can change it by editing the ``prefix`` variable in ``config/config.py``. Run ``-help`` in discord to get a list of all its commands.

If you have any suggestions or queries, feel free to open an issue.

I borrowed some code from the Paradøx discord bot, check out their repo `here <https://gitlab.paradoxical.pw/team-paradox/paradox>`_.
