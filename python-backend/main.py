import uvicorn
import argparse
# from wildweb3_api import app
from config import load_config


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


def main(config_file):
    # Load any config needed here
    config = load_config(config_file)

    # Run the web server
    run_webserver(config['api_server'])


# Entry Point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WildWeb3 Python Backend")
    parser.add_argument(
        "--config",
        type=str,
        default="../data/config.toml",
        help="Path to the configuratino file"
    )

    args = parser.parse_args()
    print("Welcome to WildWeb3 python backend")

    main(args.config)

