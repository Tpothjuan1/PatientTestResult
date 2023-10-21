"""
Name:Juan Sanchez Moreno
Date:10/13/2022
Assignment: Module 7: Send Encrypted Message
Due Date:10/15/2023
About this project: This script will run the DDL statements to create a SQLite DB storing patient test result information
Some pre-existing data is added with table creation.
Assumptions:NA
All work below was performed by Juan Sanchez
"""

###############IMPORTS  #######################

import sqlite3 as sql
import Encryption

## Connecting to the DB
conn = sql.connect("HospitalUsersCreateDB.db")

## Cursor to execute statements on DBMS
cursor = conn.cursor()

## Dropping the PatientTestResult  table
cursor.execute("DROP TABLE IF EXISTS PatientTestResult;")
print("Table PatientTestResult dropped")


## DDL for PatientTestResult table
cursor.execute(
    """CREATE TABLE PatientTestResult (
               TestResultId INTEGER PRIMARY KEY,
               UserId INTEGER,
               TestName TEXT,
               TestResult TEXT,
               FOREIGN KEY(UserId) REFERENCES HospitalUser(UserId));"""
)

print("Table PatientTestResult created")

results = [
    [1, 2, "Blood work", "positive"],
    [2, 5, "Covid Test", "positive"],
    [3, 4, "Biopsy", "undetermined"],
    [4, 6, "Blood work", "positive"],
    [5, 1, "Covid Test", "negative"],
    [6, 3, "Eye exam", "positive"],
]

# DML
# loop to inser 1 test result at a time
## Encrypt test name and test result
for result in results:
    tId = result[0]
    uId = result[1]
    tName = Encryption.theCypher.Encrypt(result[2].encode("utf-8"))
    tResult = Encryption.theCypher.Encrypt(result[3].encode("utf-8"))

    cursor.execute(
        """INSERT INTO PatientTestResult(TestResultId, UserId, TestName, TestResult)
                    VALUES
                    (?, ?, ?, ?);""",
        (tId, uId, tName, tResult),
    )

    ## Commit the table
    conn.commit()

# Show contents of the table
rows = cursor.execute("SELECT * FROM PatientTestResult;").fetchall()
for row in rows:
    print(row)

## Close the cursor and connection when done
cursor.close()
conn.close()

print("Connection Closed")
