from os import getenv
from shutil import copyfile

from flask import Flask, request
from flask import render_template
from covid_app.controllers.database_helpers import connect_to_database
from covid_app.controllers.database_helpers import close_conection_to_database
from covid_app.controllers.database_helpers import change_database
from covid_app.controllers.database_helpers import query_database

import datetime


app = Flask(__name__)

# This is a terrible example of how to configure a flask.
# this type of configuration should be done in a separate file,
# using environment variables. The code is written this way for
# relative ease of reading - but the code gets out of hand very
# quickly if you follow this approach.

# local file for testing purposes
app.config['DATABASE_FILE'] = 'covid_app/data/covid_app.sqlite'

# hack to run with sqlite on app engine: if the code is run on app engine,
# this will copy the existing database to a writeable tmp directory.
# note that it will get overwritten every time you deploy! a production-ready
# approach is to store the file long-term on google cloud storage,
# or, better yet, use fully managed  relational database management software
# via Cloud SQL.
if getenv('GAE_ENV', '').startswith('standard'):
    app_engine_path = "/tmp/covid_app.sqlite"
    copyfile(app.config['DATABASE_FILE'], app_engine_path)
    app.config['DATABASE_FILE'] = app_engine_path
else:
    pass


@app.route('/')
def index():
    return render_template('index.html', page_title="Covid Diary")


@app.route('/register', methods=['GET', 'POST'])
def create_person():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            phone_number = request.form.get('telephone')

            sql_insert = "INSERT INTO Contacts (name, email, phone_number) VALUES (\"{name}\", \"{email}\", \"{phone_number}\");".format(
                name=name, email=email, phone_number=phone_number)

            database_tuple = connect_to_database(app.config["DATABASE_FILE"])
            change_database(database_tuple[0], database_tuple[1], sql_insert)

            # select all the names for the form selector
            sql_query = "SELECT name FROM Contacts ORDER BY name ASC;"

            query_response = query_database(database_tuple[1], sql_query)
            close_conection_to_database(database_tuple[0])

            return render_template('index.html', page_title="Covid Diary",
                               names=query_response), 201
        except Exception:
            # something bad happended. Return an error page and a 500 error
            error_code = 500
            return render_template('error.html', page_title=error_code), error_code
    else:
        return render_template("register.html", page_title="Register new user")

@app.route('/create', methods=['POST'])
def create_meeting():
    try:
        name = request.form.get('name')
        time = request.form.get('time')
        date = request.form.get('day').split("-")
        date = datetime.date(int(date[0]), int(date[1]), int(date[2]))

        # getting the person_id from Contacts with the name
        # app.logger.info(name)
        # turn this into an SQL command. For example:
        # "Adam" --> "INSERT INTO Meetings (name) VALUES("Adam");"

        # connect to the database with the filename configured above
        # returning a 2-tuple that contains a connection and cursor object
        # --> see file database_helpers for more
        database_tuple = connect_to_database(app.config["DATABASE_FILE"])

        sql_query = "SELECT id FROM Contacts WHERE name = (\"{name}\");".format(
            name=name)
        query_response = query_database(database_tuple[1], sql_query)

        # now that we have connected, add the new meeting (insert a row)
        # --> see file database_helpers for more
        sql_insert = "INSERT INTO Meetings (person_id,time, date) VALUES (\"{person_id}\", \"{time}\", \"{date}\");".format(
            person_id=query_response[0][0],time=time, date=date)
        change_database(database_tuple[0], database_tuple[1], sql_insert)

        # now, get all of the meetings from the database, not just the new one.
        # first, define the query to get all meetings:

        sql_query = "SELECT * FROM Meetings WHERE date BETWEEN datetime('now', '-13 days') AND datetime('now', 'localtime') ORDER BY date ASC;"

        # query the database, by passinng the database cursor and query,
        # we expect a list of tuples corresponding to all rows in the database
        query_response = query_database(database_tuple[1], sql_query)

        close_conection_to_database(database_tuple[0])

        # In addition to HTML, we will respond with an HTTP Status code
        # The status code 201 means "created": a row was added to the database
        return render_template('index.html', page_title="Covid Diary",
                               meetings=query_response), 201
    except Exception:
        # something bad happended. Return an error page and a 500 error
        error_code = 500
        return render_template('error.html', page_title=error_code), error_code


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
