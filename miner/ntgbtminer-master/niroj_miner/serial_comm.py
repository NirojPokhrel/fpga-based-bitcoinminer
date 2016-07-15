import serial
import midstate
import hashlib
import util
import struct

DEBUG_STRING = "SERIAL_COMM"

class MySerial:

	def __init__(self, serial_port="/dev/ttyACM0" , debug='False'):
		self.serial_port = serial_port
		self.debug = debug
		self.serial = None

	def open(self):
		#Debug
		if self.debug:
			self.serial = "Debug Mode"
			return

		self.serial = serial.Serial(
			port=self.serial_port, baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, 
			bytesize=serial.EIGHTBITS, timeout=10)
		ser = self.serial
		print("Connected to: " + ser.portstr)
		ser.flushInput()
		print("Chars waiting in buffer after flush: " + str(ser.inWaiting()))
		print(ser.readline())

	#Data used here are all hex.So, find different ways to change data into hex and then we can work accordingly.
	def write_data( self, secondhalf, midstatesw, targetsw):
		if self.serial is None:
			self.open()
			if self.serial is None:
				print "Cannot open serial communication with FPGA board"
				return None

		if self.debug:
			self.secondhalf = secondhalf
			self.midstatesw = midstatesw
			self.targetsw = targetsw
			return
		ser = self.serial
		ser.write(secondhalf[0:8].encode())
		ser.write(b'\n')
		ser.write(secondhalf[8:16].encode())
		ser.write(b'\n')
		ser.write(secondhalf[16:24].encode())
		ser.write(b'\n')
		print(ser.readline())
		print(ser.readline())
		print(ser.readline())
		ser.write(midstatesw[0:8].encode())
		ser.write(b'\n')
		ser.write(midstatesw[8:16].encode())
		ser.write(b'\n')
		ser.write(midstatesw[16:24].encode())
		ser.write(b'\n')
		ser.write(midstatesw[24:32].encode())
		ser.write(b'\n')
		ser.write(midstatesw[32:40].encode())
		ser.write(b'\n')
		ser.write(midstatesw[40:48].encode())
		ser.write(b'\n')
		ser.write(midstatesw[48:56].encode())
		ser.write(b'\n')
		ser.write(midstatesw[56:64].encode())
		ser.write(b'\n')
		print(ser.readline())
		print(ser.readline())
		ser.write(targetsw[0:8].encode())
		ser.write(b'\n')
		ser.write(targetsw[8:16].encode())
		ser.write(b'\n')
		ser.write(targetsw[16:24].encode())
		ser.write(b'\n')
		ser.write(targetsw[24:32].encode())
		ser.write(b'\n')
		ser.write(targetsw[32:40].encode())
		ser.write(b'\n')
		ser.write(targetsw[40:48].encode())
		ser.write(b'\n')
		ser.write(targetsw[48:56].encode())
		ser.write(b'\n')
		ser.write(targetsw[56:64].encode())
		ser.write(b'\n')
		line = ser.readline()
		words = line.split()
		if words[0] == 'Target':
			self.target = words[2]
			print self.target
		print line
		print(ser.readline())
		print(ser.readline())
		done = 0
		print "Before sending: secondhalf is ", secondhalf
		print "Before sending: midstatesw is ", midstatesw
		print "Before sending: target is ", targetsw
		while(done == 0):
			line = ser.readline()
			if  line != b'':
				print(line)
				words = line.split()
				if words[0] == 'Nonce:':
					self.nonce = words[1]
					break
		print('End')
		ser.close()
		return None

	def get_target(self):
		return self.target

	def get_nonce(self):
		return self.nonce

	def get_hash_info(self):
		if self.debug:
			new_data = util.hex2bin('00000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000280')
			second_head = block_header[64:76] + new_data
			data_temp = midstate.calculateMidstate( second_head, my_data, 64 )

		'''
		Send a info to FPGA board to stop the current hashing and send the info regarding.
		send fff to indicate that hashin info is requested
		ser = self.serial
		ser.write(secondhalf[0:8].encode())
		ser.write(b'\n')
		ser.write(secondhalf[8:16].encode())
		ser.write(b'\n')
		ser.write(secondhalf[16:24].encode())
		ser.write(b'\n')
		print(ser.readline())
		print(ser.readline())
		print(ser.readline())
		'''
		return None

	#TODO: What if block is found before we requested for the hashing info. We may loose the block because didn't initiate serial communication.
	#If block is found then, it might start writing to our block. Check every second or two
	#nonce is used for debuggin purpose only. Otherwise it has no usage
	def get_current_state(self, nonce=0):
		if self.debug:
			return self.debug_hash(nonce)
		line = self.serial.readline()
		if  line != b'':
			print(line)
			return line

		return None

	def debug_hash(self, nonce):
		n_nonce = struct.pack("<L", nonce)
		new_data = util.hex2bin('800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000280')
		new_data = n_nonce + new_data
		second_head = util.hex2bin(self.secondhalf) + new_data
		data_temp = midstate.calculateMidstate( second_head, util.hex2bin(self.midstatesw), 64 )
		final_hash = hashlib.sha256(data_temp).digest()[::-1]
		print DEBUG_STRING, util.bin2hex(final_hash)
		# Check if it the block meets the target target hash
		if util.block_check_target(final_hash, util.hex2bin(self.targetsw)):
			return (final_hash, nonce)
		return (None, nonce)




