Developing GOCD Dashboard
=========================

Before everything:

Install the following packages:

    sudo apt-get install lynx

You need at least version 3.8.3 of sqlite. If you get
`sqlite3.OperationalError: near "WITH": syntax error`
you need a newer version. Do this:

    sudo add-apt-repository ppa:jonathonf/backports
    sudo apt-get update
    sudo apt-get install sqlite3

The console based browser is used for the automated tests.

    sudo python2 -m pip install texttest

In the checkout directory, do the following (this is only needed once):

    python3 -m venv --clear ${PWD}/texttest/venv

The following is needed every time you have  new shell:

    source ${PWD}/texttest/venv/bin/activate

Now, `python` should be the same as `${PWD}/texttest/venv/bin/python3`

    python -m pip install requirements.txt
    python setup.py install -f

Use `${PWD}/texttest/venv/bin/gocddash_sync.py` ('-d' for continuous sync)
to fetch data for the pipelines specified in pipelines.json. Environment
variable `APP_CONFIG` should define the path to application.cfg, see
`texttest/environment.dash`, and `-p` used to find your `pipelines.json`.
The sync also includes an email notification system (see point 6 below).

Stage failures will be parsed and categorized in the following three distinct
phases in which the failure occurred:

* STARTUP: the job failed but the tests were not even started, no tests run
  according to JUnit
* TEST: there were test failures according to JUnit
* POST: all tests passed according to JUnit, but the job still failed

For the runs that actually contain _test_ failures, additional information
is gathered, which is then used for analysis:

* Which tests failed, and how?


Starting the Dashboard
-----------------------

Before it will work you need some configuration. Create a file `application.cfg`
under `gocddash`. There is a sample example file there named
`application.cfg.example` that you can copy.

The synchronization of run data from Go is done through `gocddash_sync.py`.
Synchronization of data will be done for pipelines specified in `pipelines.json`.
Look at `pipelines.json.example` to see what format this file should have.

Run `app.py` in the gocddash directory - this will serve the dashboard.

The dashboard is available locally from http://127.0.0.1:5000/dash/
1. Since by default no pipelines are shown, they must be enabled under
   "Select pipeline groups".
2. Once data has been synchronized, pipelines (under the Failing/Progress/All tabs)
   with additional information are marked with "Insights" along with the latest
   pipeline count for which the information pertains to.
3. On the Insights page for a pipeline, information is displayed in three panels.
   Failed pipelines contain more information and actions.
4. On the Pipeline graphs page, success rate/failure type per agent and historical
   test count graphs are available.
5. A graph of system wide historical success rate per agent is also available through
   the More/Config dropdown menu at the top.
6. The sync process also handles an email notification system for alerting primary
   suspects when a pipeline breaks. The notification system is opt-in per pipeline
   as specified in pipelines.json.


Upgrading gocdpb in PyPI
------------------------

Make sure that all tests pass and that the version has been updated in setup.py.
Commit and push changes to the repository before doing the following.

    $ python3 setup.py sdist
    $ twine upload dist/gocddash-<new version>.tar.gz
    $ sudo pip3 install --upgrade gocddash

Verify that the new version is downloaded, and works as intended.
