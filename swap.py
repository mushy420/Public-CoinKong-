import asyncio
import random
import json
import aiohttp
from config import config

class SwapService:
    """Service for processing cryptocurrency swaps"""
    
    def __init__(self):
        self.active_swaps = {}
        self.completed_swaps = {}
    
    async def initiate_swap_with_dex(self, swap_record):
        """Initiate a swap with an actual DEX (simulated for demo)"""
        # Choose a random DEX from the configured list
        dex = random.choice(config["dexAPIs"])
        from_currency = swap_record["fromCurrency"]
        to_currency = swap_record["toCurrency"]
        amount = swap_record["fromAmount"]
        
        try:
            # Simulate API call to DEX
            print(f"Initiating swap with {dex['name']}: {amount} {from_currency} → {to_currency}")
            
            # In a real implementation, this would be an actual API call
            # For demo purposes, we'll simulate a response
            
            # Simulate network delay
            await asyncio.sleep(2)
            
            # Generate a mock transaction ID from the DEX
            tx_id = f"{dex['name'].lower()}-{random.randint(10000, 99999)}"
            
            return {
                "success": True,
                "dex": dex["name"],
                "txId": tx_id,
                "exchangeRate": swap_record["exchangeRate"],
                "estimatedCompletionTime": "2-10 minutes"
            }
        except Exception as e:
            print(f"Error initiating swap with DEX: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_swap(self, bot, swap_record):
        """Process a swap asynchronously with proper tracking"""
        swap_id = swap_record["id"]
        user_id = swap_record["userId"]
        
        # Store the swap in active swaps
        self.active_swaps[swap_id] = swap_record
        
        # Update swap status to "initiating"
        swap_record["status"] = "initiating"
        
        # Notify user about initiation
        embed = bot.utils.create_embed(
            title="🔄 Swap Initiated",
            description=f"Your swap request is being processed.",
            fields=[
                {"name": "💼 Swap ID", "value": swap_id},
                {"name": "💱 Status", "value": "Initiating"},
                {"name": "⏳ Estimated Time", "value": "2-10 minutes"},
            ],
            color=0x3498db  # Blue color
        )
        
        try:
            user = await bot.fetch_user(int(user_id))
            await user.send(embed=embed)
        except Exception as e:
            print(f"Could not send initiation DM to user {user_id}: {str(e)}")
        
        # Simulate initial processing
        await asyncio.sleep(3)
        
        # Actually initiate the swap with a DEX
        dex_result = await self.initiate_swap_with_dex(swap_record)
        
        if not dex_result["success"]:
            # DEX swap failed
            swap_record["status"] = "failed"
            swap_record["error"] = dex_result.get("error", "Unknown error")
            
            error_embed = bot.utils.create_embed(
                title="❌ Swap Failed",
                description=f"Your swap could not be initiated with the exchange.",
                fields=[
                    {"name": "💼 Swap ID", "value": swap_id},
                    {"name": "❌ Error", "value": swap_record["error"]},
                    {"name": "📞 Support", "value": "Please contact support for assistance."}
                ],
                color=0xe74c3c  # Red color
            )
            
            try:
                user = await bot.fetch_user(int(user_id))
                await user.send(embed=error_embed)
            except:
                print(f"Could not send error DM to user {user_id}")
                
            # Move to completed swaps (as failed)
            self.completed_swaps[swap_id] = swap_record
            del self.active_swaps[swap_id]
            return
        
        # Update swap with DEX information
        swap_record["dexName"] = dex_result["dex"]
        swap_record["dexTxId"] = dex_result["txId"]
        swap_record["status"] = "processing"
        
        # Notify user that DEX has accepted the swap
        processing_embed = bot.utils.create_embed(
            title="⚙️ Swap Processing",
            description=f"Your swap request has been accepted by the exchange and is now processing.",
            fields=[
                {"name": "💼 Swap ID", "value": swap_id},
                {"name": "🏦 Exchange", "value": dex_result["dex"]},
                {"name": "🔢 Transaction ID", "value": dex_result["txId"]},
                {"name": "⌛ Estimated Time", "value": dex_result["estimatedCompletionTime"]},
            ],
            color=0xf39c12  # Orange color
        )
        
        try:
            user = await bot.fetch_user(int(user_id))
            await user.send(embed=processing_embed)
        except:
            print(f"Could not send processing DM to user {user_id}")
        
        # Simulate exchange processing time
        await asyncio.sleep(10)  # Reduced for demo purposes
        
        # Simulate success (with a small chance of failure)
        success = random.random() > 0.1  # 90% chance of success
        
        swap_record["status"] = "completed" if success else "failed"
        
        # Generate final swap details
        status_message = "Your swap has been completed successfully!" if success else "Your swap has failed. Please try again or contact support."
        status_color = 0x2ecc71 if success else 0xe74c3c  # Green if success, red if failed
        
        # Calculate fees for clarity
        platform_fee = swap_record["platformFee"]
        exchange_fee = swap_record["exchangeFee"]
        total_fee = platform_fee + exchange_fee
        
        embed = bot.utils.create_embed(
            title="✅ Swap Completed" if success else "❌ Swap Failed",
            description=status_message,
            fields=[
                {"name": "💼 Swap ID", "value": swap_id},
                {"name": "💱 From", "value": f"${swap_record['usdAmount']} (= {swap_record['fromAmount']} {swap_record['fromCurrency']})"},
                {"name": "💰 To", "value": f"{swap_record['toAmount']} {swap_record['toCurrency']}"},
                {"name": "💹 Exchange Rate", "value": f"1 {swap_record['fromCurrency']} = {swap_record['exchangeRate']} {swap_record['toCurrency']}"},
                {"name": "🏦 Exchange", "value": swap_record["dexName"]},
                {"name": "💸 Exchange Fee", "value": f"{swap_record['exchangeFee']} {swap_record['toCurrency']} ({swap_record['exchangeFeePercent']}%)"},
                {"name": "🤖 Platform Fee", "value": f"{swap_record['platformFee']} {swap_record['toCurrency']} ({swap_record['platformFeePercent']}%)"},
                {"name": "💵 Total Fees", "value": f"{total_fee} {swap_record['toCurrency']} ({swap_record['exchangeFeePercent'] + swap_record['platformFeePercent']}%)"},
                {"name": "📊 Status", "value": swap_record["status"].capitalize()},
                {"name": "🕒 Completed At", "value": bot.utils.get_timestamp()},
            ],
            color=status_color
        )
        
        try:
            user = await bot.fetch_user(int(user_id))
            await user.send(embed=embed)
        except:
            print(f"Could not send final DM to user {user_id}")
            
        # Move to completed swaps
        self.completed_swaps[swap_id] = swap_record
        del self.active_swaps[swap_id]
        
    def get_all_swaps(self):
        """Get all swaps (active and completed)"""
        return {**self.active_swaps, **self.completed_swaps}
        
    def get_active_swaps(self):
        """Get all active swaps"""
        return self.active_swaps
        
    def get_completed_swaps(self):
        """Get all completed swaps"""
        return self.completed_swaps
