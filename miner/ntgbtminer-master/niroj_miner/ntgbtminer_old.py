# ntgbtminer - vsergeev at gmail
# No Thrils GetBlockTemplate Bitcoin Miner
import urllib2
import base64
import json
import hashlib
import struct
import time
import midstate
import util
import sha256_download

################################################################################
# Transaction Coinbase and Hashing Functions
################################################################################

# Create a coinbase transaction
#
# Arguments:
#       coinbase_script:    (hex string) arbitrary script
#       address:            (base58 string) bitcoin address
#       value:              (unsigned int) value
#
# Returns transaction data in ASCII Hex

def tx_make_coinbase(coinbase_script, address, value):
    # See https://en.bitcoin.it/wiki/Transaction

    # Create a pubkey script
    # OP_DUP OP_HASH160 <len to push> <pubkey> OP_EQUALVERIFY OP_CHECKSIG
    pubkey_script = "76" + "a9" + "14" + util.bitcoinaddress2hash160(address) + "88" + "ac"

    tx = ""
    # version
    tx += "01000000"
    # in-counter
    tx += "01"
    # input[0] prev hash
    tx += "0"*64
    # input[0] prev seqnum
    tx += "ffffffff"
    # input[0] script len
    tx += util.int2varinthex(len(coinbase_script)/2)
    # input[0] script
    tx += coinbase_script
    # input[0] seqnum
    tx += "ffffffff"
    # out-counter
    tx += "01"
    # output[0] value (little endian)
    tx += util.int2lehex(value, 8)
    # output[0] script len
    tx += util.int2varinthex(len(pubkey_script)/2)
    # output[0] script
    tx += pubkey_script
    # lock-time
    tx += "00000000"

    return tx

# Compute the SHA256 Double Hash of a transaction
#
# Arguments:
#       tx:    (hex string) ASCII Hex transaction data
#
# Returns a SHA256 double hash in big endian ASCII Hex
def tx_compute_hash(tx):
    h1 = hashlib.sha256(util.hex2bin(tx)).digest()
    h2 = hashlib.sha256(h1).digest()
    return util.bin2hex(h2[::-1])

# Compute the Merkle Root of a list of transaction hashes
#
# Arguments:
#       tx_hashes:    (list) ASCII Hex transaction hashes
#
# Returns a SHA256 double hash in big endian ASCII Hex
def tx_compute_merkle_root(tx_hashes):
    # Convert each hash into a binary string
    for i in range(len(tx_hashes)):
        # Reverse the hash from big endian to little endian
        tx_hashes[i] = util.hex2bin(tx_hashes[i])[::-1]

    # Iteratively compute the merkle root hash
    while len(tx_hashes) > 1:
        # Duplicate last hash if the list is odd
        if len(tx_hashes) % 2 != 0:
            tx_hashes.append(tx_hashes[-1][:])

        tx_hashes_new = []
        for i in range(len(tx_hashes)/2):
            # Concatenate the next two
            concat = tx_hashes.pop(0) + tx_hashes.pop(0)
            # Hash them
            concat_hash = hashlib.sha256(hashlib.sha256(concat).digest()).digest()
            # Add them to our working list
            tx_hashes_new.append(concat_hash)
        tx_hashes = tx_hashes_new

    # Format the root in big endian ascii hex
    return util.bin2hex(tx_hashes[0][::-1])

################################################################################
# Block Preparation Functions
################################################################################

# Form the block header
#
# Arguments:
#       block:      (dict) block data in dictionary
#
# Returns a binary string
def block_form_header(block):
    header = ""

    # Version
    header += struct.pack("<L", block['version'])
    # Previous Block Hash
    header += util.hex2bin(block['previousblockhash'])[::-1]
    # Merkle Root Hash
    header += util.hex2bin(block['merkleroot'])[::-1]
    # Time
    header += struct.pack("<L", block['curtime'])
    # Target Bits
    header += util.hex2bin(block['bits'])[::-1]
    # Nonce
    header += struct.pack("<L", block['nonce'])
    return header

# Compute the Raw SHA256 Double Hash of a block header
#
# Arguments:
#       header:    (string) binary block header
#
# Returns a SHA256 double hash in big endian binary
def block_compute_raw_hash(header):
    return hashlib.sha256(hashlib.sha256(header).digest()).digest()[::-1]

# Convert block bits to target
#
# Arguments:
#       bits:       (string) compressed target in ASCII Hex
#
# Returns a target in big endian binary
def block_bits2target(bits):
    # Bits: 1b0404cb
    # 1b -> left shift of (0x1b - 3) bytes
    # 0404cb -> value
    shift = ord(util.hex2bin(bits[0:2])[0]) - 3
    value = util.hex2bin(bits[2:])

    # Shift value to the left by shift (big endian)
    target = value + "\x00"*shift
    # Add leading zeros (big endian)
    target = "\x00"*(32-len(target)) + target

    return target

# Check if a block header hash meets the target hash
#
# Arguments:
#       block_hash: (string) block hash in big endian binary
#       target:     (string) target in big endian binary
#
# Returns true if header_hash meets target, false if it does not.
#Both block_hash and target_hash are in big endian format
def block_check_target(block_hash, target_hash):
    # Header hash must be strictly less than or equal to target hash
    for i in range(len(block_hash)):
        if ord(block_hash[i]) == ord(target_hash[i]):
            continue
        elif ord(block_hash[i]) < ord(target_hash[i]):
            return True
        else:
            return False

# Format a solved block into the ASCII Hex submit format
#
# Arguments:
#       block:      (dict) block
#
# Returns block in ASCII Hex submit format
def block_make_submit(block):
    subm = ""

    # Block header
    subm += util.bin2hex(block_form_header(block))
    # Number of transactions as a varint
    subm += util.int2varinthex(len(block['transactions']))
    # Concatenated transactions data
    for tx in block['transactions']:
        subm += tx['data']

    return subm

################################################################################
# Mining Loop
################################################################################

# Mine a block
#
# Arguments:
#       block_template:     (dict) block template
#       coinbase_message:   (string) binary string for coinbase script
#       extranonce_start:   (int) extranonce for coinbase script
#       address:            (string) base58 reward bitcoin address
#
# Optional Arguments:
#       timeout:            (False / int) timeout in seconds to give up mining
#       debugnonce_start:   (False / int) nonce start for testing purposes
#
# Returns tuple of (solved block, hashes per second) on finding a solution,
# or (None, hashes per second) on timeout or nonce exhaustion.
def block_mine(block_template, coinbase_message, extranonce_start, address, timeout=False, debugnonce_start=False, debug=False):
    # Add an empty coinbase transaction to the block template
    if debug:
        print "Algo 1 start:"
    coinbase_tx = {}
    block_template['transactions'].insert(0, coinbase_tx)
    # Add a nonce initialized to zero to the block template
    block_template['nonce'] = 0

    # Compute the target hash
    target_hash = block_bits2target(block_template['bits'])

    # Mark our mine start time
    time_start = time.clock()

    # Initialize our running average of hashes per second
    hps_list = []

    # Loop through the extranonce
    extranonce = extranonce_start    

    # Update the coinbase transaction with the extra nonce
    coinbase_script = coinbase_message + util.int2lehex(extranonce, 4)
    coinbase_tx['data'] = tx_make_coinbase(coinbase_script, address, block_template['coinbasevalue'])
    coinbase_tx['hash'] = tx_compute_hash(coinbase_tx['data'])

        # Recompute the merkle root
    tx_hashes = [tx['hash'] for tx in block_template['transactions']]
    block_template['merkleroot'] = tx_compute_merkle_root(tx_hashes)

        # Reform the block header
    block_header = block_form_header(block_template)

    time_stamp = time.clock()

        # Loop through the nonce
    nonce = 0 if debugnonce_start == False else debugnonce_start

        # Update the coinbase transaction with the extra nonce
    coinbase_script = coinbase_message + util.int2lehex(extranonce, 4)
    coinbase_tx['data'] = tx_make_coinbase(coinbase_script, address, block_template['coinbasevalue'])
    coinbase_tx['hash'] = tx_compute_hash(coinbase_tx['data'])

        # Recompute the merkle root
    tx_hashes = [tx['hash'] for tx in block_template['transactions']]
    block_template['merkleroot'] = tx_compute_merkle_root(tx_hashes)

        # Reform the block header
    block_header = block_form_header(block_template)

    time_stamp = time.clock()
            # Update the block header with the new 32-bit nonce
    block_header = block_header[0:76] + chr(nonce & 0xff) + chr((nonce >> 8) & 0xff) + chr((nonce >> 16) & 0xff) + chr((nonce >> 24) & 0xff)
            # Recompute the block hash
    block_hash = block_compute_raw_hash(block_header)
    
    while extranonce <= 0xffffffff:

        # Update the coinbase transaction with the extra nonce
        coinbase_script = coinbase_message + util.int2lehex(extranonce, 4)
        coinbase_tx['data'] = tx_make_coinbase(coinbase_script, address, block_template['coinbasevalue'])
        coinbase_tx['hash'] = tx_compute_hash(coinbase_tx['data'])

        # Recompute the merkle root
        tx_hashes = [tx['hash'] for tx in block_template['transactions']]
        block_template['merkleroot'] = tx_compute_merkle_root(tx_hashes)

        # Reform the block header
        block_header = block_form_header(block_template)

        time_stamp = time.clock()

        # Loop through the nonce
        nonce = 0 if debugnonce_start == False else debugnonce_start
        while nonce <= 0xffffffff:
            # Update the block header with the new 32-bit nonce
            block_header = block_header[0:76] + chr(nonce & 0xff) + chr((nonce >> 8) & 0xff) + chr((nonce >> 16) & 0xff) + chr((nonce >> 24) & 0xff)
            # Recompute the block hash
            block_hash = block_compute_raw_hash(block_header)

            if debug == True:
                print "block_mine-> block_header:", util.bin2hex(block_header)
                print "block_mine-> header_hash:[2]", util.bin2hex(block_hash)

            # Check if it the block meets the target target hash
            if block_check_target(block_hash, target_hash):
                block_template['nonce'] = nonce
                block_template['hash'] = util.bin2hex(block_hash)
                hps_average = 0 if len(hps_list) == 0 else sum(hps_list)/len(hps_list)
                return (block_template, hps_average)

            # Lightweight benchmarking of hashes / sec and timeout check
            if nonce > 0 and nonce % 1000000 == 0:
                time_elapsed = time.clock() - time_stamp
                hps_list.append(1000000.0 / time_elapsed)
                time_stamp = time.clock()

                # If our mine time expired, return none
                if timeout != False and (time_stamp - time_start) > timeout:
                    hps_average = 0 if len(hps_list) == 0 else sum(hps_list)/len(hps_list)
                    return (None, hps_average)
            if debug == True:
                break
            nonce += 1
        extranonce += 1
        if debug == True:
            break

    # If we ran out of extra nonces, return none
    hps_average = 0 if len(hps_list) == 0 else sum(hps_list)/len(hps_list)
    return (None, hps_average)

###############################################################################
# Changes made by me 
###############################################################################
def fpga_miner(block_template, coinbase_message, extranonce_start, address, timeout=False, debugnonce_start=False, debug=False):
    # Add an empty coinbase transaction to the block template
    if debug:
        print ""
        print "Algo 2 start:"
        print ""
    coinbase_tx = {}
    block_template['transactions'].insert(0, coinbase_tx)
    # Add a nonce initialized to zero to the block template
    block_template['nonce'] = 0

    # Compute the target hash
    target_hash = block_bits2target(block_template['bits'])
    if debug == True:
        print block_template['bits']
        print "target_hash", util.bin2hex(target_hash)

    # Mark our mine start time
    time_start = time.clock()

    # Initialize our running average of hashes per second
    hps_list = []

    # Loop through the extranonce
    extranonce = extranonce_start
    coinbase_script = coinbase_message + util.int2lehex(extranonce, 4)
    coinbase_tx['data'] = tx_make_coinbase(coinbase_script, address, block_template['coinbasevalue'])
    coinbase_tx['hash'] = tx_compute_hash(coinbase_tx['data'])
    
    # Recompute the merkle root
    tx_hashes = [tx['hash'] for tx in block_template['transactions']]
    block_template['merkleroot'] = tx_compute_merkle_root(tx_hashes)

    # Reform the block header
    block_header = block_form_header(block_template)
    #TODO: CHECK IF WE NEED TO CHANGE THE ENDIANESS FOR CALCULATING THE MIDSTATE#
    #Block header should be in big endian#
    my_data = midstate.calculateMidstate(block_header[0:64])
    midstatesw = util.bin2hex(my_data)
    targetsw = util.bin2hex(target_hash)
    secondhalf = util.bin2hex(block_header[64:76])
    if debug == True:
        new_data = util.hex2bin('00000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000280')
        second_head = block_header[64:76] + new_data
        data_temp = midstate.calculateMidstate( second_head, my_data, 64 )
        print "fpga_mine-> block_header:", util.bin2hex(block_header)
        print "midstate_calc:[1]", util.bin2hex(data_temp)
        print "fpga_mine->header_hash first round[1]", hashlib.sha256(block_header).hexdigest()
        print "fpga_mine-> header_hash:[2]", hashlib.sha256(data_temp).hexdigest()
        print "fpga_mine->header_hash two round[2]", hashlib.sha256(hashlib.sha256(block_header).digest()).hexdigest()
        return None, 0

    ###COMMENTED FOR TESTING REST OF THE CODE###
    import serial
    print('Starting serial')

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
    #Data used here are all hex.So, find different ways to change data into hex and then we can work accordingly.
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
    print(ser.readline())
    print(ser.readline())
    print(ser.readline())
    done = 0
    while(done == 0):
        line = ser.readline()
        if  line != b'':
            print(line)
    print('End')



################################################################################
# Standalone Bitcoin Miner, Single-threaded
################################################################################

###Test starts
def standalone_miner(coinbase_message, address):
    print "Mining new block template..."
    block_template1 = util.rpc_getblocktemplate()
    mined_block, hps = block_mine(block_template1, coinbase_message, 0, address, timeout=60, debug=True)
    x, y = fpga_miner(block_template1, coinbase_message, 0, address, timeout=60, debug=True)

###Test Ends
            
'''           
def standalone_miner(coinbase_message, address):
    while True:
        print "Mining new block template..."
        mined_block, hps = block_mine(util.rpc_getblocktemplate(), coinbase_message, 0, address, timeout=60)
        print "Average Mhash/s: %.4f\n" % (hps / 1000000.0)

        if mined_block != None:
            print "Solved a block! Block hash:", mined_block['hash']
            submission = block_make_submit(mined_block)
            print "Submitting:", submission, "\n"
            util.rpc_submitblock(submission)


def standalone_miner(coinbase_message, address):
    while True:
        print "Mining new block template..."
        mined_block, hps = fpga_miner(util.rpc_getblocktemplate(), coinbase_message, 0, address, timeout=60)
        print "Average Mhash/s: %.4f\n" % (hps / 1000000.0)

        if mined_block != None:
            print "Solved a block! Block hash:", mined_block['hash']
            submission = block_make_submit(mined_block)
            print "Submitting:", submission, "\n"
            util.rpc_submitblock(submission)
'''

if __name__ == "__main__":
    standalone_miner(util.bin2hex("Hello from Niroj!"), "15PKyTs3jJ3Nyf3i6R7D9tfGCY1ZbtqWdv")
'''
    str = '020000001fba9705b223d40c25b0aba35fee549aa477307862fb45ad180200000000000033d14883e297679e3f9a5eb108dab72ff0998e7622e427273e90027e'
    my_data = util.hex2bin(str)
    ret_val = midstate.calculateMidstate(my_data)
    print_val = util.bin2hex(ret_val)
    print print_val
'''
