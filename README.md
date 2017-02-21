flask_motif_analyzer
====================
  
  **Author:** Daniel Mansour  
  **Organization:** University of St. Thomas (Houston, TX)  
  **Created for:** Dr. Albert Ribes-Zamora & Dr. Maia Larios-Sanz  
Requirements
============

  1. Linux (Tested w/ Ubuntu 16.04 LTS)
  2. Python 3.5.2
  3. Git
  4. Apache2
  5. mod_wsgi
  6. MongoDB
  7. Celery
  8. Python packages as listed in `requirements.txt`
 
Installation Documentation
==========================
## This following documentation is for a clean install of `flask_motif_analyzer` using a fresh Amazon AWS Ubuntu 16.04 LTS Virtual Server.  
*Note that `flask_motif_analyzer` has a Python module name of `motif_analyzer`.*  
*If you already have a partial installation or use a different WSGI server, please feel free to skip those parts!*  

1. Server
---------

We recommend Amazon AWS for hosting. [https://aws.amazon.com/]  
We tested installation on Ubuntu 16.04 LTS. This is an available Virtual Machine selection for AWS.

2. Python Installation
----------------------

**1. Download Prereqs**  
`sudo apt-get update && sudo apt-get install build-essential checkinstall && sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev`  
**2. Download Python 3.5.2**  
`cd ~ && wget https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz`  
**3. Install Python**  
When configuring for install, `--enabled-shared` is important for installing `mod_wsgi` later  
`sudo tar xzf Python-3.5.2.tgz && cd Python-3.5.2 && sudo ./configure --enable-shared && sudo make altinstall`  
**4. Check Python Version**  
`python3.5 -V`  
> Python 3.5.2

**5. Update Pip**  
`pip3.5 install --upgrade pip`

3. Install Git
--------------
Git is needed to install this package.  
`sudo apt-get install git`

4. Install `flask_motif_analyzer`
---------------------------------
Installing this module in the home directory will make it easier to configure the Apache server later.  
`cd ~ && git clone https://github.com/demansou/flask_motif_analyzer`

5. Install a virtual environment
--------------------------------
Install a virtual environment in the `flask_motif_analyzer` base directory. You don't want to install the required package modules for the global Python install. It makes it hard to keep track of which requirements are for which projects. A virtual environment enables a local Python 3.5.2 install specifically for this project.  
`cd ~/flask_motif_analyzer && python3.5 -m venv ~/flask_motif_analyzer/venv`

6. Activate the virtual enviroment
----------------------------------
**1. Activate the virtual environment**  
`cd ~/flask_motif_analyzer && source venv/bin/activate`  
**2. Check Python version and install location**  
`python -V && which python`  
> Python 3.5.2  
> /home/ubuntu/flask_motif_analyzer/venv/bin/python

**3. Upgrade pip**  
`pip install --upgrade pip`  

7. Install `flask_motif_analyzer` package requirements
------------------------------------------------------
Use pip to install `flask_motif_analyzer` requirements. Ensure that the virtual environment is activated.  
`cd ~/flask_motif_analyzer && pip install -r requirements.txt`  

At this point, the server can run locally using `aws_debug.py`. However, this produces a single-threaded server which won't stand the rigors of multiple requests. Luckily, Python and Flask integrate fairly easily with Apache2 using `mod_wsgi` which provides a WSGI interface for Python web applications.

8. Install Apache2
------------------
Apache2 comes preinstalled with Ubuntu as a service. It can be controlled using `sudo service apache2 start|stop|restart`. However, the default Apache2 does not come preinstalled with `mod_wsgi` which is needed for Python web applications. Therefore, we must install a standalone version of Apache2 for this next step. To be clear, we will be using the Apache2 service in the end, but this is a needed, if troublesome, part of the process.  
**Default Apache2 Service:** `/etc/apache2`  
**Apache2 Installed Package:** `/usr/lib/apache2`  
`sudo apt-get update && sudo apt-get install apache2 apache2-dev`

9. Install and configure `mod_wsgi`
-----------------------------------
*Full documentation can be found at https://pypi.python.org/pypi/mod_wsgi*  
At this point, you should still be in your Python virtual environment. If not, repeat step 6 before continuing.  
**1. Install `mod_wsgi`**  
`pip install mod_wsgi`  
**2. Get needed info**  
`sudo mod_wsgi-express install-module`  
> LoadModule wsgi_module "/usr/lib/apache2/modules/mod_wsgi-py35.cpython-35m-x86_64-linux-gnu.so"  
> WSGIPythonHome "/home/ubuntu/flask_motif_analyzer/venv/bin/python"  

**3. Create backup of and append `/etc/apache2/apache2.conf` config file**  
`sudo cp /etc/apache2/apache2.conf /etc/apache2/apache2.conf.old && sudo echo "LoadModule wsgi_module \"/usr/lib/apache2/modules/mod_wsgi-py35.cpython-35m-x86_64-linux-gnu.so\"" | sudo tee -a /etc/apache2/apache2.conf && sudo echo "WSGIPythonHome \"/home/ubuntu/flask_motif_analyzer/venv/bin/python\"" | sudo tee -a /etc/apache2/apache2.conf`  
*We'll restart Apache2 to enable the config updates after the next step*

10. Create Apache2 site config file
-----------------------------------
**1. Create config file to write to**  
`cd ~ && vim flask_motif_analyzer.conf`  
**2. Copy config text to open vim editor file (insert text with `:i`, escape from insertion mode with escape key, save with `:wq`)**  
```
<VirtualHost *:80>
        WSGIDaemonProcess flask_motif_analyzer threads=5 user=ubuntu group=ubuntu
        WSGIScriptAlias / /var/www/flask_motif_analyzer/motif_analyzer.wsgi

        <directory /var/www/flask_motif_analyzer>
                WSGIProcessGroup flask_motif_analyzer
                WSGIApplicationGroup %{GLOBAL}
                WSGIScriptReloading On
                Require all granted
        </Directory>

        ErrorLog ${APACHE_LOG_DIR}/error.log
        LogLevel info
        CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>
```  
**3. Create symlink with saved config file**  
`sudo ln -s /home/ubuntu/flask_motif_analyzer.conf /etc/apache2/sites-available`  
**4. Enable site with `a2ensite`**  
`cd /etc/apache2/sites-available && sudo a2ensite flask_motif_analyzer.conf && sudo service apache2 restart`  

11. Symlink `flask_motif_analyzer` package directory into `/var/www`
--------------------------------------------------------------------
If you noticed in the Apache2 config file, the directory link to `flask_motif_analyzer` was `/var/www`. This is the default location of Apache's web server and it's good to follow the config. However, we're going to make it simple and maintain the default user/group settings for our file now.  
`sudo ln -s /home/ubuntu/flask_motif_analyzer /var/www`  
*If you want more security, go ahead and move the directory over. It's fairly easy to do so.*  

# more to come...
12. MongoDB setup
-----------------
13. Celery setup
----------------
