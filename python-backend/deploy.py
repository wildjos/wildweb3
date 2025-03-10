# for deploy:
import os
import json
import time 

from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from eth_account.signers.local import LocalAccount
from dotenv import load_dotenv


load_dotenv()

def deploy(base_filename: str, constructor_args: list):


    # Connect to the Infura Sepolia node
    ethNodeUrl = 'https://sepolia.infura.io/v3/'
    apiKey =  os.getenv("INFURA_API_KEY")
    if not apiKey:
        raise ValueError("INFURA_API_KEY environment variable is not set")

    w3 = Web3(Web3.HTTPProvider(ethNodeUrl + apiKey))
    print(f"EthNodeUrl: {ethNodeUrl} is connected: {w3.is_connected()}")

    # Ensure connection is successful
    if not w3.is_connected():
        raise Exception("Failed to connect to the Ethereum node")

    # Set the default account 
    pkey = os.getenv("PRIVATE_KEY")
    if not pkey:
        raise ValueError("PRIVATE_KEY environment variable is not set")
    
    contract_account: LocalAccount = Account.from_key(pkey)

    # Load the ABI and binary
    abi_path = f'build/{base_filename}ABI.json'
    bin_path = f'build/{base_filename}BIN.json'
    
    with open(abi_path, 'r') as abi_file:
        contract_abi = json.load(abi_file)
    with open(bin_path, 'r') as bin_file:
        contract_bin = bin_file.read()

    # Create the contract instance
    contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bin)
    print(f"contract_account.address: {contract_account.address}")
    print(f"nonce: {w3.eth.get_transaction_count(contract_account.address)}")

    gas_price = w3.eth.gas_price
    # higher_gas_price = int(gas_price * 1.5)  # 2x for priority
    print(f"Current gas price: {w3.from_wei(gas_price, 'gwei')} gwei")
    # print(f"Increased gas price: {w3.from_wei(higher_gas_price, 'gwei')} gwei")

    balance = w3.eth.get_balance(contract_account.address)
    print(f"ETH Balance: {w3.from_wei(balance, 'ether')} ETH")

    # Build the transaction
    transaction = contract.constructor(*constructor_args).build_transaction({
        'from': contract_account.address,
        'nonce': w3.eth.get_transaction_count(contract_account.address),
        'gas': 1_500_000,
        'gasPrice': int(gas_price)

    })

    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=pkey)

    # Send the transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"tx_hash: {tx_hash.hex()}")
   
    max_attempts = 50  
    attempt = 0
    
    # Wait for the transaction to be mined
    while attempt < max_attempts:
        try:
            tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
            if tx_receipt:
                print(f"Transaction confirmed: {tx_receipt}")
                break
        except TransactionNotFound:
            print(f"Attempt {attempt+1}: Waiting for transaction confirmation...")

        time.sleep(5) 
        attempt += 1
    else:
        raise TimeoutError(f"Transaction: {tx_hash.hex()} not confirmed after: {max_attempts} attempts.")

    # Get the contract address
    contract_address = tx_receipt.contractAddress

    print(f"Contract deployed at address: {contract_address}")
    return contract_address

