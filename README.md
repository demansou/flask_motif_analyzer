flask_motif_analyzer
====================
  
  **Author:** Daniel Mansour  
  **Organization:** University of St. Thomas (Houston, TX)  
  **Created for:** Dr. Albert Ribes-Zamora & Dr. Maia Larios-Sanz  
Requirements
============

  1. Linux (Tested w/ Ubuntu 16.04 LTS)
  2. Git
  3. Python 3.5.2
  4. Apache2
  5. mod_wsgi
  6. MongoDB
  7. Celery
  8. Python packages as listed in `requirements.txt`
 
Installation Documentation
==========================

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

7. Install package requirements
-------------------------------
Use pip to install `flask_motif_analyzer` requirements. Ensure that the virtual environment is activated.  
`cd ~/flask_motif_analyzer && pip install -r requirements.txt`  

At this point, the server can run locally using `aws_debug.py`. However, this produces a single-threaded server which won't stand the rigors of multiple requests. Luckily, Python and Flask integrate fairly easily with Apache2 using `mod_wsgi` which provides a WSGI interface for Python web applications.

8. Install Apache2
------------------
Apache2 comes preinstalled with Ubuntu as a service. It can be controlled using `sudo service apache2 start|stop|restart`. However, the default Apache2 does not come preinstalled with `mod_wsgi` which is needed for Python web applications. Therefore, we must install a standalone version of Apache2 for this next step. To be clear, we will be using the Apache2 service in the end, but this is a needed, if troublesome, part of the process.  
`sudo apt-get update && sudo apt-get install apache2 apache2-dev`

9. Install and configure `mod_wsgi`
---------------------
*Full documentation can be found at https://pypi.python.org/pypi/mod_wsgi*  
At this point, you should still be in your Python virtual environment. If not, repeat step 6 before continuing.  
**1. Install `mod_wsgi`**  
`pip install mod_wsgi`  
**2. Get needed info**  
`sudo mod_wsgi-express install-module`  
> LoadModule wsgi_module "/usr/lib/apache2/modules/mod_wsgi-py35.cpython-35m-x86_64-linux-gnu.so"  
> WSGIPythonHome "/home/ubuntu/flask_motif_analyzer/venv/bin/python" 

# more to come...
