"""
Contract Store module.

This module provides functionality to read from and write to the database
for storing contract information, such as who deployed what contract and when.
"""


from typing import List, Dict, Any
import psycopg2
from python_backend.models import Contract
from python_backend.logger_config import LOGGER

# Database connection details
DATABASE_URL = "postgresql://myuser:mypassword@postgres_db/mydatabase"


def get_connection():
    """
    Create and return a new database connection.
    """
    return psycopg2.connect(DATABASE_URL)


def store_contract_info(contract_info: Contract):
    """
    Store contract information in the database.

    Args:
        contract_info (dict): A dictionary containing contract information.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO contracts (contract_name, contract_address,
                                    deployer_name, deployer_address, 
                                    network, 
                                    deployment_tx_hash, 
                                    deployment_timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (contract_info.contract_name, contract_info.contract_address,
              contract_info.deployer_name, contract_info.deployer_address,
              contract_info.network,
              contract_info.deployment_tx_hash, contract_info.deployment_timestamp))

        conn.commit()
        LOGGER.info("Contract information stored successfully.")

        # Commit transaction
        cur.close()
        conn.close()
    except psycopg2.Error as e:
        LOGGER.error("Database error: %s", e, exc_info=True)
        raise RuntimeError("Unexpected database error occurred in store_contract_info.") from e


def get_contracts() -> List[Dict[str, Any]]:
    """
    Retrieve all contract information from the database.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing contract information.
    """
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM contracts;")
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        LOGGER.info(column_names)
        contracts = [dict(zip(column_names, row)) for row in rows]

        return contracts
    except psycopg2.Error as e:
        LOGGER.error("Database error: %s", e)
        raise RuntimeError("Unexpected database error occurred in get_contracts.") from e
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def check_tables() -> bool:
    """
    Check if the contracts table exists in the database.

    Returns:
        bool: True if the table exists, False otherwise.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'contracts';
        """)
        result = cur.fetchone()

        cur.close()
        conn.close()

        return bool(result)
    except psycopg2.Error as e:
        LOGGER.error("Database error: %s", e)
        raise RuntimeError("Unexpected database error occurred in check_tables.") from e
