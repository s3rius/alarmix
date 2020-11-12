.. image:: ./logo.png
    :alt: logo
    :align: center

===============
Installation
===============

.. code-block:: bash

    python -m pip install alarmix

⚠️ `MPV <https://mpv.io/>`_ must be installed and accessible ⚠️

At first, you need to start alarmd daemon:

.. code-block:: bash

    alarmd --sound "path/to/sound"

Then you can manage your alarms with `alarmc` command.

.. code-block:: bash

    alarmc # Show scheduled alarms
    alarmc stop # Stop buzzing alarm
    alarmc add 20:00 19:30 14:00 # Add alarms
    alarmc add 20:00 --delete # delete TODO: make other command
    alarmc

    alarmc -h # Show help