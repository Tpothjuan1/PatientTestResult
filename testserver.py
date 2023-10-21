"""
Name:Juan Sanchez Moreno
Date:10/13/2022
Assignment: Module 7: Send Encrypted Message
Due Date:10/15/2023
About this project: Script to launch server that receives a string message
decrypts it, validates it, and adds it to the test results table
Assumptions:NA
All work below was performed by Juan Sanchez
"""

import socketserver
import Encryption
import sqlite3 as sql
from patientapp import IsBlank

# Custom handler


class myHandler(socketserver.BaseRequestHandler):
    def handle(self):
        ## Using strip to remove extra bytes
        self.data = self.request.recv(1024).strip()
        self.plaintext = Encryption.theCypher.Decrypt(self.data)

        # Print client's address
        print("{}	sent message:	".format(self.client_address[0]))

        # Print received message
        print("Message Received: {}".format(self.plaintext))

        # split into individual data elements
        self.dataList = self.plaintext.split("^")

        # validations
        self.flag = 0

        # 3 elements
        if not (len(self.dataList) == 3):
            print("Invalid input format")
            return

        # user id to int
        self.dataList[0] = int(self.dataList[0])

        # zip input with labels
        self.fields = ["UserId", "TestName", "TestResult"]
        self.inputDict = dict(zip(self.fields, self.dataList))

        # Validate user id
        try:
            # Connect to the DB
            self.connect = sql.connect("HospitalUsersCreateDB.db")
            # Get cursor to execute
            self.cur = self.connect.cursor()

            rows = self.cur.execute(
                """
                SELECT *
                FROM HospitalUser
                WHERE UserId = ?;
                """,
                (self.inputDict["UserId"],),
            ).fetchone()

        except:
            print("Error fetching data")
            self.connect.close()
            return

        if rows == None:
            print("Invalid user Id")
            self.flag = 1

        # Validate Test Name
        if IsBlank(self.inputDict["TestName"]):
            print("Test name is Blank please input a valid test name")
            self.flag = 1

        # Validate Test Result
        if IsBlank(self.inputDict["TestResult"]):
            print("Test result is Blank please input a valid test result")
            self.flag = 1

        ## If input is valid
        if self.flag == 0:
            try:
                # Encrypt before inserting
                self.inputDict["TestName"] = Encryption.theCypher.Encrypt(
                    self.inputDict["TestName"].encode("utf-8")
                )
                self.inputDict["TestResult"] = Encryption.theCypher.Encrypt(
                    self.inputDict["TestResult"].encode("utf-8")
                )

                # Insert into the test results table
                self.cur.execute(
                    """
                INSERT INTO PatientTestResult(UserId, TestName, TestResult)
                    VALUES
                    (?, ?, ?);""",
                    (
                        self.inputDict["UserId"],
                        self.inputDict["TestName"],
                        self.inputDict["TestResult"],
                    ),
                )

                self.connect.commit()

                print("Results successfully added")

            except:
                print("error inserting the data. insertion aborted")
                self.connect.close()
                return

        # flag is not zero invalid input
        else:
            print("Entry not added")

        # Close connection
        self.connect.close()


# Server run

if __name__ == "__main__":
    try:
        HOST, PORT = "localhost", 9999

        ## Instantiate the server
        svr = socketserver.TCPServer((HOST, PORT), myHandler)

        ## Keep the server running continously
        svr.serve_forever()

    except svr.error as e:
        print("Error: ", e)
        exit(1)

    finally:
        svr.close()
