Due to the complexity of the program installation and programs to run, the project was developed in the several steps. 
	Step 1: Hardcoded default data value used.
	Step 2: Reduced target value.
	Step 3: Connect to the network.
	Step 4: Verify and measure the performance.
	Step 5: Run fully functioning node by connecting the miner software to the network.

Dependencies:
	Project was tested and run with the following configuration.
	OS - UBUNTU-14.04
	PYTHON VERSION 2.7
	pip installer was used to install different python libraries. ($sudo apt-get install pip)
	PYTHON LIBRARIES:
		- urllib2
		- base64
		- json
		- hashlib
		- time
		- random
		- serial
	#### SOME OF THE LIBRARIES MAY NOT BE INSTALLED IN THE PYTHON DEVELOPMENT ENVIORNMENT. IF SO IT CAN BE INSTALLED USING PIP eg ($pip install serial)  this can be used to install serial libraries used in the project.


	The project can be tested with and without connecting to the main bitcoin network.

	1. Without connecting to the bitcoin network.

	In this version, header data and target are hard coded. The hard coded value are used to find the block so that it need not connect to the network for verifying the project.
	The following changes has to be made in the config files:
					(config.py)
		PORT_ADDRESS = '/dev/ttyACM0'
		SUBMIT_DATA = False
		DEBUG_LOCAL_DATA = True
		TARGET_REDUCE = "00000fff"
		PUBLIC_KEY = "mxWqotbFkgBNAziCFHTUpkws8YHootQHD8" #PUBLICKEY FOR account nirojpokhrel
		COINBASE_MSG = "Any message you want to put in coinbase transactions!!!"
		REDUCE_NONCE = True

		The main thing here is PORT_ADDRESS. This should be the address of the port your FPGA board is connected to. The submit data should be false since we will not be submitting the found block which is dummy in our case. The main thing is DEBUG_LOCAL_DATA which needs to be true to activate this step. The rest of the configuration can be left as it is.

	After all the set ups are done.Then it can be run simply by issuing python command.
		$python miner.py

	This will execute the code and call fpga_miner_with_debug_data(). The output can be studied using the print logs which has all the information and difference of hashing time between fpga and PC miner.
	##DUE TO SOME TIME TAKEN TO SETUP SERIAL COMMUNICATION. IT TAKES SOME TIME TO MINE THE FIRST BLOCK but after that it works fine.

	2. With connection to bitcoin network

		$sudo apt-add-repository ppa:bitcoin/bitcoin
		$sudo apt-get update
		$sudo apt-get install bitcoind
		$mkdir ~/.bitcoin
		$touch ~/.bitcoin/bitcoin.conf
		$chmod 600 ~/.bitcoin/bitcoin.conf
		$echo rpcuser=user_user_name >> ~/.bitcoin/bitcoin.conf
		$echo rpcpassword=your_password >> ~/.bitcoin/bitcoin.conf
		$bicoind -testnet -daemon

		NOTES: 
		1. IF THERE IS DIFFICULTY IN SETTING UP THE NETWORK. FOLLOWING WEBSITES PROVIDE DETAIL INFORMATION
			https://bitcoin.org/en/full-node#ubuntu-1410.
		2. rpcuser and rpcpassword set here should be same as the one that will be used in config.py.
		3. bitcoin network - The network can be selected to be test (for development purpose ) or main network. By default if no options are given ($bicoind -daemon) then it is main net, otherwise, if it is explicitly mentioned then it is test network($bitcoind -testnet -daemon). However, to start using main net bitcoind has to download 65-70 GB of blockchain data and may take several hours with high internet connectivity for the bitcoind to be ready. However, the blockchain data needed to download for testnet is smaller( around 10-15 GB). So, testnet our choice of the network.

	Once the bitcoind is up and running in our machine. Then following changes can be made in the config.py. 
				cofig.py
		RPC_URL     = "http://127.0.0.1:18332"
		RPC_USER    = "nirojpokhrel"
		RPC_PASS    = "niroj123"
		PORT_ADDRESS = '/dev/ttyACM0' #Needs changing ?????
		SUBMIT_DATA = False
		DEBUG_LOCAL_DATA = False
		TARGET_REDUCE = "00000fff"
		PUBLIC_KEY = "mxWqotbFkgBNAziCFHTUpkws8YHootQHD8" #PUBLICKEY FOR account nirojpokhrel
		COINBASE_MSG = "Any message you want to put in coinbase transactions!!!"
		REDUCE_NONCE = True

	RPC_URL is the url of your bitcoind. If you are running in the same system as miner then it is as mentioned above. The port number should be 18832 for testnet and 8332 for the main network. The RPC_USER and RPC_PASS is the same one created above whicle creating bitcoin.conf. DEBUG_LOCAL_DATA is now false since we are getting the data with RPC call. However, for the purpose of debugging all the information is left as it is.

	3. Make the miner ready for submission
	For the purpose of submission, following changes has to be made in the config.py.
				config.py
		RPC_URL     = "http://127.0.0.1:18332"
		RPC_USER    = "nirojpokhrel"
		RPC_PASS    = "niroj123"
		PORT_ADDRESS = '/dev/ttyACM0' #Needs changing ?????
		SUBMIT_DATA = True
		DEBUG_LOCAL_DATA = False
		TARGET_REDUCE = "00000fff"
		PUBLIC_KEY = "mxWqotbFkgBNAziCFHTUpkws8YHootQHD8" #PUBLICKEY FOR account nirojpokhrel
		COINBASE_MSG = "Any message you want to put in coinbase transactions!!!"
		REDUCE_NONCE = False

	SUBMIT_DATA should be true, DEBUG_LOCAL_DATA should be false and REDUCE_NONCE should also be false. 

	DISCLAIMER: We think the miner should be fine and the block submitted will be accepted. However, we were not able to find the block and test it due to limitation of our testing time with the devices.


If there is any trouble to run the program let us know via email,
	nirojpokhrel@gmail.com
	danukg.sjce@gmail.com 
	rockychmp777@gmail.com 
