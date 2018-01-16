This directory contains the experimental grade access system for CSC 483.

Directory structure:

README.txt             : This file

users.txt              : Contains first names, usernames, passwords, port numbers for all users

bin/                   : Scripts for starting servers and underlying python code

    start_server.sh    : Starts a server for given student on a port, always running for each student
                         usage  ./start_server.sh <username> <port>

    server.py          : Simple python server run by start_server.sh
    
    start_final_server : Starts final grade server only runs when I need to examine final grades.
    		         usage  ./start_final_server <port>

    final_server.py    : Simple python server run by start_final_server.  A minor modification to server.py
    

final_grades/          : Stores final grade files for all students, only
                         accessible as root for security reasons.


lab_grades/<user>/     : stores lab grades for all students, will contain student work eventually.



TODO:

 - Find and fix security flaws?


NOTE: To initialize users.txt file (set default password to be the same as user name), I write a separate script
named initialize.py. It will change the passwords in the original text file to the hashed version and also include
the salt value for each one.

1. The first error is with using subprocess to pass on the contents of a single file. From reading the python
documentation online, when we will sock.accept(), the server will block calls that hold the processes. Thus,
when we use subprocess to cat a file, we would receive the error SSL3_GET_RECORD: wrong version number.

Note: This is basically my thought process when I tried to decode, thus it can be wrong. 

However, when I changed it to a simple routine: open the file, and then use makefile to write the content to the 
client side, everything works fine.

In addition, since we do not use subprocess anymore, we also remove the risk of shell injection.

2. In addition, I included some additional guides to make the system more accessible to users. For example, I add a comment
to say that an user does not have access to the grades on a certain port, to signify that they are using the wrong ports.
Another example is to tell the users that they are entering invalid user names (not 8 characters, or not in the database).

3. To improve security, when changing passwords, I make it so that the length of the passwords need to be greater than 3, to
lower the chance of being brute forced.

4. Make it so that only TLSv1.2 and later can make connections to the server to increase security. The server does not crash
if an unsupported protocol is used. Tested using: openssl s_client -ssl3 -connect localhost:7353

DESIGN PRINCIPLES REFLECTION

1. Economy of design:
	In this process, I got to use a good and tested security tool to secure my server: store salt hashed passwords instead of 
plain text for user authentication. It is a simple, easy to use and also powerful tool.
	In addition, using ssl and its protocol are a straight forward and powerful way to secure a server. With just one or two line 
of code, my server now requires a system capable of TLSv1_2, which is a great step up from the original design. 

2. Psychological Acceptability: 
	I tried to make the system as usable and fun to use as possible, while making sure that it is still secured. Thus, it will 
not create too much inconvenience that the users would want o subvert security.

3. Layering:
	To an extent, this project also has a few layers of protection. SSL offers the first layer, salt hashed password as the second, and username + port 
verification as the last. While this is not a good use of layering, it offers a good impression of how it works in real-life aopplication.

4. Least privilege:
	Each user only has access to her own grades, and really cannot do anything else. He or she can log in, but will be logged out immediately after the grades are 
presented. In addition, due to having different ports, knowing username and password to another's account does not grant the access to that person's grades.




