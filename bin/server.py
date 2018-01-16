# Simple and completely insecure grade-accessing server.
# Author: Matt Anderson
# Version: Winter 2018

import sys
import os
from socket import *
import subprocess
import hashlib, hmac
import ssl
import getpass
import binascii

changed = False
# Check arguments
args = sys.argv
if len(args) != 3:
    print("Usage: python3 server.py <username> <port-number>")
    exit()


# Read usernames and passwords from file.
passwords = {}
try:
    pw_file_r = open('../../users.txt','r')
except:
    print("Error: Unable to locate users.txt")
    exit()

lines = pw_file_r.readlines()
#<firstname> <username> <password> <port> <salt>
for line in lines:
    toks = line.strip().split()
    passwords[toks[1]] = (toks[2],toks[4])

pw_file_r.close()


# Configure socket parameters.
try:
    port = int(args[2])
except:
    print("Error: Invalid port number")
    exit()

host = ''
addr = (host, port)
buf_len = 4096


context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.options &= ~ssl.OP_NO_SSLv3
context.options &= ~ssl.OP_NO_SSLv2
context.options &= ~ssl.OP_NO_TLSv1
context.options &= ~ssl.OP_NO_TLSv1_1
context.load_cert_chain(certfile="../../certificate.pem", keyfile="../../key.pem")

# Create TCP socket to listen on.
try:
    sock = socket(AF_INET,SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(addr)
    sock.listen(1)
    print("Started server, pid: %d, user: %s, port: %d" % (os.getpid(),args[1],port))
except:
    print("Error: Unable to start sever on port", port)
    exit()
#Loop waiting for connections
while True:

    # Wait for a new connection
    connection, client_address = sock.accept()

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
        if not clean_uname in passwords.keys():
            f_out.write("Error: Invalid username\n")
            f_out.flush()

        else:
            hahsed_enter_password = hashlib.pbkdf2_hmac('sha256',pw.encode(),binascii.unhexlify(passwords[clean_uname][1].encode()),100000)
            if not hmac.compare_digest(hahsed_enter_password, binascii.unhexlify(passwords[clean_uname][0].encode())):
                f_out.write("Error: Invalid username and password combination\n")
                f_out.flush()
            else:
                while pw == clean_uname:
                    f_out.write("Please change your password.")
                    f_out.write("\n")
                    f_out.write("You will not be able to advance without doing so")
                    f_out.write("\n")
                    f_out.write("Enter your new password here: ")
                    f_out.flush()
                    pw = f_in.readline().strip()

                salt = os.urandom(16)
                pw = hashlib.pbkdf2_hmac('sha256',pw.encode(),salt,100000)
                passwords[clean_uname] = (binascii.hexlify(pw).decode(),binascii.hexlify(salt).decode())

                f_out.write("\nAccess granted. Here are your grades.\n")
                try:
                    with open("grades_%s" %uname) as f:
                        f_out.write(f.read())
                except:
                    f_out.write("I am sorry. You do not have access to view grades on this port.")

                # # Cat the student grade file in the directory back to client.
                # # WARNING: This is a terrible way to pass on the contents of a single file.
                # #          Never write code like this!!!
                # proc = subprocess.Popen(["cat grades_%s" % uname], stdout=f_out,stdin=f_in, \
                #                         stderr=subprocess.STDOUT,shell=True)
                #
                # # Wait for the process to complete.
                # proc.wait()

    # Terminate connection and clean up
    finally:
        connstream.close()
        f_in.close()
        f_out.close()
        print("Closed connection from", client_address)

        try:
            pw_file_r = open('../../users.txt','r')
            pw_file_w = open('../../users_temp','w')
        except:
            print("Error: Unable to locate users.txt")
            exit()

        lines = pw_file_r.readlines()
        #<firstname> <username> <password> <port> <salt>
        for line in lines:
            toks = line.strip().split()
            newstr = toks[0] + " " + toks[1] + " " + passwords[toks[1]][0] + " " + toks[3] + " " + passwords[toks[1]][1] + "\n"
            pw_file_w.write(newstr)

        pw_file_w.close()
        pw_file_r.close()
        os.rename('../../users.txt'.replace('.txt', '_temp'),'../../users.txt')
