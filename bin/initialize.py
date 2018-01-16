import sys
import os
from socket import *
import subprocess
import hashlib, binascii
import ssl

# Check arguments
args = sys.argv
if len(args) != 1:
    print("Usage: python3 server.py <username> <port-number>")
    exit()

try:
    pw_file_r = open('../users.txt','r')
    pw_file_w = open('../users_temp','w')
except:
    print("Error: Unable to locate users.txt")
    exit()

lines = pw_file_r.readlines()
#<firstname> <username> <password> <port>
for line in lines:
    toks = line.strip().split()
    salt = os.urandom(16)
    toks[2] = binascii.hexlify(hashlib.pbkdf2_hmac('sha256',toks[1].encode(),salt,100000)).decode()
    salt = binascii.hexlify(salt).decode()
    newstr = toks[0] + " " + toks[1] + " " + toks[2] + " " + toks[3] + " " + salt + "\n"
    pw_file_w.write(newstr)

pw_file_w.close()
pw_file_r.close()
os.rename('../users.txt'.replace('.txt', '_temp'),'../users.txt')
