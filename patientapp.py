"""
Name:Juan Sanchez Moreno
Date:10/13/2022
Assignment: Module 7: Send Encrypted Message
Due Date:10/15/2023
About this project: This document will leverage flask to create a simple
HTML site that uses sessions to manage accounts and actions user can do 
on the app depending on their level of security. Sensitive data is encrypted in the DB.
It incorporates a socket connection to a server to add results to the tests table.
Assumptions:NA
All work below was performed by Juan Sanchez
"""

###############IMPORTS  #######################

from flask import Flask, render_template, request, session, flash, abort
import sqlite3 as sql
import os
import Encryption
import socket

############### HELPER FUNCTIONS  #######################


##IsBlank returns true is a string is empty or made up of only
##Whitespaces
def IsBlank(someString):
    temp = someString.strip()
    if len(temp) == 0:
        return True
    else:
        return False


## IsNumericBetween returns true if the input string represents
## a numeric value between the low and high numbers. Else, it
## Returns false
## Referenced from 101computing.net/number-only/
def IsNumericBetween(inp, low=0, high=10000000000):
    try:
        userInput = int(inp)
    except ValueError:
        return False

    if userInput < low or userInput > high:
        return False
    else:
        return True


## Flask app instantiation

app = Flask(__name__)


## Home Render. Depends on session value
@app.route("/")
def home():
    if not session.get("loggedIn"):
        return render_template("login.html")
    else:
        return render_template("home.html", name=session["uName"])


## Login mechanism that reports issues using Flash messages
@app.route("/login", methods=["POST"])
def loginUser():
    # Connect to the DB
    connect = sql.connect("HospitalUsersCreateDB.db")

    try:
        # Retreive username and password from form
        uname = request.form["username"].encode("utf-8")
        pword = request.form["password"].encode("utf-8")
        # encrypt username
        uname = Encryption.theCypher.Encrypt(uname)
        # encrypt password
        pword = Encryption.theCypher.Encrypt(pword)

        # Return dicts
        connect.row_factory = sql.Row

        # Get cursor to execute
        cur = connect.cursor()

        rows = cur.execute(
            "SELECT * FROM HospitalUser WHERE UserName=? AND LoginPassword=?;",
            (uname, pword),
        ).fetchone()

        # Successful login
        if rows != None:
            session["uName"] = Encryption.theCypher.Decrypt(uname)
            session["loggedIn"] = True
            session["secLevel"] = rows["SecurityLevel"]
        # Failed login
        else:
            session["loggedIn"] = False
            flash(
                "This user/password combination doesn't exist. Please try valid credentials"
            )
    # Failed Query/execution
    except:
        flash("Input error, please try again")
    finally:
        connect.close()

    return home()


@app.route("/logout")
def logout():
    session["uName"] = ""
    session["secLevel"] = 0
    session["loggedIn"] = False
    return home()


## Show user information only if user is logged in
@app.route("/showuser")
def showUser():
    if not session.get("loggedIn"):
        abort(404)
    else:
        ## Get info from database

        # Connect to the DB
        connect = sql.connect("HospitalUsersCreateDB.db")
        # Get dictionary instead of tuple from fetch
        connect.row_factory = sql.Row
        # Get cursor to execute
        cur = connect.cursor()
        # Get rows
        row = cur.execute(
            "SELECT * FROM HospitalUser WHERE UserName= ?;",
            (Encryption.theCypher.Encrypt(session["uName"].encode("utf-8")),),
        ).fetchone()

        # Decrypt data to display plaintext
        sensitive = {}
        sensitive["uName"] = Encryption.theCypher.Decrypt(row["UserName"])
        sensitive["pNum"] = Encryption.theCypher.Decrypt(row["UserPhNum"])
        sensitive["pw"] = Encryption.theCypher.Decrypt(row["LoginPassword"])

        # Close cursor
        cur.close()
        # Close Connection
        connect.close()

        return render_template("showuser.html", row=row, sensitive=sensitive)


## Show table Render
@app.route("/table")
def ShowTable():
    # Only do this if level 3

    if session.get("loggedIn") and session["secLevel"] > 2:
        # Connect to the DB
        connect = sql.connect("HospitalUsersCreateDB.db")
        # Get dictionary instead of tuple from fetch
        connect.row_factory = sql.Row
        # Get cursor to execute
        cur = connect.cursor()
        # Get rows
        rows = cur.execute("SELECT * FROM HospitalUser;").fetchall()

        # Create list of dicts from rows to be able to decrypt the data
        rowdicts = [dict(row) for row in rows]
        # for each row decrypt the sensitive info
        for rd in rowdicts:
            rd["UserName"] = Encryption.theCypher.Decrypt(rd["UserName"])
            rd["UserPhNum"] = Encryption.theCypher.Decrypt(rd["UserPhNum"])
            rd["LoginPassword"] = Encryption.theCypher.Decrypt(rd["LoginPassword"])

        ## Close cursor
        cur.close()

        return render_template("table.html", rows=rowdicts)

    # Not authorized
    else:
        abort(404)


## Add new patient form
@app.route("/addform")
def NewPatient():
    # Show only if user security level is 2 or 3
    if session.get("loggedIn") and session["secLevel"] > 1:
        return render_template("patient.html")
    else:
        abort(404)


## Add a new test form
@app.route("/addformtest")
def addformtest():
    # Show only if user security level is 2 or 3
    if session.get("loggedIn") and session["secLevel"] > 1:
        return render_template("addtest.html")
    else:
        abort(404)


## Method to receive the user form and provide results
@app.route("/transf", methods=["POST", "GET"])
def transf():
    # Check user has enough permission
    if session.get("loggedIn") and session["secLevel"] > 1:
        if request.method == "POST":
            ##Flag is 0 is input is correct
            flag = 0

            name = request.form["Name"]
            age = request.form["Age"]
            phn = request.form["PhoneNumber"]
            seclvl = request.form["SecurityLevel"]
            pw = request.form["Password"]

            ##Covid checkbox
            if request.form.get("HasCovid") == None:
                hascovid = 0
            else:
                hascovid = 1

            ##Input checks
            if IsBlank(name):
                flash("Name is Blank please input a valid name")
                flag = 1

            if not (IsNumericBetween(age, 1, 120)):
                flash(
                    "Age is invalid please input a whole number greater than 0 and less than 121"
                )
                flag = 1
            else:
                age = int(age)

            if IsBlank(phn):
                flash("Phone Number is Blank please input a valid name")
                flag = 1

            if not (IsNumericBetween(seclvl, 1, 3)):
                flash(
                    "Security level is invalid please input a whole number between 1 and 3"
                )
                flag = 1
            else:
                seclvl = int(seclvl)

            if IsBlank(pw):
                flash("Password is Blank please input a valid password")
                flag = 1

            ## If successfull

            if flag == 0:
                flash("Successful Input")

                # Encrypt sentitive data before insertion
                name = Encryption.theCypher.Encrypt(name.encode("utf-8"))
                phn = Encryption.theCypher.Encrypt(phn.encode("utf-8"))
                pw = Encryption.theCypher.Encrypt(pw.encode("utf-8"))

                # Connect to the DB
                connect = sql.connect("HospitalUsersCreateDB.db")
                # Get cursor to execute
                cur = connect.cursor()

                ## Insert into Table

                cur.execute(
                    """
                    INSERT INTO HospitalUser (UserName, UserAge, UserPhNum, UserHasCOVID, SecurityLevel, LoginPassword)
                    VALUES (?,?,?,?,?,?)
                    """,
                    (name, age, phn, hascovid, seclvl, pw),
                )

                # Commit change
                connect.commit()

                # Close connection
                connect.close()

        return render_template("patient.html")

    else:
        abort(404)


## Method to receive the test result form
@app.route("/addtest", methods=["POST"])
def addtest():
    ## make sure user is logged in and has the permissions
    if session.get("loggedIn") and session["secLevel"] > 1:
        if request.method == "POST":
            ## input verification flag
            flag = 0

            userid = request.form["userId"]
            testname = request.form["testName"]
            testresult = request.form["testResult"]

        ## Input verification

        # user id is numeric > 0
        if not (IsNumericBetween(userid, 1)):
            flash("Please input a numeric value greater than 0")
            flag = 1
        else:
            userid = int(userid)

        # Test name is not empty
        if IsBlank(testname):
            flash("test name is Blank please input a valid test name")
            flag = 1

        # Test result is not empty
        if IsBlank(testresult):
            flash("test result is Blank please input a valid test result")
            flag = 1

        ## Successful input
        if flag == 0:
            # Try a connection to the server
            try:
                ## Server connection block
                HOST, PORT = "localhost", 9999
                sokt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sokt.connect((HOST, PORT))

                ## Using '^' as a separator between elements of the message
                message = [str(userid), testname, testresult]
                message = "^".join(message)

                ## Encrypt the whole message before sending
                cipher = Encryption.theCypher.Encrypt(message.encode("utf-8"))

                ## Send the ciphertext
                sokt.sendall(cipher)

                ## Close the connection
                sokt.close()

                flash("Test Results Accepted")

            # Couldn't make the connection to the server
            except:
                flash("The server couldn't be reached please try later")

        return render_template("addtest.html")

    ## Not logged in or not permissions
    else:
        abort(404)


## Show test results table
@app.route("/showresults")
def showresults():
    ## Verify user is logged in backend
    if session.get("loggedIn") and session["secLevel"] > 0:
        connect = sql.connect("HospitalUsersCreateDB.db")
        # Get dictionary instead of tuple from fetch
        connect.row_factory = sql.Row
        # Get cursor to execute
        cur = connect.cursor()
        # Encrypt username to run sql query
        encryptedUname = Encryption.theCypher.Encrypt(session["uName"].encode("utf-8"))
        # Get rows
        rows = cur.execute(
            """
                           SELECT TestName, TestResult 
                           FROM PatientTestResult
                           JOIN HospitalUser 
                           ON HospitalUser.UserId = PatientTestResult.UserId
                           WHERE HospitalUser.UserName = ?
                           ;""",
            (encryptedUname,),
        ).fetchall()

        # Create list of dicts from rows to be able to decrypt the data
        rowdicts = [dict(row) for row in rows]
        # for each row decrypt the sensitive info
        for rd in rowdicts:
            rd["TestName"] = Encryption.theCypher.Decrypt(rd["TestName"])
            rd["TestResult"] = Encryption.theCypher.Decrypt(rd["TestResult"])

        ## Close cursor
        cur.close()

        return render_template("testresults.html", rows=rowdicts)

    ## not logged in or authorized
    else:
        abort(404)


## Run app
if __name__ == "__main__":
    # Random generator for session
    app.secret_key = os.urandom(12)
    # Run app
    app.run(debug=True)
