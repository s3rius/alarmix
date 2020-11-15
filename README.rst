|py_versions| |build_statuses| |pypi_versions|

.. |py_versions| image:: https://img.shields.io/pypi/pyversions/alarmix?style=flat-square
    :alt: python versions

.. |build_statuses| image:: https://img.shields.io/github/workflow/status/s3rius/alarmix/Release%20python%20package?style=flat-square
    :alt: build status

.. |pypi_versions| image:: https://img.shields.io/pypi/v/alarmix?style=flat-square
    :alt: pypi version
    :target: https://pypi.org/project/fastapi-template/

.. image:: https://raw.githubusercontent.com/s3rius/alarmix/master/logo.png
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

    alarmc # Show scheduled alarms for today
    alarmc -f # Show all scheduled alarms
    alarmc stop # Stop buzzing alarm
    alarmc add 20:00 19:30 14:00 # Add alarms
    alarmc add +30 +2:40 # Add alarms with relative time
    alarmc delete 20:00 # Remove alarm from schedule
    alarmc

    alarmc -h # Show help
