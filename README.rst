|py_versions| |build_statuses| |pypi_versions|

.. |py_versions| image:: https://img.shields.io/pypi/pyversions/alarmix?style=flat-square
    :alt: python versions

.. |build_statuses| image:: https://img.shields.io/github/workflow/status/s3rius/alarmix/Release%20python%20package?style=flat-square
    :alt: build status

.. |pypi_versions| image:: https://img.shields.io/pypi/v/alarmix?style=flat-square
    :alt: pypi version
    :target: https://pypi.org/project/alarmix/

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

    # Run alarmd-server as a daemon
    alarmd -s "path/to/sound/to/play" -d

    # To kill it you need to run
    alarmd kill

    # Of course you can see help
    alarmd -h

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

Also alarmc can display information about your schedule in different formats:

.. code-block::

    ➜  ~ alarmc # Default schedule information
    +------------+----------------+
    | alarm time | remaining time |
    +------------+----------------+
    |  09:30:00  |    9:01:28     |
    +------------+----------------+

    ➜  ~ alarmc -r # Raw data without table formatting (separated by '\t' character)
    alarm time      remaining time
    09:30:00        9:00:43

    ➜  ~ alarmc -w # Show "When" column
    +------------+----------------+----------+
    | alarm time | remaining time |   when   |
    +------------+----------------+----------+
    |  09:30:00  |    8:58:58     | weekdays |
    +------------+----------------+----------+

    ➜  ~ alarmc -c # Show "Cancelled" column
    +------------+----------------+-----------+
    | alarm time | remaining time | cancelled |
    +------------+----------------+-----------+
    |  09:30:00  |    8:57:35     |   False   |
    +------------+----------------+-----------+

    # All options can be combined
    ➜  ~ alarmc -rwc
    alarm time      remaining time  when            cancelled
    09:30:00        8:58:15         weekdays        False

