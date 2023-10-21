"""
Name:Juan Sanchez Moreno
Date:10/21/2022
Assignment: Module 8: Send Authenticated Message
Due Date:10/22/2023
About this project: Script to start up a server that listens on port 8888
for messages to update the testresutls table. It will receive an ecrypted message
along with an HMAC tag for authentication.
Assumptions:NA
All work below was performed by Juan Sanchez
"""

import socketserver
import Encryption
import sqlite3 as sql
from patientapp import IsBlank, IsNumericBetween
import hmac, hashlib


class myHandler(socketserver.BaseRequestHandler):
    def myHandler(self):
        # unsecure key
        authSecret = b"this not not safe at all"
        splitString = "^%@*"

        # Receive the data with strip to remove extra bytes
        self.data = self.request.recv(1024).strip()

        # Separate encrypted message form HMAC. HMAC is using SHA3-512
        self.encryptedMsg = self.data[-64:]
        self.hmacTag = self.data[:-64]

        # Need to unencrypt message first
        self.rcvdPlaintxt = Encryption.theCypher.Decrypt(self.encryptedMsg)

        # Authenticate message
        self.computedTag = hmac.new(
            authSecret, self.rcvdPlaintxt, hashlib.sha3_512
        ).digest()

        # tags invalid signature
        if self.computedTag != self.hmacTag:
            print(
                "Unauthenticated Test Result Update received! Be on alert! Watch out for bad guys !!!"
            )

        # valid signature
        else:
            # split input
            self.testid, self.result = self.rcvdPlaintxt.split(splitString)

            # input validation
            self.validFlag = True

            if not (IsNumericBetween(self.testid)):
                print("Test id is not an integer in the correct range")
                self.validFlag = False

            else:
                # Make into integer
                self.testid = int(self.testid)

                try:
                    # Connect to the DB
                    self.connect = sql.connect("HospitalUsersCreateDB.db")
                    # Get cursor to execute
                    self.cur = self.connect.cursor()

                    rows = self.cur.execute(
                        """
                        SELECT *
                        FROM PatientTestResult
                        WHERE TestResultId = ?;
                        """,
                        (self.testid,),
                    ).fetchone()

                    # no existing test id found
                    if rows == None:
                        print("Test ID couldn't be found")
                        self.validFlag = False

                except:
                    print("Error fetching data")

                finally:
                    self.connect.close()

            # Validating test result
            if IsBlank(self.result):
                print("Test result can't be empty")
                self.validFlag = False

            # post validation insert update

            if self.validFlag:
                try:
                    # Connect to the DB
                    self.connect = sql.connect("HospitalUsersCreateDB.db")
                    # Get cursor to execute
                    self.cur = self.connect.cursor()

                    rows = self.cur.execute(
                        """
                        UPDATE PatientTestResult
                        SET TestResult = ?
                        WHERE TestResultId = ?;
                        """,
                        (self.result, self.testid),
                    )

                except:
                    print("Error Updtating data")

                finally:
                    self.connect.close()


# Server run
if __name__ == "__main__":
    try:
        HOST, PORT = "localhost", 8888

        ## Instantiate the server
        svr = socketserver.TCPServer((HOST, PORT), myHandler)

        ## Keep the server running continously
        svr.serve_forever()

    except svr.error as e:
        print("Error: ", e)
        exit(1)

    finally:
        svr.close()
