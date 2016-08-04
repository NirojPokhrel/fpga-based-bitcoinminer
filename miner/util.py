
import random
import json
import urllib2
import base64
import json
import hashlib
import struct
import time
from config import RPC_USER, RPC_URL, RPC_PASS
import serial

# JSON-HTTP RPC Configuration
# This will be particular to your local ~/.bitcoin/bitcoin.conf
################################################################################
# Bitcoin Daemon JSON-HTTP RPC
################################################################################

def rpc(method, params=None):
    rpc_id = random.getrandbits(32)

    callstr = json.dumps({"id": rpc_id, "method": method, "params": params})

    authstr = base64.encodestring('%s:%s' % (RPC_USER, RPC_PASS)).strip()

    request = urllib2.Request(RPC_URL)
    request.add_header("Authorization", "Basic %s" % authstr)
    request.add_data(callstr)
    f = urllib2.urlopen(request)
    response = json.loads(f.read())

    if response['id'] != rpc_id:
        raise ValueError("invalid response id!")
    elif response['error'] != None:
        raise ValueError("rpc error: %s" % json.dumps(response['error']))

    return response['result']

################################################################################
# Bitcoin Daemon RPC Call Wrappers
################################################################################

def rpc_getblocktemplate():
    try: return rpc("getblocktemplate", [{}])
    except ValueError: return {}

def rpc_submitblock(block_submission):
    try: return rpc("submitblock", [block_submission])
    except ValueError: return {}

# For unittest purposes:

def rpc_getblock(block_id):
    try: return rpc("getblock", [block_id])
    except ValueError: return {}

def rpc_getrawtransaction(transaction_id):
    try: return rpc("getrawtransaction", [transaction_id])
    except ValueError: return {}

################################################################################
# Representation Conversion Utility Functions
################################################################################

# Convert an unsigned integer to a little endian ASCII Hex
def int2lehex(x, width):
    if width == 1: return "%02x" % x
    elif width == 2: return "".join(["%02x" % ord(c) for c in struct.pack("<H", x)])
    elif width == 4: return "".join(["%02x" % ord(c) for c in struct.pack("<L", x)])
    elif width == 8: return "".join(["%02x" % ord(c) for c in struct.pack("<Q", x)])

# Convert an unsigned integer to little endian varint ASCII Hex
def int2varinthex(x):
    if x < 0xfd: return "%02x" % x
    elif x <= 0xffff: return "fd" + int2lehex(x, 2)
    elif x <= 0xffffffff: return "fe" + int2lehex(x, 4)
    else: return "ff" + int2lehex(x, 8)

# Convert a binary string to ASCII Hex
def bin2hex(s):
    h = ""
    for c in s:
        h += "%02x" % ord(c)
    return h

# Convert an ASCII Hex string to a binary string
def hex2bin(s):
    b = ""
    for i in range(len(s)/2):
        b += chr(int(s[2*i : 2*i + 2], 16))
    return b

# Convert a Base58 Bitcoin address to its Hash-160 ASCII Hex
def bitcoinaddress2hash160(s):
    table = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    x = 0
    s = s[::-1]
    for i in range(len(s)):
        x += (58**i)*table.find(s[i])

    # Convert number to ASCII Hex string
    x = "%050x" % x
    # Discard 1-byte network byte at beginning and 4-byte checksum at the end
    return x[2:50-8]

ser = None
def initialize_serial():
    print('Starting serial')
    global ser
    ser = serial.Serial(
      port='/dev/ttyACM0',\
      baudrate=115200,\
      parity=serial.PARITY_NONE,\
      stopbits=serial.STOPBITS_ONE,\
      bytesize=serial.EIGHTBITS,\
      timeout=10)
    print("Connected to: " + ser.portstr)
    ser.flushInput()
    print("Chars waiting in buffer after flush: " + str(ser.inWaiting()))
    print(ser.readline())

def get_serial():
    global ser
    if ser is None:
        initialize_serial()
    return ser