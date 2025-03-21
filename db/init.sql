

CREATE TABLE IF NOT EXISTS contracts (
    id SERIAL PRIMARY KEY,
    contract_name TEXT NOT NULL, -- Contract name
    contract_address TEXT UNIQUE NOT NULL, -- Deployed contract address
    deployer_name TEXT NOT NULL, -- User-friendly name (e.g., "Alice")
    deployer_address TEXT NOT NULL, -- EOA (Externally Owned Account) that deployed the contract
    network TEXT NOT NULL, -- Blockchain network (e.g., Ethereum, Polygon, etc.)
    deployment_tx_hash TEXT UNIQUE NOT NULL, -- Transaction hash of deployment
    deployment_timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS function_calls (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER REFERENCES contracts(id),
    method_name TEXT,
    caller_address TEXT,
    tx_hash TEXT UNIQUE NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER REFERENCES contracts(id),
    event_name TEXT,
    data JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

