import serial

class my_serial:

	def __init__(self, serial_port="/dev/ttyACM0"):
		self.serial_port = serial_port