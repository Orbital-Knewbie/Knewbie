# Knewbie
Web Application built using Flask and React

## Getting Started

### Prerequisites
* [Git](https://git-scm.com/)
* [Python 3](https://www.python.org/downloads/)
* [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
### Pre-Installation
Setting up on WSL notably produces some errors if the installation steps were to be taken immediately. This section will try to help prevent this by providing the commands taken before actual installation.
1. [A common `apt hook` error that appears on WSL](https://askubuntu.com/questions/1123159/broken-apt-on-wsl-18-04) can be fixed by removing it. You may want to save a backup just in case.
###### WSL only
```
sudo rm -rf /etc/apt/apt.conf.d/20snapd.conf
```
2. Due to the [Common Build Problems using `pyenv`](https://github.com/pyenv/pyenv/wiki/Common-build-problems), if using Linux/WSL, there is a need to install `libsqlite3-dev` before getting started. See this [StackOverflow answer](https://stackoverflow.com/questions/39907475/cannot-import-sqlite3-in-python3) for more information regarding the commands used.
###### Linux/WSL only
```
sudo apt-get install build-essential
sudo apt-get install libsqlite3-dev 
sudo apt-get remove python3.6
cd /tmp && wget https://www.python.org/ftp/python/3.6.10/Python-3.6.10.tgz
tar -xvf Python-3.6.10.tgz
cd Python-3.6.10 && ./configure
make && sudo make install
```

### Installing
Commands given should be carried out on the command line. Commands were tested on Windows and [WSL](https://docs.microsoft.com/en-us/windows/wsl/about) and Python 3.6 was used for development.


1. Clone this repo and enter the folder.
###### Both Linux/WSL and Windows
```
git clone https://github.com/Orbital-Knewbie/Knewbie
cd Knewbie
```
2. Install, then create a Python 3 `virtualenv`.
###### Both Linux/WSL and Windows
```
sudo pip3 install virtualenv
virtualenv -p python3 venv
```
3. Enter ```virtualenv```.
###### Linux/WSL only
```
source venv/bin/activate
```
###### Windows only
```
venv\Scripts\activate
```
5. Install dependencies. If there are missing modules, it can likely be fixed with `pip install`.
###### Both Linux/WSL and Windows
```
pip install -r requirements.txt
```
6. Set the environment variable. Note that there is no spacing around `=`.
###### Linux/WSL only
```
export FLASK_APP=run.py
```
###### Windows only
```
set FLASK_APP=run.py
```
7. Run the application.
###### Both Linux/WSL and Windows
```
flask run
```
8. Open up `localhost:5000` on a browser of your choice.

## Built With

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - The web framework used
