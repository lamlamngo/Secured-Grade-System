# Simple and completely insecure grade-accessing server.
# Author: Matt Anderson
# Version: Winter 2018

import sys
import os
from socket import *
import subprocess
import hashlib, binascii
import ssl

# Check arguments
args = sys.argv
if len(args) != 3:
    print("Usage: python3 server.py <username> <port-number>")
    exit()


# Read usernames and passwords from file.
passwords = {}
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
    toks[2] = hashlib.pbkdf2_hmac('sha256',toks[1].encode(),salt,100000)
    newstr = toks[0] + " " + toks[1] + " " + toks[2].hex() + " " + toks[3] + "\n"
    pw_file_w.write(newstr)

pw_file_w.close()
pw_file_r.close()
os.rename('../users.txt'.replace('.txt', '_temp'),'../users.txt')

# Configure socket parameters.
try:
    port = int(args[2])
except:
    print("Error: Invalid port number")
    exit()

host = ''
addr = (host, port)
buf_len = 4096

# # Create TCP socket to listen on.
# try:
#     sock = socket(AF_INET,SOCK_STREAM)
#     sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
#     sock.bind(addr)
#     sock.listen(1)
#     print("Started server, pid: %d, user: %s, port: %d" % (os.getpid(),args[1],port))
# except:
#     print("Error: Unable to start sever on port", port)
#     exit()

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="certificate.pem", keyfile="key.pem")

bindsocket = socket()
bindsocket.bind(addr)
bindsocket.listen(5)
# Loop waiting for connections
while True:

    # Wait for a new connection
    connection, client_address = bindsocket.accept()

    connstream = context.wrap_socket(connection, server_side=True)
    #print('Accepted connection from', client_address)

    f_in = connstream.makefile('r')
    f_out = connstream.makefile('w')

    # Request username.
    f_out.write("Please enter username: ")
    f_out.flush()
    uname = f_in.readline().strip()

    # Clean up username
    if len(uname) < 8:
        clean_uname = ""
    else:
        clean_uname = uname[0:8]

    # Request password.
    f_out.write("Please enter password: ")
    f_out.flush()
    pw = f_in.readline().strip()

    try:

        # Check for valid user/password pair.
        if not clean_uname in passwords.keys() or passwords[clean_uname] != pw:
            f_out.write("Error: Invalid username or password combination.\n")
            f_out.flush()

        else:
            # Cat the student grade file in the directory back to client.
            # WARNING: This is a terrible way to pass on the contents of a single file.
            #          Never write code like this!!!
            proc = subprocess.Popen(["cat grades_%s" % uname], stdout=f_out,stdin=f_in, \
                                    stderr=subprocess.STDOUT,shell=True)

            # Wait for the process to complete.
            proc.wait()

    # Terminate connection and clean up
    finally:
        connection.close()
        f_in.close()
        f_out.close()
        #print("Closed connection from", client_address)
