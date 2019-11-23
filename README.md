# Obar Backend

Backend for a product vendor application made with Flask framework. 

## Installation

Clone the repo with:
```
git clone https://github.com/randomBEAR/obar_backend.git
```
Create a new Python virtual environment (or don't) 
and install the required modules. Open the terminal in the project folder and run
```
pip install -r requirements.txt
```

After having installed all the modules add these two environment variables 
to your terminal session:

If you are on Linux:
```
$ export FLASK_APP=obar
$ export FLASK_ENV=development
```
On Windows:
```
$ set FLASK_APP=obar
$ set FLASK_ENV=development
```
In order to run properly, Obar needs a SQLite database. To create one open start 
Python from CLI in the same project folder and insert these commands:
```
>>> from obar import create_app
>>> from obar.models import db
>>> db.create_all(app=create_app())
```
If imports keep failing, check if your Python working directory is correct:
```
>>> import os
>>> os.getcwd()
```
A file named obar_database.db should be created in `/obar`. To run the application 
type in your console:
```
flask run
```
The application will be running on http://127.0.0.1:5000/ .
