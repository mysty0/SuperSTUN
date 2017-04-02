import socket
import threading
import time
import sys
from multiprocessing import Process, Pipe, Queue

def sendError(error, addr, sock):
	print 'ERROR ', error, ' on user ', addr
	sock.sendto(error, addr)

def createSocket(port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	sock.bind((UDP_IP, port))
	return sock

def subSocketKiller(proc, kTime):
	time.sleep(kTime)
	print 'Kill proccess: ', proc
	#sock.close()
	proc.terminate()

def subSocketListener(port, addr, lastSock):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		sock.bind((UDP_IP, port))
		print 'Bind subsocket port: ', port
		print 'Start listening'
		lastSock.sendto('PORTOK', addr)
		#clallback.put(sock)
		while True:
			data, addr = sock.recvfrom(1024)	
			print 'subsubsocket new packet', data, ' from ', addr
			sock.sendto(data+" "+str(addr), addr)
		sock.close()
	except Exception, e:
		print 'exep ', e
		sendError('ERRORPORT', addr, lastSock)
		sock.close()
	

def testPort(port):
	if port.isdigit():
		iport = int(port)
		if iport>50000 and iport<65000:
			return True
	return False

def createSubsocket(port, sock, addr):
	p = Process(target=subSocketListener, args=(port, addr, sock, ))
	p.start()
	#s = q.get()
	kp = Process(target=subSocketKiller, args=(p, 5 ))
	kp.start()

def listenProcess(sock):
	while True:
		data, addr = sock.recvfrom(1024)	
		print 'main socket new packet', data, ' from ', addr
		if testPort(data):
			port = int(data)
    		createSubsocket(int(data), sock, addr)
    	else:
			sendError("ERRORPARSEPORT", addr, sock)

	sock.close()


UDP_IP = ""
UDP_PORT = 7777

mainSock = createSocket(UDP_PORT)
print 'server started on ', UDP_PORT

parent_conn, child_conn = Pipe()
p = Process(target=listenProcess, args=(mainSock,))
p.start()
print parent_conn.recv()   # prints "[42, None, 'hello']"
p.join()

