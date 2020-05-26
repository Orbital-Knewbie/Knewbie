# Knewbie
Web Application built using Flask and React

## Getting Started

### Prerequisites
* [Git](https://git-scm.com/)
* [Python 3](https://www.python.org/downloads/)
### Installing
Commands given should be carried out on the command line. Commands were tested on [WSL](https://docs.microsoft.com/en-us/windows/wsl/about) and [MVS](https://visualstudio.microsoft.com/vs/) was used for development.
1. Clone this repo and enter the folder.
```
git clone https://github.com/Orbital-Knewbie/Knewbie
cd Knewbie
```
2. Install, then create a `virtualenv`.
```
pip install virtualenv
virtualenv venv
```
3. Enter ```virtualenv```.
```
source venv/bin/activate
```
* If Step 2 was done on the Windows command line, then do
```
venv\Scripts\activate
```
4. Install dependencies. If there are missing modules, it can likely be fixed with `pip install`.
```
pip install -r requirements.txt
```
5. Set the environment variable. Note that there is no spacing around `=`.
```
export FLASK_APP=run.py
```
* If on Windows, do
```
set FLASK_APP=run.py
```
6. Run the application.
```
flask run
```
7. Open up `localhost:5000` on a browser of your choice.

## Built With

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - The web framework used
