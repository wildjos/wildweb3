import uvicorn
# from typing import 
from wildweb3_api import app
from config import load_config, ConfigType

CONFIG_FILE = "../data/config.toml"

def run_webserver(config):
        
    server_config = uvicorn.Config(
        app=config["app_name"],
        host=config["host"],
        port=config["port"],
        log_level=config["log_level"],
        reload=config["reload"],
        workers=1)
    
    server = uvicorn.Server(server_config)
    server.run()


def main():
    # Load any config needed here (add TOML?)
    config = load_config(CONFIG_FILE)

    # Run the web server
    run_webserver(config['api_server'])


# Entry Point
if __name__ == "__main__":
    print("Welcome to WildWeb3 python backend")
    main()

