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
		print("Serial Connection: " + ser.portstr)
		ser.flushInput()
		print("Data Remaining in Buffer: " + str(ser.inWaiting()))
		print(ser.readline())

	#Data used here are all hex.
	def write_data( self, data_remaining , midstate_hex , target_hex ):
		if self.serial is None:
			self.open()
			if self.serial is None:
				print "Cannot open serial communication with FPGA board"
				return None

		if self.debug:
			self.data_remaining  = data_remaining 
			self.midstate_hex  = midstate_hex 
			self.target_hex  = target_hex 
			return
		ser = self.serial
		ser.write(data_remaining [0:8].encode())
		ser.write(b'\n')
		ser.write(data_remaining [8:16].encode())
		ser.write(b'\n')
		ser.write(data_remaining [16:24].encode())
		ser.write(b'\n')
		print(ser.readline())
		print(ser.readline())
		print(ser.readline())
		ser.write(midstate_hex [0:8].encode())
		ser.write(b'\n')
		ser.write(midstate_hex [8:16].encode())
		ser.write(b'\n')
		ser.write(midstate_hex [16:24].encode())
		ser.write(b'\n')
		ser.write(midstate_hex [24:32].encode())
		ser.write(b'\n')
		ser.write(midstate_hex [32:40].encode())
		ser.write(b'\n')
		ser.write(midstate_hex [40:48].encode())
		ser.write(b'\n')
		ser.write(midstate_hex [48:56].encode())
		ser.write(b'\n')
		ser.write(midstate_hex [56:64].encode())
		ser.write(b'\n')
		print(ser.readline())
		print(ser.readline())
		ser.write(target_hex [0:8].encode())
		ser.write(b'\n')
		ser.write(target_hex [8:16].encode())
		ser.write(b'\n')
		ser.write(target_hex [16:24].encode())
		ser.write(b'\n')
		ser.write(target_hex [24:32].encode())
		ser.write(b'\n')
		ser.write(target_hex [32:40].encode())
		ser.write(b'\n')
		ser.write(target_hex [40:48].encode())
		ser.write(b'\n')
		ser.write(target_hex [48:56].encode())
		ser.write(b'\n')
		ser.write(target_hex [56:64].encode())
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

	'''
	Can be changed to get the data from the serial in between!!!
	'''
	def get_hash_info(self):
		if self.debug:
			new_data = util.hex2bin('00000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000280')
			second_head = block_header[64:76] + new_data
			data_temp = midstate.calculateMidstate( second_head, my_data, 64 )

		return None

	'''
	Debugging serial communication!!!
	'''
	def debug_hash(self, nonce):
		n_nonce = struct.pack("<L", nonce)
		new_data = util.hex2bin('800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000280')
		new_data = n_nonce + new_data
		second_head = util.hex2bin(self.data_remaining ) + new_data
		data_temp = midstate.calculateMidstate( second_head, util.hex2bin(self.midstate_hex ), 64 )
		final_hash = hashlib.sha256(data_temp).digest()[::-1]
		print DEBUG_STRING, util.bin2hex(final_hash)
		# Check if it the block meets the target target hash
		if util.block_check_target(final_hash, util.hex2bin(self.target_hex )):
			return (final_hash, nonce)
		return (None, nonce)




