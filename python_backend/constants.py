"""
This module defines constants and ensures the necessary directories exist.

Constants:
    STORAGE_PATH (str): Base storage path inside the container.
    BUILD_PATH (str): Path for storing compiled ABI/BIN files.
    UPLOADS_PATH (str): Path for storing uploaded Solidity files.
"""

import os

# Base storage path inside the container
STORAGE_PATH = "/app"

# Paths for persisted files
BUILD_PATH = os.path.join(STORAGE_PATH, "build")       # Stores compiled ABI/BIN files
UPLOADS_PATH = os.path.join(STORAGE_PATH, "uploads")   # Stores uploaded Solidity files

# Ensure the directories exist when the app starts
os.makedirs(BUILD_PATH, exist_ok=True)
os.makedirs(UPLOADS_PATH, exist_ok=True)
