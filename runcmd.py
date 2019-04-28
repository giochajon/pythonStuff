	#                                     _ 
	# _ __ _   _ _ __   ___ _ __ ___   __| |
	#| '__| | | | '_ \ / __| '_ ` _ \ / _` |
	#| |  | |_| | | | | (__| | | | | | (_| |
	#|_|   \__,_|_| |_|\___|_| |_| |_|\__,_|
	#
	#  sends a command to Simon's computer and returns the result

import subprocess
import sys

HOST="192.168.1.69"
# Ports are handled in ~/.ssh/config since we use OpenSSH

# the following line will send arguments 
COMMAND= ' '.join(sys.argv[1:])

#COMMAND= 'pkill firefox'



ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
result = ssh.stdout.readlines()
if result == []:
    error = ssh.stderr.readlines()
    print (sys.stderr, "ERROR: %s" % error)
else:
    print (result)