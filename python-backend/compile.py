# for compile:
import solcx
import json
import os

def compile(filename: str):
    
    # Set the Solidity compiler version
    solcx.install_solc('0.8.0')
    solcx.set_solc_version('0.8.0')

    # Read the Solidity source code
    with open(filename, 'r') as file:
        lottery_source = file.read()

    # Compile the Solidity source code
    compiled_sol = solcx.compile_source(
        lottery_source,
        output_values=['abi', 'bin']
    )

    # Extract the contract interface
    contract_id, contract_interface = compiled_sol.popitem()

    # Get the base filename without the .sol extension
    base_filename = os.path.splitext(os.path.basename(filename))[0]

    # Save the ABI and binary to JSON files
    os.makedirs('build', exist_ok=True)
    with open(f'build/{base_filename}ABI.json', 'w') as abi_file:
        json.dump(contract_interface['abi'], abi_file)
    with open(f'build/{base_filename}BIN.json', 'w') as bin_file:
        bin_file.write(contract_interface['bin'])

    print(f"Contract {base_filename} compiled successfully!")