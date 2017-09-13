Thumbnails Setup
================

Directory Structure
-------------------

Each app has its own subdirectory within the *media* folder: *media* is at the root level
(the same level as *manage.py*) and at the same level of the apps is the *thumbnails-cache*
directory.

1. media

1.1 accessories

1.1.1 images of accessories

1.2 *thumbnails-cache* with all its sub-dirs.

ImageFile Setup of model Photo
------------------------------

photo    = models.ImageField(upload_to = 'accessories', blank=True, null=True)

Setting of *settings.py*
------------------------

The project settings is located in *boutique*.

- 'thumbnails' is declared within INSTALLED_APPS list;

- BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

- STATIC_URL = '/static/'

- MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

- MEDIA_URL = '/'

Project URLS
------------

Import from django.conf.urls.static import static in the urls.py of the project
and add this path to the url patterns. For example:

url(r'^finance/', include('finance.urls', namespace="finance")),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




