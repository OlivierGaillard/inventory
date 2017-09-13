How to start
============

- Use the requirements.txt file to make a virtualenv.
- With the admin add one Enterprise object and at least one user.
- Create the permission *view_achat* and set it to this user.
- Create one *Employee* instance by selecting this user and this enterprise.

Dump and load of data
---------------------

Per default format is JSON. We can add `--indent 4`. For sample:
`python manage.py dumpdata coordinates.Localite --indent 4 > locations.json`

En revanche utiliser `django-admin` (like the documentation write) generates
one error.

::
   django-admin dumpdata [app_label[.ModelName] [app_label[.ModelName] ...]]

Usage for testing
-----------------

Following the documentation it suffices to create a `fixtures` directory
in the app and declare this in the test class::

  class TestFraisArrivage(TestCase):
    
    fixtures = ['locations.json']

Then every unittest benefits will load these data in the temporary database
which is set for the test. Writing a simple test to count the
locations failed because countries were referenced. Okay I dumped the
countries and added them to fixtures::
  fixtures = ['countries.json', 'locations.json']


TODO
====

- Automate the setup
- Add fake articles with faker
- Create a demo site.
- Fix and update functional tests with selenium
