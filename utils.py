import discord
import random
import time
import asyncio
import json
import aiohttp
from config import config

class Utils:
    """Utility functions for the bot"""
    
    def __init__(self):
        # Mock USD rates for demo purposes
        self.usd_rates = {
            'BTC': 35000,
            'ETH': 2300,
            'LTC': 75,
            'XRP': 0.7,
            'SOL': 65,
            'DOGE': 0.08,
            'BCH': 250,
            'XMR': 150,
            'TRX': 0.1
        }
        
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
        """Check if a user can use the bot (not blacklisted and either not in maintenance or whitelisted or owner)"""
        if self.is_blacklisted(user_id):
            return False
        
        # Maintenance mode check - owners can always use the bot
        if self.is_owner(user_id):
            return True
            
        # In maintenance mode, only whitelisted users can use the bot
        if self.is_in_maintenance() and not self.is_whitelisted(user_id):
            return False
            
        return True
    
    def format_currency(self, amount, currency):
        """Format a currency amount for display"""
        if currency == "USD":
            return f"${amount:.2f}"
        return f"{amount:.8f}".rstrip('0').rstrip('.') + f" {currency}"
    
    def generate_swap_id(self):
        """Generate a unique swap ID"""
        return f"KONG-{int(time.time())}-{random.randint(0, 999)}"
    
    def get_timestamp(self):
        """Get current timestamp"""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    def format_swap_record(self, swap):
        """Format a swap record for display"""
        # Calculate total fees
        exchange_fee = swap.get('exchangeFee', 0)
        platform_fee = swap.get('platformFee', 0)
        total_fee = exchange_fee + platform_fee
        
        return {
            "id": swap["id"],
            "status": swap["status"],
            "fromAmount": self.format_currency(swap["fromAmount"], swap["fromCurrency"]),
            "usdAmount": self.format_currency(swap.get("usdAmount", 0), "USD"),
            "toAmount": self.format_currency(swap["toAmount"], swap["toCurrency"]),
            "exchangeFee": self.format_currency(swap.get("exchangeFee", 0), swap["toCurrency"]),
            "platformFee": self.format_currency(swap.get("platformFee", 0), swap["toCurrency"]),
            "totalFee": self.format_currency(total_fee, swap["toCurrency"]),
            "exchangeFeePercent": f"{swap.get('exchangeFeePercent', 0)}%",
            "platformFeePercent": f"{swap.get('platformFeePercent', 0)}%",
            "totalFeePercent": f"{swap.get('exchangeFeePercent', 0) + swap.get('platformFeePercent', 0)}%",
            "fee": f"{swap.get('fee', 0)}%",
            "initiatedAt": swap["timestamp"],
            "userId": swap["userId"],
            "sourceAddress": swap.get("sourceAddress", "N/A"),
            "destinationAddress": swap.get("destinationAddress", "N/A"),
            "confirmations": swap.get("confirmations", 0),
            "requiredConfirmations": swap.get("requiredConfirmations", 0),
            "exchangeRate": swap["exchangeRate"],
            "dexName": swap.get("dexName", "N/A"),
            "dexTxId": swap.get("dexTxId", "N/A")
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
    
    def get_usd_rate(self, currency):
        """Get USD rate for a currency"""
        return self.usd_rates.get(currency.upper(), 1.0)
    
    def usd_to_crypto(self, usd_amount, currency):
        """Convert USD to cryptocurrency amount"""
        rate = self.get_usd_rate(currency)
        if rate <= 0:
            return 0
        return usd_amount / rate
    
    def crypto_to_usd(self, crypto_amount, currency):
        """Convert cryptocurrency to USD amount"""
        rate = self.get_usd_rate(currency)
        return crypto_amount * rate
    
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
        
        # Add a small random variation to simulate market movements
        variation = 1 + (random.random() - 0.5) * 0.02  # +/- 1%
        
        if pair in mock_rates:
            base_rate = mock_rates[pair]
            current_rate = base_rate * variation
            
            # Mock exchange fee (0.1% to 0.3%)
            exchange_fee_percent = random.uniform(0.1, 0.3)
            
            return {
                "rate": current_rate,
                "source": "MockAPI",
                "exchangeFeePercent": exchange_fee_percent,
                "platformFeePercent": config["defaultFee"]
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
    
    async def meets_minimum_amount(self, usd_amount):
        """Check if USD amount meets the minimum swap requirement"""
        return usd_amount >= config["minimumSwapAmountUSD"]
    
    def create_embed(self, title, description, fields=None, color=0xff9900):
        """Create embed for Discord messages with improved styling"""
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
        
        # Add a fancy footer with the bot name
        embed.set_footer(text="🦍 CoinKong Bot | Crypto Swaps Made Simple", 
                         icon_url="https://cdn.discordapp.com/attachments/1179286008138305617/1191166853750788096/bot_profile_pic.png?ex=65a84c40&is=6595d740&hm=76ce5d4e6cb775a9db3d5e0935b87e97d7a8fc873ac3d37dc5c7c9a001a12f36&")
        
        return embed
