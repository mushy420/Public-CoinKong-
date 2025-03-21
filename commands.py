import discord
from discord import app_commands
import asyncio
from config import config
from swap import SwapService

# Initialize swap service
swap_service = SwapService()

async def register_commands(bot):
    """Register all commands with the bot."""
    
    # User Commands
    @bot.tree.command(name="swap", description="Perform a crypto-to-crypto swap")
    @app_commands.describe(
        usd_amount="Amount in USD to swap",
        from_currency="Source cryptocurrency",
        to_currency="Target cryptocurrency"
    )
    async def swap_command(interaction: discord.Interaction, usd_amount: float, from_currency: str, to_currency: str):
        # Check if user can use the bot
        if not bot.utils.can_use_bot(interaction.user.id):
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="❌ Access Denied",
                    description="You are not allowed to use this command.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
            
        # Check if bot is in maintenance and user is not owner or whitelisted
        if bot.utils.is_in_maintenance() and not (bot.utils.is_whitelisted(interaction.user.id) or bot.utils.is_owner(interaction.user.id)):
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="🛠️ Maintenance Mode",
                    description="Bot is currently in maintenance mode. Please try again later.",
                    color=0xf39c12  # Orange color
                ),
                ephemeral=True
            )
            return
            
        # Validate inputs
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if not bot.utils.is_token_supported(from_currency):
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="❌ Invalid Currency",
                    description=f"Invalid source currency: {from_currency}. Use /supported_tokens to see available options.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
            
        if not bot.utils.is_token_supported(to_currency):
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="❌ Invalid Currency",
                    description=f"Invalid target currency: {to_currency}. Use /supported_tokens to see available options.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
            
        if from_currency == to_currency:
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="❌ Invalid Swap",
                    description="Source and target currencies cannot be the same.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
            
        if usd_amount <= 0:
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="❌ Invalid Amount",
                    description="Amount must be greater than zero.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
            
        # Check minimum amount
        if not await bot.utils.meets_minimum_amount(usd_amount):
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="❌ Below Minimum",
                    description=f"Amount is below the minimum required (${config['minimumSwapAmountUSD']} USD).",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
        
        await interaction.response.defer(thinking=True)
        
        try:
            # Convert USD to source cryptocurrency
            crypto_amount = bot.utils.usd_to_crypto(usd_amount, from_currency)
            if crypto_amount <= 0:
                await interaction.followup.send(
                    embed=bot.utils.create_embed(
                        title="❌ Conversion Error",
                        description=f"Could not convert ${usd_amount} to {from_currency}.",
                        color=0xe74c3c  # Red color
                    ),
                    ephemeral=True
                )
                return
            
            # Get exchange rate
            rate_info = await bot.utils.find_best_exchange_rate(from_currency, to_currency, crypto_amount)
            estimated_amount = crypto_amount * rate_info["rate"]
            
            # Calculate fees
            platform_fee_percent = rate_info["platformFeePercent"]
            exchange_fee_percent = rate_info["exchangeFeePercent"]
            
            platform_fee = bot.utils.calculate_fee(estimated_amount, platform_fee_percent)
            exchange_fee = bot.utils.calculate_fee(estimated_amount, exchange_fee_percent)
            
            total_fee = platform_fee + exchange_fee
            final_amount = estimated_amount - total_fee
            
            # Create a new swap record
            swap_id = bot.utils.generate_swap_id()
            
            # In a real implementation, we would ask for the user's wallet addresses here
            # For this demo, we'll use placeholder addresses
            source_address = "source_wallet_address"
            destination_address = "destination_wallet_address"
            
            swap_record = {
                "id": swap_id,
                "userId": str(interaction.user.id),
                "fromCurrency": from_currency,
                "toCurrency": to_currency,
                "usdAmount": usd_amount,
                "fromAmount": crypto_amount,
                "toAmount": final_amount,
                "exchangeRate": rate_info["rate"],
                "platformFee": platform_fee,
                "exchangeFee": exchange_fee,
                "platformFeePercent": platform_fee_percent,
                "exchangeFeePercent": exchange_fee_percent,
                "fee": platform_fee_percent + exchange_fee_percent,  # Total fee percentage
                "status": "pending",
                "timestamp": bot.utils.get_timestamp(),
                "sourceAddress": source_address,
                "destinationAddress": destination_address
            }
            
            # Store the swap record
            swap_service.active_swaps[swap_id] = swap_record
            
            # Create response embed
            embed = bot.utils.create_embed(
                title="🚀 Swap Initiated",
                description=f"Your swap request has been submitted successfully.",
                fields=[
                    {"name": "💼 Swap ID", "value": swap_id},
                    {"name": "💵 USD Amount", "value": f"${usd_amount:.2f}"},
                    {"name": "💱 From", "value": f"{bot.utils.format_currency(crypto_amount, from_currency)}"},
                    {"name": "💰 To (Estimated)", "value": f"{bot.utils.format_currency(final_amount, to_currency)}"},
                    {"name": "📈 Exchange Rate", "value": f"1 {from_currency} = {rate_info['rate']} {to_currency}"},
                    {"name": "🏦 Exchange Fee", "value": f"{exchange_fee_percent}% ({bot.utils.format_currency(exchange_fee, to_currency)})"},
                    {"name": "🤖 Platform Fee", "value": f"{platform_fee_percent}% ({bot.utils.format_currency(platform_fee, to_currency)})"},
                    {"name": "💵 Total Fees", "value": f"{platform_fee_percent + exchange_fee_percent}% ({bot.utils.format_currency(total_fee, to_currency)})"},
                    {"name": "📊 Status", "value": "Pending"},
                ],
                color=0x3498db  # Blue color
            )
            
            await interaction.followup.send(embed=embed)
            
            # Process the swap
            asyncio.create_task(swap_service.process_swap(bot, swap_record))
            
        except Exception as error:
            await interaction.followup.send(
                embed=bot.utils.create_embed(
                    title="❌ Error",
                    description=f"An error occurred while processing your swap request: {str(error)}",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )

    @bot.tree.command(name="status", description="Check the status of a swap")
    @app_commands.describe(swap_id="The ID of the swap to check")
    async def status_command(interaction: discord.Interaction, swap_id: str):
        # Check if user can use the bot
        if not bot.utils.can_use_bot(interaction.user.id):
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="❌ Access Denied",
                    description="You are not allowed to use this command.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
        
        # Get all swaps (active and completed)
        all_swaps = swap_service.get_all_swaps()
            
        if swap_id not in all_swaps:
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="❓ Not Found",
                    description=f"Swap with ID {swap_id} not found.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
            
        swap = all_swaps[swap_id]
        
        # Check if this swap belongs to the user
        if swap["userId"] != str(interaction.user.id) and not bot.utils.is_owner(interaction.user.id):
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="🔒 Access Denied",
                    description="You don't have permission to view this swap.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
            
        # Format and display swap status
        formatted_swap = bot.utils.format_swap_record(swap)
        
        # Choose color based on status
        status_colors = {
            "pending": 0x3498db,    # Blue
            "initiating": 0x3498db, # Blue
            "processing": 0xf39c12, # Orange
            "completed": 0x2ecc71,  # Green
            "failed": 0xe74c3c      # Red
        }
        status_color = status_colors.get(swap["status"].lower(), 0x95a5a6)  # Gray default
        
        # Create appropriate emoji for status
        status_emojis = {
            "pending": "⏳",
            "initiating": "🔄",
            "processing": "⚙️",
            "completed": "✅",
            "failed": "❌"
        }
        status_emoji = status_emojis.get(swap["status"].lower(), "❓")
        
        fields = [
            {"name": "💱 From", "value": f"{formatted_swap['usdAmount']} (= {formatted_swap['fromAmount']})"},
            {"name": "💰 To", "value": formatted_swap["toAmount"]},
            {"name": "📈 Exchange Rate", "value": f"1 {swap['fromCurrency']} = {swap['exchangeRate']} {swap['toCurrency']}"},
            {"name": "🤖 Platform Fee", "value": f"{formatted_swap['platformFeePercent']} ({formatted_swap['platformFee']})"},
            {"name": "🏦 Exchange Fee", "value": f"{formatted_swap['exchangeFeePercent']} ({formatted_swap['exchangeFee']})"},
            {"name": "🕒 Initiated At", "value": formatted_swap["initiatedAt"]},
        ]
        
        # Add exchange information if available
        if swap.get("dexName", "N/A") != "N/A":
            fields.append({"name": "🏛️ Exchange", "value": swap["dexName"]})
            
        if swap.get("dexTxId", "N/A") != "N/A":
            fields.append({"name": "🔢 Transaction ID", "value": swap["dexTxId"]})
        
        embed = bot.utils.create_embed(
            title=f"🔍 Swap Status: {swap_id}",
            description=f"Current status: {status_emoji} {swap['status'].capitalize()}",
            fields=fields,
            color=status_color
        )
        
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="supported_tokens", description="List all supported cryptocurrencies")
    async def supported_tokens_command(interaction: discord.Interaction):
        tokens = config["supportedTokens"]
        
        # Create a formatted list of tokens with emojis
        token_emojis = {
            "BTC": "₿",
            "ETH": "Ξ",
            "LTC": "Ł",
            "XRP": "✕",
            "SOL": "◎",
            "DOGE": "Ð",
            "BCH": "₿",
            "XMR": "ɱ",
            "TRX": "♅"
        }
        
        token_list = "\n".join([
            f"• {token_emojis.get(token['symbol'], '🪙')} {token['symbol']} ({token['name']}) on {token['network']}" 
            for token in tokens
        ])
        
        embed = bot.utils.create_embed(
            title="🪙 Supported Cryptocurrencies",
            description=f"The following cryptocurrencies are currently supported:\n\n{token_list}",
            color=0x3498db  # Blue color
        )
        
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="support", description="Get support information")
    async def support_command(interaction: discord.Interaction):
        embed = bot.utils.create_embed(
            title="🆘 CoinKong Support",
            description="Need help with CoinKong Bot?",
            fields=[
                {"name": "📞 Contact", "value": "For support, contact @bammity on Telegram"},
                {"name": "🤖 Commands", "value": "Use /help to see available commands"},
                {"name": "💰 Minimum Swap", "value": f"${config['minimumSwapAmountUSD']} USD equivalent"},
                {"name": "💸 Platform Fee", "value": f"{config['defaultFee']}% (configurable by owner)"},
                {"name": "🏦 Exchange Fee", "value": "Varies by exchange (typically 0.1-0.3%)"}
            ],
            color=0x9b59b6  # Purple color
        )
        
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="help", description="Display bot usage instructions")
    async def help_command(interaction: discord.Interaction):
        user_commands = [
            "• `/swap [usd_amount] [from_currency] [to_currency]` - Perform a crypto-to-crypto swap",
            "• `/status [swap_id]` - Check the status of a swap",
            "• `/supported_tokens` - List all supported cryptocurrencies",
            "• `/support` - Get support information",
            "• `/help` - Display this help message"
        ]
        
        owner_commands = [
            "• `/set_fee [percentage]` - Adjust the platform fee percentage",
            "• `/pause` - Temporarily disable swaps for maintenance",
            "• `/resume` - Re-enable swaps after maintenance",
            "• `/whitelist [userid]` - Allow a user to use the bot during maintenance",
            "• `/blacklist [userid]` - Prevent a user from using the bot",
            "• `/show_order [swap_id]` - Show detailed information about a swap",
            "• `/user_orders [userid]` - List all swaps initiated by a user"
        ]
        
        embed = bot.utils.create_embed(
            title="📖 CoinKong Bot Help",
            description="Here are the available commands:",
            fields=[
                {"name": "👤 User Commands", "value": "\n".join(user_commands)},
                {"name": "👑 Owner Commands", "value": "\n".join(owner_commands)}
            ],
            color=0x3498db  # Blue color
        )
        
        await interaction.response.send_message(embed=embed)

    # Owner Commands
    @bot.tree.command(name="set_fee", description="Adjust the platform fee percentage")
    @app_commands.describe(percentage="New fee percentage (0.0-100.0)")
    async def set_fee_command(interaction: discord.Interaction, percentage: float):
        if not bot.utils.is_owner(interaction.user.id):
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="🔒 Access Denied",
                    description="You don't have permission to use this command.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
            
        if percentage < 0 or percentage > 100:
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="❌ Invalid Value",
                    description="Percentage must be between 0 and 100.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
            
        config["defaultFee"] = percentage
        
        await interaction.response.send_message(
            embed=bot.utils.create_embed(
                title="✅ Fee Updated",
                description=f"Platform fee percentage has been updated to {percentage}%.",
                color=0x2ecc71  # Green color
            )
        )

    @bot.tree.command(name="pause", description="Temporarily disable swaps for maintenance")
    async def pause_command(interaction: discord.Interaction):
        if not bot.utils.is_owner(interaction.user.id):
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="🔒 Access Denied",
                    description="You don't have permission to use this command.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
            
        config["isPaused"] = True
        
        await interaction.response.send_message(
            embed=bot.utils.create_embed(
                title="🛑 Bot Paused",
                description="Bot has been paused for maintenance. Only whitelisted users can use swap functionality.",
                color=0xf39c12  # Orange color
            )
        )

    @bot.tree.command(name="resume", description="Re-enable swaps after maintenance")
    async def resume_command(interaction: discord.Interaction):
        if not bot.utils.is_owner(interaction.user.id):
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="🔒 Access Denied",
                    description="You don't have permission to use this command.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
            
        config["isPaused"] = False
        
        await interaction.response.send_message(
            embed=bot.utils.create_embed(
                title="▶️ Bot Resumed",
                description="Bot has been resumed. All users can now use swap functionality.",
                color=0x2ecc71  # Green color
            )
        )

    @bot.tree.command(name="whitelist", description="Allow a user to use the bot during maintenance")
    @app_commands.describe(user_id="Discord user ID to whitelist")
    async def whitelist_command(interaction: discord.Interaction, user_id: str):
        if not bot.utils.is_owner(interaction.user.id):
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="🔒 Access Denied",
                    description="You don't have permission to use this command.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
            
        if user_id in config["whitelistedUsers"]:
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="ℹ️ Already Whitelisted",
                    description=f"User {user_id} is already whitelisted.",
                    color=0x3498db  # Blue color
                ),
                ephemeral=True
            )
            return
            
        config["whitelistedUsers"].append(user_id)
        
        await interaction.response.send_message(
            embed=bot.utils.create_embed(
                title="✅ User Whitelisted",
                description=f"User {user_id} has been added to the whitelist.",
                color=0x2ecc71  # Green color
            )
        )

    @bot.tree.command(name="blacklist", description="Prevent a user from using the bot")
    @app_commands.describe(user_id="Discord user ID to blacklist")
    async def blacklist_command(interaction: discord.Interaction, user_id: str):
        if not bot.utils.is_owner(interaction.user.id):
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="🔒 Access Denied",
                    description="You don't have permission to use this command.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
            
        if user_id in config["blacklistedUsers"]:
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="ℹ️ Already Blacklisted",
                    description=f"User {user_id} is already blacklisted.",
                    color=0x3498db  # Blue color
                ),
                ephemeral=True
            )
            return
            
        config["blacklistedUsers"].append(user_id)
        
        await interaction.response.send_message(
            embed=bot.utils.create_embed(
                title="✅ User Blacklisted",
                description=f"User {user_id} has been added to the blacklist.",
                color=0x2ecc71  # Green color
            )
        )

    @bot.tree.command(name="show_order", description="Show detailed information about a swap")
    @app_commands.describe(swap_id="The ID of the swap to view")
    async def show_order_command(interaction: discord.Interaction, swap_id: str):
        if not bot.utils.is_owner(interaction.user.id):
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="🔒 Access Denied",
                    description="You don't have permission to use this command.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
        
        # Get all swaps (active and completed)
        all_swaps = swap_service.get_all_swaps()
            
        if swap_id not in all_swaps:
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="❓ Not Found",
                    description=f"Swap with ID {swap_id} not found.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
            
        swap = all_swaps[swap_id]
        formatted_swap = bot.utils.format_swap_record(swap)
        
        # Create a detailed embed with all swap information
        fields = []
        for key, value in formatted_swap.items():
            # Skip redundant fields that would make the embed too large
            if key not in ["fromAmount", "toAmount", "exchangeFee", "platformFee", "fee"]:
                fields.append({"name": key, "value": str(value)})
        
        # Choose color based on status
        status_colors = {
            "pending": 0x3498db,    # Blue
            "initiating": 0x3498db, # Blue
            "processing": 0xf39c12, # Orange
            "completed": 0x2ecc71,  # Green
            "failed": 0xe74c3c      # Red
        }
        status_color = status_colors.get(swap["status"].lower(), 0x95a5a6)  # Gray default
        
        embed = bot.utils.create_embed(
            title=f"🔍 Swap Details: {swap_id}",
            description=f"Full details for swap {swap_id}",
            fields=fields,
            color=status_color
        )
        
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="user_orders", description="List all swaps initiated by a user")
    @app_commands.describe(user_id="Discord user ID to check")
    async def user_orders_command(interaction: discord.Interaction, user_id: str):
        if not bot.utils.is_owner(interaction.user.id):
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="🔒 Access Denied",
                    description="You don't have permission to use this command.",
                    color=0xe74c3c  # Red color
                ),
                ephemeral=True
            )
            return
        
        # Get all swaps from both active and completed
        all_swaps = swap_service.get_all_swaps()
        user_swaps = [swap for swap in all_swaps.values() if swap["userId"] == user_id]
        
        if not user_swaps:
            await interaction.response.send_message(
                embed=bot.utils.create_embed(
                    title="❓ No Swaps Found",
                    description=f"No swaps found for user {user_id}.",
                    color=0x3498db  # Blue color
                ),
                ephemeral=True
            )
            return
            
        # Format the list of swaps with emojis for status
        status_emojis = {
            "pending": "⏳",
            "initiating": "🔄",
            "processing": "⚙️",
            "completed": "✅",
            "failed": "❌"
        }
        
        swap_list = "\n".join([
            f"• {status_emojis.get(swap['status'].lower(), '❓')} {swap['id']}: ${swap.get('usdAmount', 0):.2f} → {swap['fromAmount']} {swap['fromCurrency']} → {swap['toAmount']} {swap['toCurrency']} ({swap['status']})"
            for swap in user_swaps
        ])
        
        embed = bot.utils.create_embed(
            title=f"📋 Swaps for User {user_id}",
            description=f"Found {len(user_swaps)} swaps:\n\n{swap_list}",
            color=0x3498db  # Blue color
        )
        
        await interaction.response.send_message(embed=embed)
