#!/bin/bash

echo 'Copying web resources from Django package'
mkdir admin
cp -R /usr/lib/python2.6/site-packages/django/contrib/admin/media/* admin/
#cp -R /usr/lib/python2.7/site-packages/django/contrib/admin/media/* admin/
