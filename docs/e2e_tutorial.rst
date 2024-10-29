*************************
E2E Test Writing Tutorial
*************************

For the tutorial we will try to test the first part of the harvest. We will try to harvest arXiv
and then assert that a holdingpen entry for the harvested record appears.

Fixtures
++++++++

Let's create a test file `tests/e2e/test_arxiv_in_hp.py` in INSPIRE-Next. To run our tests we will
need to import a few things and set up some fixtures:

.. code-block:: python

    import os
    import pytest
    import time

    from inspirehep.testlib.api import InspireApiClient
    from inspirehep.testlib.api.mitm_client import MITMClient, with_mitmproxy

    @pytest.fixture
    def inspire_client():
        # INSPIRE_API_URL is set by k8s when running the test in Jenkins
        inspire_url = os.environ.get('INSPIRE_API_URL', 'http://test-web-e2e.local:5000')
        return InspireApiClient(base_url=inspire_url)


    @pytest.fixture
    def mitm_client():
        mitmproxy_url = os.environ.get('MITMPROXY_HOST', 'http://mitm-manager.local')
        return MITMClient(mitmproxy_url)

``InspireApiClient`` is used to interact with INSPIRE through the API. Using it we can for example
trigger a harvest, or request holdingpen entries. ``MITMClient`` is a similar client for the proxy,
with it we can swap scenarios, enable recording of interactions, or make assertions based on what
happened during the test. ``with_mitmproxy`` is a helper decorator, that will automatically set up
the scenario for you (scenario name will match the test name) and optionally, if you specify
``record=True``, enable recording for the duration of the test.


We will also need the following fixture to set up all of the dummy fixtures and records in the
test instance of INSPIRE. Most likely when writing a real test this fixture will already be present,
as it is needed for virtually any test:

.. code-block:: python

    @pytest.fixture(autouse=True, scope='function')
    def init_environment(inspire_client):
        inspire_client.e2e.init_db()
        inspire_client.e2e.init_es()
        inspire_client.e2e.init_fixtures()
        # refresh login session, giving a bit of time
        time.sleep(1)
        inspire_client.login_local()

Interaction Recording
+++++++++++++++++++++

Now that we have set up all of the necessary fixtures, we can attempt to start writing our test.
We add a wait (for now, we will improve it later in the tutorial) at the end as to give time for
INSPIRE to harvest, pull the pdf and the eprint, etc. Without this, the test would finish
immediately after scheduling the crawl, which would deregister the scenario and disable recording.
Later on, we will add actual polling to see if the articles were harvested.

.. code-block:: python

    @with_mitmproxy(should_record=True)
    def test_arxiv_in_hp(inspire_client, mitm_client):
        inspire_client.e2e.schedule_crawl(
            spider='arXiv_single',
            workflow='article',
            url='http://export.arxiv.org/oai2',
            identifier='oai:arXiv.org:1806.04664',  # Non-core, will halt
        )

        time.sleep(60)  # Let's wait for INSPIRE to harvest the records

Let us now run this "test" and see what happens:

.. code-block:: bash

    docker compose -f docker-compose.test.yml run --rm e2e pytest tests/e2e/test_arxiv_in_hp.py

Proxy Web UI
++++++++++++

After the test started running we can use the proxy's web interface to look at the requests that are
happening during the test session. The proxy exposes its web interface on port 8081, so open your
browser and navigate to ``http://127.0.0.1:8081``.

There you will see initial requests to RT, ElasticSearch and so on, logging in to INSPIRE. These are
followed by requests to the ``mitm-manager.local`` that set up the test scenario (``PUT /config``)
and and recording (``POST /record``).

After this all the requests (until disabling recording and/or switching the scenario) belong to the
current test session. Many of them (``test-indexer``, ``test-web-e2e.local``) are whitelisted and
not recorded. You might notice a few requests to ArXiv like so:

* ``GET http://export.arxiv.org/oai2?verb=GetRecord&metadataPrefix=arXiv&identifier=oai...``
* ``GET https://arxiv.org/pdf/1806.04664``
* ``GET https://arxiv.org/e-print/1806.04664``

These are live interactions that are recorded, you can find them in
``tests/e2e/scenarios/arxiv_in_hp/ArxivService/``. If you need to re-record an interaction, simply
remove the file you want to overwrite or rename it in such a way that it doesn't have a `yaml`
extension.

.. tip::
    Since the responses from ArXiv come compressed, in order to preserve the original test data,
    this is also the way they are stored. If you need to look inside, you can copy the body from
    the yaml, and assuming it's pasted in another file called ``gzip.txt`` run:

    ``cat gzip.txt | base64 -di | gzip -d > plain.txt``

    Similarily to compress it back:

    ``cat plain.txt | gzip | base64 > gzip.txt``

Querying the Holdingpen
+++++++++++++++++++++++

Now that our interactions are recorded we can go ahead and finish our test, by making assertions
on the holdingpen records. We can also remove the ``should_record=True`` option from the
``@with_mitmproxy`` decorator, as our interactions are now recorded.

To make assertions we can use the ``inspire_client`` and more precisely its ``holdingpen`` module:

.. code-block:: python

    @with_mitmproxy
    def test_arxiv_in_hp(inspire_client, mitm_client):
        inspire_client.e2e.schedule_crawl(
            spider='arXiv_single',
            workflow='article',
            url='http://export.arxiv.org/oai2',
            identifier='oai:arXiv.org:1806.04664',
        )

        time.sleep(60)

        holdingpen_entries = inspire_client.holdingpen.get_list_entries()

        assert len(holdingpen_entries) == 1

        holdingpen_entry = holdingpen_entries[0]

        assert holdingpen_entry.status == 'HALTED'
        assert holdingpen_entry.core is None
        assert holdingpen_entry.arxiv_eprint == '1806.04664'

This test needs to be refactored to not use a "simple" ``time.sleep``, but actual polling, but
already it should work.

Further Improvements
++++++++++++++++++++

As mentioned before, we can introduce a fixture which will enable us to poll until harvest was
finished, instead of having a simple ``time.sleep`` (snippet taken from
``tests/e2e/test_arxiv_harvest.py``):

.. code-block:: python

    def wait_for(func, *args, **kwargs):
        max_time = kwargs.pop('max_time', 200)
        interval = kwargs.pop('interval', 2)

        decorator = backoff.on_exception(
            backoff.constant,
            AssertionError,
            interval=interval,
            max_time=max_time,
        )
        decorated = decorator(func)
        return decorated(*args, **kwargs)

We can then use the fixture in our test:

.. code-block:: python

    @with_mitmproxy
    def test_arxiv_in_hp(inspire_client, mitm_client):
        inspire_client.e2e.schedule_crawl(
            spider='arXiv_single',
            workflow='article',
            url='http://export.arxiv.org/oai2',
            identifier='oai:arXiv.org:1806.04664',
        )

        def _in_holdinpen():
            holdingpen_entries = inspire_client.holdingpen.get_list_entries()
            assert len(holdingpen_entries) > 0
            assert holdingpen_entries[0].status == 'HALTED'
            return holdingpen_entries

        # Will poll every two seconds and timeout after 200 seconds
        holdingpen_entries = wait_for(_in_holdinpen)

        assert len(holdingpen_entries) == 1

        holdingpen_entry = holdingpen_entries[0]

        assert holdingpen_entry.core is None
        assert holdingpen_entry.arxiv_eprint == '1806.04664'

We can also use the mitmproxy client to make assertions on the interactions with external services
that happened during our test:

.. code-block:: python

    @with_mitmproxy
    def test_arxiv_in_hp(inspire_client, mitm_client):
        # ... ...
        mitm_client.assert_interaction_used('ArxivService', 'interaction_0', times=1)

Above will fail if the interaction ``scenarios/arxiv_in_hp/ArxivService/interaction_0.yaml`` has not
been used exactly one time. You can leave off the ``times`` parameter if you want to assert that
the interaction happened at least once, instead of specifying exactly the number of times. Names
of interactions are not important so you can rename them if you like. Naming only matters if two
interactions can match the same request: in such case the lexicographically first one is chosen for
consistency.

Troubleshooting/Tips
++++++++++++++++++++

Accessing web node in browser
-----------------------------

If for any reason you need to access the web interface of INSPIRE, you can add an entry to your
``/etc/hosts`` file with the IP of the web container:

.. code-block:: bash

    $ docker inspect inspirenext_test-web-e2e.local_1 | grep '"IPAddress"'

                "IPAddress": "",
                    "IPAddress": "172.20.0.9",

    $ sudo vim /etc/hosts

And add a line at the bottom:

.. code-block:: text

    172.20.0.9 test-web-e2e.local

Now you can visit http://test-web-e2e.local:5000 in your browser, provided the container is running.

Docker cheatsheet
-----------------

In order to start the web container (don't forget the ``.local`` at the end!):

.. code-block:: bash

    docker compose -f docker-compose.test.yml up test-web-e2e.local

For any other container, change the ``test-web-e2e.local`` to the suitable name; other containers
don't end in ``.local``, this is needed only for inspire-next node as it has to be a domain name.

Similarily substitute ``up`` for ``stop`` or ``kill`` to bring it down, and ``rm`` to remove the
container (e.g. so that the new updated image can be used).

To view the logs of a container:

.. code-block:: bash

    docker compose -f docker-compose.test.yml logs test-worker-e2e

In order to run a shell in an already running container (e.g. to investigate errors):

.. code-block:: bash

    # E.g. for INSPIRE
    docker compose -f docker-compose.test.yml exec test-web-e2e.local bash

    # For MITM-Proxy we use `ash`, as it runs on Alpine Linux base, which doesn't ship with `bash`
    docker compose -f docker-compose.test.yml exec mitm-proxy ash

