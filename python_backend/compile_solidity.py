"""
Module for compiling Solidity contracts.
"""
import os
import json
import solcx

from python_backend.constants import BUILD_PATH



def compile_solidity(filename: str):
    """
    Compile a Solidity contract and save the ABI and binary to JSON files.

    Args:
        filename (str): The path to the Solidity source file.
    """
    # Set the Solidity compiler version
    solcx.install_solc('0.8.0')
    solcx.set_solc_version('0.8.0')

    # Read the Solidity source code
    with open(filename, 'r', encoding='utf-8') as file:
        solidity_source = file.read()

    # Compile the Solidity source code
    compiled_sol = solcx.compile_source(
        solidity_source,
        output_values=['abi', 'bin']
    )

    # Extract the contract interface
    _, contract_interface = compiled_sol.popitem()

    # Get the base filename without the .sol extension
    base_filename = os.path.splitext(os.path.basename(filename))[0]

    # Save the ABI and binary to JSON files
    with open(f'{BUILD_PATH}/{base_filename}ABI.json', 'w', encoding='utf-8') as abi_file:
        json.dump(contract_interface['abi'], abi_file)
    with open(f'{BUILD_PATH}/{base_filename}BIN.json', 'w', encoding='utf-8') as bin_file:
        bin_file.write(contract_interface['bin'])

    print(f"Contract {base_filename} compiled successfully!")
