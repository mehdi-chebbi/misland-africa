# Setup OSS_LDMS using Docker for Development

### Build new Docker images

Build Docker image for development and spin the container

> docker-compose up -d --build

### Bring the containers up

> docker-compose up -d

**NB**: To check for errors in the logs, run **docker-compose logs -f**

### Run the migrations

> docker-compose exec web python manage.py migrate --noinput

**NB:**. Run **docker-compose down -v** to remove the volumes along with the containers. Then, re-build the images, run the containers, and apply the migrations.

1. Ensure the default Django tables were created:

> docker-compose exec db psql --username=hello_django --dbname=hello_django_dev

### You can check that the volume was created as well by running

> docker volume inspect django-on-docker_postgres_data

### Update the file permissions locally:

> chmod +x app/entrypoint.dev.sh

### Apply the migrations

Run them manually, after the containers spin up, like so:

> docker-compose exec web python manage.py flush --no-input
> docker-compose exec web python manage.py migrate

### Bring down a container

> docker-compose down -v

### Check for errors

If the container fails to start, check for errors in the logs via 

> docker-compose -f docker-compose.yml logs -f.

# Deploy OSS_LDMS using Docker for Production

### Important:
- Change ENV_TYPE in .env from DEV to PROD

### Summary

1. We use Docker multi-build to reduce the overall image size
1. We add Gunicorn, a production-grade WSGI server to serve Django app
1. We add Nginx into the mix to act as a reverse proxy for Gunicorn to handle client requests as well as serve up static files.

**NB**: Use the **docker-compose -f docker-compose.prod.yml** option in the dev machine where there is a likelihood of multiple containers

* Push **docker-compose.prod.yml** to the production server

* **Modify ALLOWED_HOSTS**. Ensure you add the ip address of the server to the **ALLOWED_HOSTS = ['my_server']** setting in env.prod file. Example is given below:

> DJANGO_ALLOWED_HOSTS=10.1.60.101 localhost 0.0.0.0 127.0.0.1 [::1]

* Build the production images and spin up the containers. The -d flag starts the container in daemon mode

> docker-compose -f docker-compose.prod.yml up -d --build

* Verify that the database was created along with the default Django tables. **db** is the name of the container under services in the .yml file

> docker-compose -f docker-compose.prod.yml exec db psql -h db --username={DB_USERNAME} --dbname={DB_NAME}

* If you get the below error **_django.db.utils.OperationalError: FATAL:  database "{DB_NAME}" does not exist_**, run **docker-compose down -v** to remove the volumes along with the containers. Then, re-build the images, run the containers, and apply the migrations. To apply migrations, run

> docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --no-input

Test out the admin page at http://localhost:1337/admin. The static files are not being loaded anymore. This is expected since Debug mode is off. We will fix this shortly.

* You can check that the volume was created as well by running:

> docker volume inspect oss-ldms_postgres_data

* If the container fails to start, check for errors in the logs via 

> docker-compose -f docker-compose.prod.yml logs -f

* Update the file permissions locally for the start script

> chmod +x app/entrypoint.prod.sh

* Test the containers

> docker-compose -f docker-compose.prod.yml down -v
> docker-compose -f docker-compose.prod.yml up -d --build
> docker-compose -f docker-compose.prod.yml exec web python manage.py createcachetable
> docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
> docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear

* Ensure the app is up and running at http://localhost:1337. Post **1337** is the port specified in docker-compose.prod.yml file

* Bring the containers down once done

> docker-compose -f docker-compose.prod.yml down -v

## Clear cache

To clear all the cache, open Django shell by running python manage.py shell, then run the below commands

```python

from django.core.cache import cache
cache.clear() 

```

## Create Shared Folder

If you are deploying on Synology, shared folders must be created. These folders **MUST BE MANUALLY ATTACHED** to the container. This is done using the Docker GUI of Synology. To associate, select Docker from the main menu, then go to containers. Select the Image you want to map a volume to. Click Launch -> Advanced Settings -> Volumes. Add a new Folder.

* Create **/media, /static and /postgres_data** folders under the Docker application in Synology. Remember to grant full permissions to the user group **Everyone**. You will need to run the **docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear** command again.

## Restore media files

* The uploaded raster files need to be copied over to the new server
* Create **media_backup** directory in the new Docker host
* Run **rsync** to copy the media files across servers

* The syntax of rsync is rsynch [OPTIONS] source destination
* The example below shows how to copy remote files onto the local server

> rsync -avz root@172.105.246.124:/home/nyaga/app/oss_ldms/backend/media/ media_backup/
* The example below shows how to copy local files onto the remote server

> rsync -avz /var/snap/docker/common/var-lib-docker/volumes/oss-ldms_media_volume/_data/ root@194.163.176.189:/var/lib/docker/volumes/oss_ldms_media_volume/_data/

* Copy the media files onto the shared volume of the **web** container

> cp sudo cp media_backup/ /var/snap/docker/common/var-lib-docker/volumes/oss-ldms_media_volume/_data/

## Restore database

* First take a backup of the existing database via:

> pg_dump -h 127.0.0.1 -U {DB_USER} {DB_NAME} > ~/app/oss_ldms_backup_20210313_premod.sql

* If the database is hosted in a docker container, run the command below

> docker-compose -f docker-compose.prod.yml exec db pg_dump -h db --username={DB_USER} --dbname={DB_NAME} --password -f /var/lib/postgresql/oss_ldms_backup_20210903.sql

or 

> docker-compose -f docker-compose.misland.prod.yml exec db pg_dump -h db --username=ldms_user --dbname=oss_ldms --password -f /var/lib/postgresql/oss_ldms_backup_20221220.sql

* You can then navigate to **/var/snap/docker/common/var-lib-docker/volumes/oss-ldms_postgres_data/_data/ to copy the backup from there or send it via rsync to the new server as below

> rsync -avz /var/snap/docker/common/var-lib-docker/volumes/oss-ldms_postgres_data/_data/ root@194.163.176.189:/var/lib/docker/volumes/oss_ldms_postgres_data/_data/

* Since the Postgres in Linode server is Postgres 10, we need to replace the **AS INTEGER** string since it is not supported in Postgres 9

> cat oss_ldms_backup_20210313_premod.sql | sed -e '/AS integer/d' > oss_ldms_backup_20210313.sql

* Zip the backup file

> zip oss_ldms_backup_20210313.zip oss_ldms_backup_20210313.sql


## Transfer backup file to the current server

Use **rsync** to make the Transfer

* Create the backup directory

> mkdir dbbackup

* Run the **rsync** command

> rsync -avz root@172.105.246.124:/home/nyaga/app/db_backup/oss_ldms_backup_20210313.zip dbbackup/

or

> rsync -avz root@192.168.2.102:/var/lib/docker/volumes/oss-ldms_postgres_data/_data/oss_ldms_backup_20221220.sql dbbackup/

* cd to the dbbackup/ folder i.e location of the backup file

* Unzip the file. You may need to install the unzip package via **sudo apt install unzip**

> unzip oss_ldms_backup_20210313.zip

* Copy the unzipped database file to a mounted shared directory. The sql file must be existing in the container so it needs to be copied across. An example is 

> cd /volume1/oss_ldms/

**NB**: Depending on the Docker host, the shared volume may be different. Confirm the location of the shared volume by running  **docker inspect {POSTGRES_CONTAINER_ID}** and checking the section on **mounts**. An example is "/var/snap/docker/common/var-lib-docker/volumes/oss-ldms_postgres_data/_data". 

**NB**: Remember the shared folders are located in /volume1/@docker/volumes/ for Synology architecture

> cp sudo cp oss_ldms_backup_20210313.sql /var/snap/docker/common/var-lib-docker/volumes/oss-ldms_postgres_data/_data/

* Restore the database via:

First drop the entire schema by running. You need to cd to the folder where **docker-compose.prod.yml** is located

> docker-compose -f docker-compose.prod.yml exec db psql -h db  --username={DB_USER} --dbname={DB_NAME}

```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
```
Exit from the database interface by pressing \q. Then run the command below. This assumes the sql backup file has already been moved or copied to the shared volume **/var/snap/docker/common/var-lib-docker/volumes/oss-ldms_postgres_data/_data/**

> docker-compose -f docker-compose.prod.yml exec db psql -h db  --username={DB_USER} --dbname={DB_NAME} --password -f /var/lib/postgresql/oss_ldms_backup_20210313.sql

* If you encounter an error, run 
> ALTER TABLE ldms_adminleveltwo alter column nl_name_1 drop not null;
> ALTER TABLE ldms_adminleveltwo alter column varname_2 drop not null;
> ALTER TABLE ldms_adminleveltwo alter column nl_name_2 drop not null;

* You can now try log in using an existing Django admin account at **{SERVER_ADDRESS}:1337/admin**

**NB**: if you are running docker-compose as sudo, it might request you to enter a sudo password before it requests for the db user password

**NB**: To restore from a plain .sql dump file, do the following. But first ensure the database is dropped and created first before running the commands

> sudo su postgres
> psql databasename -f exportfilename.sql

## Automated backups

* A new docker container has been added to handle automatic backups and restores. See https://github.com/kartoza/docker-pg-backup for more details.
* The backup frequency can be specified as a crontab. Currently, a daily backup is taken at 23:00 hours.
* Only the 7 latest backups are kept. Older backups are deleted
* The backup file is named using the file format **{year}/{month}/PG_oss_ldms.{day_of_month}-{month}-{year}.dmp**. An example is **2022/October/PG_oss_ldms.05-October-2022.dmp**

### To take a backup at an instance, run the command below

```bash
docker-compose -f docker-compose.devserver.prod.yml exec dbbackups ./backups.sh
```

The backups will be stored in the /backups folder within the docker container. But normally this is usually a mounted volume. Check your compose file to see where the backups are stored on the host

### Restore a backup dump

* The backup dump file must be accessible within the dbbackups container. So if its not, copy onto the mounted volume. See example below

```bash
sudo cp /var/snap/docker/common/var-lib-docker/volumes/oss-ldms_db-backups/_data/2023/May/PG_oss_ldms.21-May-2023.dmp /var/lib/docker/volumes/oss-ldms_db-backups/_data
```

* Edit the .env file and provide values as below

```bash
# postgres backups
TARGET_DB=oss_ldms
WITH_POSTGIS=1
TARGET_ARCHIVE=/backups/PG_oss_ldms.21-May-2023.dmp
```

**Note**: pg-backup container stores files in /backups folder

* Run the following command

```bash
docker-compose -f docker-compose.misland.prod.yml exec dbbackups /restore.sh
```

## Debug container

To run the container in DEBUG mode, run

> docker run -it {CONTAINER_NAME} /bin/bash

To run a command on a running container

>  docker exec -it {CONTAINER_ID}  /bin/bash

## To check logs for a container

>  docker logs {CONTAINER_ID}

## NOTES

1. Serving **Static files**.

* Since Gunicorn is an application server, it will not serve up static files. So, how should both static and media files be handled in this particular configuration?

* Update settings.py

> STATIC_URL = "/static/"
> STATIC_ROOT = os.path.join(BASE_DIR, "static")


### To push the image to Dockerhub:

In case you need to push images to Docker hub, follow the steps below:

* Tag the images as such 

> docker tag django-on-docker_nginx stevenyaga/oss_ldms_nginx:latest

> docker tag oss-ldms_web stevenyaga/oss_ldms_web:latest
> docker tag oss-ldms_nginx stevenyaga/oss_ldms_nginx:latest
> docker tag kartoza/postgis:9.6-2.4 stevenyaga/oss_ldms_postgres:latest

* Push the image to

> docker login
> docker push  stevenyaga/oss_ldms_web:latest
> docker push  stevenyaga/oss_ldms_nginx:latest
> docker push  stevenyaga/oss_ldms_postgres:latest


## Install and using Geoserver docker image

* Run docker pull 
<pre>docker pull kartoza/geoserver</pre>

* Run the following command to start Geoserver container
<pre> docker run -e GEOSERVER_ADMIN_USER=admin  -e GEOSERVER_ADMIN_PASSWORD=geoserver -e RESET_ADMIN_CREDENTIALS=TRUE -d -p 8600:8080 --name geoserver  kartoza/geoserver:2.20.1 </pre>

* The default password is located in the following file within docker container **/opt/geoserver/data_dir/security/masterpw/default/passwd**
* You can also retrieve the password by looking at the logs
> If you get an error about existing container, do the following
<pre>docker ps -a </pre>
> Get the id of the Geoserver container. Then remove the container
<pre>docker rm {CONTAINER_ID}

* Launch the Geoserver from a browser as below and login using the credentials (username=admin, password=geoserver) as specified above i.e GEOSERVER_ADMIN_USER=admin and GEOSERVER_ADMIN_PASSWORD=geoserver
<pre>http://localhost:8600/geoserver/</pre>

### References

* https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/
* https://www.prisma.io/dataguide/postgresql/inserting-and-modifying-data/importing-and-exporting-data-in-postgresql
