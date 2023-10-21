"""
Name:Juan Sanchez Moreno
Date:10/13/2022
Assignment: Module 7: Send Encrypted Message
Due Date:10/15/2023
About this project: This script will run the DDL and DML statements to create a SQLite DB storing patient information
Some pre-existing data is added with table creation. It also encrypts sensitive data inside the database
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

## Dropping the HospitalUser  table
cursor.execute("DROP TABLE IF EXISTS HospitalUser ;")
print("Table HospitalUser dropped")

## Creating the patient table
## UserID as primary key that will auto-increment with each new user
cursor.execute(
    """CREATE TABLE HospitalUser (
               UserId INTEGER PRIMARY KEY,
               UserName TEXT,
               UserAge INTEGER,
               UserPhNum TEXT,
               UserHasCOVID INTEGER,
               SecurityLevel INTEGER,
               LoginPassword TEXT);"""
)

print("Table HospitalUser created")

users = [
    [1, "JMaxwell", 34, "123-675-7645", 0, 1, "test123"],
    [2, "NielsBohr", 68, "895-345-6523", 1, 2, "test123"],
    [3, "DBernoulli", 29, "428-197-3967", 0, 3, "test123"],
    [4, "NoetherE", 37, "239-567-3498", 1, 2, "test123"],
    [5, "MdmeCurie", 67, "407-825-9898", 1, 2, "radium123"],
    [6, "BRiemann", 23, "619-705-8887", 0, 3, "mathrules"],
]

# loop to inser users 1 by one and encrypt sensitive data
for user in users:
    uId = user[0]
    uName = Encryption.theCypher.Encrypt(user[1].encode("utf-8"))
    age = user[2]
    phNum = Encryption.theCypher.Encrypt(user[3].encode("utf-8"))
    hasCov = user[4]
    secLvl = user[5]
    pw = Encryption.theCypher.Encrypt(user[6].encode("utf-8"))

    ## Add initial data into the database
    cursor.execute(
        """INSERT INTO HospitalUser(UserId, UserName, UserAge, UserPhNum, UserHasCOVID, SecurityLevel, LoginPassword)
                VALUES
                (?, ?, ?, ?, ?, ?, ?);""",
        (uId, uName, age, phNum, hasCov, secLvl, pw),
    )

    ## Commit the table
    conn.commit()

# Show contents of the table
rows = cursor.execute("SELECT * FROM HospitalUser;").fetchall()
for row in rows:
    print(row)

## Close the cursor and connection when done
cursor.close()
conn.close()

print("Connection Closed")
