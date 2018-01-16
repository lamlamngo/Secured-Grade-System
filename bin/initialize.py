# Initialize the users.txt file to salt hashed default password.
# Adapted from the server.py file by CSC-483 Professor Matt Anderson.
# Written by Lam Ngo

import sys
import os
import hashlib, binascii

# Check arguments
args = sys.argv
if len(args) != 1:
    print("Usage: python3 initialize.py")
    exit()

try:
    pw_file_r = open('../users.txt','r')
    #write to a temp file in order to read and write at the same time.
    pw_file_w = open('../users_temp','w')
except:
    print("Error: Unable to locate users.txt")
    exit()

lines = pw_file_r.readlines()
#<firstname> <username> <password> <port>
for line in lines:
    toks = line.strip().split()
    salt = os.urandom(32)
    toks[2] = binascii.hexlify(hashlib.pbkdf2_hmac('sha256',toks[1].encode(),salt,200000)).decode()
    salt = binascii.hexlify(salt).decode()

    #save the hex version of the bytes password and salt values.
    newstr = toks[0] + " " + toks[1] + " " + toks[2] + " " + toks[3] + " " + salt + "\n"
    pw_file_w.write(newstr)

pw_file_w.close()
pw_file_r.close()

#replace the original file with the updated file. Keep only one copy.
os.rename('../users.txt'.replace('.txt', '_temp'),'../users.txt')
