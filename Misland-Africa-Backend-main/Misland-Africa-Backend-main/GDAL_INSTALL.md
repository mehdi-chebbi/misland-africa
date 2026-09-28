## Steps to install gdal

### Step 1: Install gdal globally

* Install the gdal globally first using the following instructions extracted from https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html

```bash
sudo add-apt-repository ppa:ubuntugis/ppa && sudo apt-get update
sudo apt-get update
sudo apt-get install gdal-bin
sudo apt-get install libgdal-dev
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip3 install GDAL
pip3 install pygdal=="`gdal-config --version`.*"

# install geoserver-rest globally. geoserver-rest will not install in virtual environment so you can comment it out in the requirements.txt file while setting up 
# for developer setup. However, for production
pip install geoserver-rest
```

### Step 2. Install gdal inside virtual environment

* Create a virtual environment and also grant it access to system wide packages

```bash
virtualenv --system-site-packages --python=python3.8 env

```
* Install gdal within a virtual environment

See https://stackoverflow.com/questions/32066828/install-gdal-in-virtualenvwrapper-environment

1. Run the below command to get the output of gdal version

```bash
gdal-config --version
```
Take note of the output of the above command

1. Activate the virtual environment 
1. Run the following command

```bash
pip install pygdal==<VERSION_OUTPUT_BY_gdal-config --version command> e.g pip install pygdal==3.3.2
``` 