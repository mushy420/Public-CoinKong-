import discord
import random
import time
import asyncio
from config import config

class Utils:
    """Utility functions for the bot"""
    
    def __init__(self):
        pass
        
    def is_owner(self, user_id):
        """Check if a user is the bot owner"""
        owner_id = config["ownerId"]
        # Convert both user IDs to strings for comparison
        user_id_str = str(user_id)
        owner_id_str = str(owner_id) if owner_id is not None else None
        
        print(f"Comparing user ID: {user_id_str} with owner ID: {owner_id_str}")
        return user_id_str == owner_id_str
    
    def is_blacklisted(self, user_id):
        """Check if a user is blacklisted"""
        user_id_str = str(user_id)
        return user_id_str in [str(id) for id in config["blacklistedUsers"]]
    
    def is_whitelisted(self, user_id):
        """Check if a user is whitelisted"""
        user_id_str = str(user_id)
        return user_id_str in [str(id) for id in config["whitelistedUsers"]]
    
    def is_in_maintenance(self):
        """Check if the bot is in maintenance mode"""
        return config["isPaused"]
    
    def can_use_bot(self, user_id):
        """Check if a user can use the bot (not blacklisted and either not in maintenance or whitelisted)"""
        if self.is_blacklisted(user_id):
            return False
        if self.is_in_maintenance() and not self.is_whitelisted(user_id) and not self.is_owner(user_id):
            return False
        return True
    
    def format_currency(self, amount, currency):
        """Format a currency amount for display"""
        return f"{amount} {currency}"
    
    def generate_swap_id(self):
        """Generate a unique swap ID"""
        return f"KONG-{int(time.time())}-{random.randint(0, 999)}"
    
    def get_timestamp(self):
        """Get current timestamp"""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    def format_swap_record(self, swap):
        """Format a swap record for display"""
        return {
            "id": swap["id"],
            "status": swap["status"],
            "fromAmount": self.format_currency(swap["fromAmount"], swap["fromCurrency"]),
            "toAmount": self.format_currency(swap["toAmount"], swap["toCurrency"]),
            "fee": f"{swap['fee']}%",
            "initiatedAt": swap["timestamp"],
            "userId": swap["userId"],
            "sourceAddress": swap["sourceAddress"],
            "destinationAddress": swap["destinationAddress"],
            "confirmations": swap.get("confirmations", 0),
            "requiredConfirmations": swap.get("requiredConfirmations", 0),
            "exchangeRate": swap["exchangeRate"]
        }
    
    async def send_direct_message(self, bot, user_id, message):
        """Send a direct message to a user"""
        try:
            user = await bot.fetch_user(int(user_id))
            await user.send(message)
            return True
        except Exception as e:
            print(f"Failed to send DM to user {user_id}: {str(e)}")
            return False
    
    def is_token_supported(self, token_symbol):
        """Check if token is supported"""
        return any(
            token["symbol"].lower() == token_symbol.lower()
            for token in config["supportedTokens"]
        )
    
    async def get_exchange_rate(self, from_currency, to_currency):
        """Get exchange rate between two currencies (mock implementation)"""
        # In a real implementation, this would fetch rates from DEX APIs
        # For this demo, we'll use a mock implementation
        mock_rates = {
            'BTC-ETH': 15.2,
            'ETH-BTC': 0.065,
            'BTC-LTC': 250,
            'LTC-BTC': 0.004,
            'ETH-LTC': 16.5,
            'LTC-ETH': 0.06,
            'BTC-XRP': 50000,
            'XRP-BTC': 0.00002,
            'ETH-XRP': 3300,
            'XRP-ETH': 0.0003,
            'BTC-SOL': 500,
            'SOL-BTC': 0.002,
            'ETH-SOL': 33,
            'SOL-ETH': 0.03,
            'BTC-DOGE': 100000,
            'DOGE-BTC': 0.00001,
            'BTC-BCH': 50,
            'BCH-BTC': 0.02,
            'BTC-XMR': 150,
            'XMR-BTC': 0.0066,
            'BTC-TRX': 200000,
            'TRX-BTC': 0.000005
        }

        pair = f"{from_currency}-{to_currency}"
        
        if pair in mock_rates:
            return {
                "rate": mock_rates[pair],
                "source": "MockAPI",
                "fee": config["defaultFee"]
            }
        
        raise ValueError(f"Exchange rate not available for {pair}")
    
    async def find_best_exchange_rate(self, from_currency, to_currency, amount):
        """Find the best exchange rate from multiple DEXs"""
        # In a real implementation, this would query multiple DEX APIs
        # For this demo, we just use our mock implementation
        return await self.get_exchange_rate(from_currency, to_currency)
    
    def calculate_fee(self, amount, fee_percentage):
        """Calculate the service fee"""
        return amount * (fee_percentage / 100)
    
    async def meets_minimum_amount(self, amount, currency):
        """Check if an amount meets the minimum swap requirement"""
        # In a real implementation, this would convert to USD and check
        # For this demo, we'll assume 1 unit of any currency is above $1
        return amount >= 1
    
    def create_embed(self, title, description, fields=None, color=0xff9900):
        """Create embed for Discord messages"""
        if fields is None:
            fields = []
            
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        
        for field in fields:
            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=field.get("inline", False)
            )
            
        embed.timestamp = discord.utils.utcnow()
        embed.set_footer(text="CoinKong Bot")
        
        return embed
