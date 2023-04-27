magic
=====

.. raw:: html

    <div align="center">
    <img src="https://img.shields.io/github/languages/top/Majixed/magic" alt="top-language">
    </div>

A personal discord.py utility bot for Linux.

How to use
----------

Clone this repository and make it your current working directory:

.. code:: sh

    $ git clone https://github.com/Majixed/magic
    $ cd magic

Install dependencies:

.. code:: sh

   $ pip install -r requirements.txt

Add your bot token to a ``.env`` file in the same directory:

.. code:: sh

    $ echo "TOKEN=<your bot's token>" > .env

To use the TeX commands, install a distribution of TeX Live from the `TUG Website <https://tug.org/texlive/acquire-netinstall.html>`_ (recommended) or your Linux distro's package manager.

Additionally, the ``convert`` and ``pdftoppm`` utilities are also required, which should be installed via your distro's package manager, for example on Ubuntu:

.. code:: sh
   
  $ sudo apt install convert pdftoppm

Before starting the bot for the first time, you must edit these variables in ``conf/var.py``:

- Replace the emoji IDs in the ``emo_del``, ``emo_left`` and ``emo_right`` variables with the ID of your own custom emojis, or a default emoji of your choosing

Finally, start up the bot:

.. code:: sh

    $ ./magic

Make sure you have given the bot the privileged Message Content intent in the `Discord Developer Portal <https://discord.com/developers/>`_, otherwise it may not be able to respond to the prefix and some features may not work.

The bot's default prefix is ``-``, you can change it by editing the ``prefix`` variable in ``conf/var.py``. Run ``-help`` to get a list of all its commands.

If you have any suggestions or queries, feel free to open an issue.
