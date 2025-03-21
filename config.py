import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration settings
config = {
    # Bot settings
    "prefix": "/",
    "token": os.getenv("DISCORD_BOT_TOKEN"),  # Set this as an environment variable when deploying
    "clientId": os.getenv("DISCORD_CLIENT_ID"),  # Set this as an environment variable when deploying
    
    # Service settings
    "defaultFee": 0.5,  # Default service fee in percentage
    "minimumSwapAmountUSD": 1,  # Minimum swap amount in USD
    
    # Bot state
    "isPaused": False,
    
    # User lists
    "whitelistedUsers": [],
    "blacklistedUsers": [],
    
    # Supported cryptocurrencies and their networks
    "supportedTokens": [
        {"symbol": "BTC", "name": "Bitcoin", "network": "Bitcoin"},
        {"symbol": "ETH", "name": "Ethereum", "network": "Ethereum"},
        {"symbol": "LTC", "name": "Litecoin", "network": "Litecoin"},
        {"symbol": "XRP", "name": "Ripple", "network": "Ripple"},
        {"symbol": "SOL", "name": "Solana", "network": "Solana"},
        {"symbol": "DOGE", "name": "Dogecoin", "network": "Dogecoin"},
        {"symbol": "BCH", "name": "Bitcoin Cash", "network": "Bitcoin Cash"},
        {"symbol": "XMR", "name": "Monero", "network": "Monero"},
        {"symbol": "TRX", "name": "Tron", "network": "Tron"}
    ],
    
    # DEX APIs
    "dexAPIs": [
        {"name": "SideShift", "url": "https://sideshift.ai/api"},
        {"name": "Exolix", "url": "https://exolix.com/api"},
        {"name": "1inch", "url": "https://api.1inch.io"},
        {"name": "Uniswap", "url": "https://api.uniswap.org"},
        {"name": "PancakeSwap", "url": "https://api.pancakeswap.info"}
    ],
    
    # Owner's Discord user ID - make sure this is loaded as a string
    "ownerId": os.getenv("OWNER_ID")
}

# Print owner ID for debugging
print(f"Owner ID loaded: {config['ownerId']}")

# If owner ID is None, print a warning
if config['ownerId'] is None:
    print("WARNING: Owner ID not found in environment variables!")
    print("Make sure your .env file contains: OWNER_ID=1162870651393146891")
    print("Current environment variables:", os.environ.keys())
