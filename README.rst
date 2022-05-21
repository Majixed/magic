magic
=====

A personal discord.py utility bot built on iOS, for iOS.

How to use
----------

To get started, install the `a-Shell <https://github.com/holzschu/a-shell>`_ terminal emulator from the App Store. If you want to make use of the ``pdftex`` and ``luatex`` modules, run ``luatex`` in the terminal:

.. code:: sh

    $ luatex

This will install the pdfTeX and LuaTeX extensions to a-Shell. Type ``y`` at the prompt and wait for it to install.

This bot is built using discord.py v2.0.0a, which is not available in PyPI. To install it, run the following commands:

.. code:: sh

    $ lg2 clone https://github.com/Rapptz/discord.py
    $ cd discord.py
    $ pip install -U .

Additionally, the bot makes use of the `discord-pretty-help <https://github.com/stroupbslayen/discord-pretty-help>`_ and `googletrans <https://github.com/ssut/py-googletrans>`_ packages, so they must also be installed.

.. code:: sh

    $ pip install discord-pretty-help
    $ pip install googletrans

Clone this repository and make it your current working directory:

.. code:: sh

    $ lg2 clone https://github.com/Majixed/magic
    $ cd magic

Add your bot token to a ``.env`` file in the same directory:

.. code:: sh

    echo "TOKEN=<your bot's token>" > .env

To use the TeX commands, create `this <https://www.icloud.com/shortcuts/a406c5e667944bfea3059f41cd44e655>`_ shortcut in the iOS Shortcuts app. This will convert the output pdf of TeX to a png image which can be uploaded to the discord channel.

Open the a-Shell terminal and Shortcuts app in Split View, so that the shortcut can run when a TeX command is invoked.

Finally, start up the bot,

.. code:: sh

    python3 magic.py

Make sure you have given the bot the correct permissions in your discord server, so that you can use all of its features. The bot's default prefix is ``&``, you can change it by editing the ``prefix`` variable in ``config/config.py``. To use the LaTeX commands, you must open the Shortcuts app in Split View, so that it may be able to use the shortcut ``pdfpng3`` to convert the generated pdf file to png.

If you have any suggestions or queries, feel free to open an issue.
