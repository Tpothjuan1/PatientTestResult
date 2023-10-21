"""
Name:Juan Sanchez Moreno
Date:10/13/2022
Assignment: Module 7: Send Encrypted Message
Due Date:10/15/2023
About this project: This module creates a cipher object with a fixed key on plaintext.
The cipher object is used to encrypt and decrypt data with the same key and initial vector.
Assumptions:NA
All work below was performed by Juan Sanchez
"""

from Crypto.Cipher import AES
import base64


class AESCryptoSuite:
    # Constructor
    def __init__(self, key, initVector):
        self.key = key
        self.initVector = initVector

    # Encrypt funcionality

    def Encrypt(self, bytesInput):
        # Create Cipher
        self.cypher = AES.new(self.key, AES.MODE_CFB, self.initVector)
        # Encrypt
        cipherText = self.cypher.encrypt(bytesInput)
        # return ciphertext encoded in base64
        return base64.b64encode(cipherText)

    def Decrypt(self, bytesInput):
        # Create Cipher
        self.cypher = AES.new(self.key, AES.MODE_CFB, self.initVector)
        # Convert to bytes
        cipherText = base64.b64decode(bytesInput)
        # Decrypt
        plainText = self.cypher.decrypt(cipherText)
        return plainText.decode("utf-8")


# This is the key, it's not safe to put it inside the source code
# To 16Byte strings
key = "this is not safe".encode("utf-8")
iv = "not safe either!".encode("utf-8")

# Cipher object to be used in the application for encryption ta

theCypher = AESCryptoSuite(key, iv)
