
INSPIRE overlay
===============

This is INSPIRE source code overlay for Invenio v.2.0. It installs on top of
Invenio digital library platform source code as [explained here](http://invenio.readthedocs.org/en/latest/getting-started/overlay.html).

Installation
------------

To install the overlay, simply clone this repository and run:

```shell
(inspire)$ cdvirtualenv src/inspire-next
(inspire)$ pip install -r requirements.txt --exists-action i
```

The parameter `exists-action` ignores any existing installations (for example, Invenio).

Next step is to install assets (js, css etc.):


```shell
(inspire)$ inveniomanage bower -i bower-base.json > bower.json
Generates or update bower.json for you.
(inspire)$ cat .bowerrc
{
    "directory": "inspire/base/static/vendors"
}
(inspire)$ bower install
(inspire)$ ls inspire/base/static/vendors
bootstrap
ckeditor
hogan
jquery
jquery-tokeninput
jquery-ui
plupload
...
```

Now you can follow the standard invenio installation and development procedures, such as running `inveniomanage collect`.

Demosite installation
---------------------

Create and fill database tables from fixtures:

```shell
(inspire)$ inveniomanage demosite create -p inspire.base
```

Populate demo records and enable demo-site:

```shell
(inspire)$ cdvirtualenv src/inspire-next
(inspire)$ inveniomanage demosite populate -p inspire.base -f inspire/testsuite/data/demo-records.xml
```

Start the server:

```shell
(inspire)$ inveniomanage runserver
```

Now you should have a running INSPIRE demo site running at [http://localhost:4000](http://localhost:4000)

## Happy hacking!
