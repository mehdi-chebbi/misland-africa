## Guide to running modularization

### Prerequisites

* Take a backup of the database

> pg_dump -h localhost --username=ldms_user --dbname=oss_ldms -f /home/sftdev/django-apps/oss-ldms/ldms_backup_20221216.sql


* In case you need to drop the database and restore the database do the following

> sudo -u postgres psql

> DROP Database oss_ldms;
> CREATE DATABASE oss_ldms;

* To restore the backup taken, run

> sudo su postgres
> psql oss_ldms -f /home/sftdev/django-apps/oss-ldms/ldms_backup_20221216.sql


1. Step 1

* Make initial migrations for common

> python manage.py makemigrations common

* Copy the migration that contains code for moving data from ldms_ to common_ tables
* Run migrations

> python manage.py migrate


2. Step 2

* Make initial migrations for common_gis

> python manage.py makemigrations common_gis

* Copy the migration that contains code for moving data from ldms_ to common_gis_ tables
* Run migrations

> python manage.py migrate


3. Step 3

* Make initial migrations for user

> python manage.py makemigrations user

* Copy the migration that contains code for moving data from ldms_ to user_ tables
* Run migrations

> python manage.py migrate


4. Step 4

* Make migrations for ldms

> python manage.py makemigrations ldms

* Run migrations since mostly it will be dropping fields and tables that previously existed in the ldms_ schema

> python manage.py migrate