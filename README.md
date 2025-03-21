
# CoinKong Discord Bot (Python Version)

A powerful Discord bot that enables users to perform cross-chain cryptocurrency swaps directly through Discord.

## Features

- Cross-chain cryptocurrency swaps
- Multi-asset support for major cryptocurrencies
- Integration with decentralized exchanges
- Secure atomic swaps using HTLCs
- User notifications via direct messages
- Administrative commands for bot management

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd coinkong-discord-bot
   ```

2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory with the following variables:
   ```
   DISCORD_BOT_TOKEN=your_bot_token
   DISCORD_CLIENT_ID=your_client_id
   OWNER_ID=your_discord_user_id
   ```

4. **Start the bot:**
   ```
   python main.py
   ```

## Available Commands

### User Commands
- `/swap [amount] [from_currency] [to_currency]`: Perform a crypto-to-crypto swap
- `/status [swap_id]`: Check the status of a swap
- `/supported_tokens`: List all supported cryptocurrencies
- `/support`: Get support information
- `/help`: Display bot usage instructions

### Owner Commands
- `/set_fee [percentage]`: Adjust the swap fee percentage
- `/pause`: Temporarily disable swaps for maintenance
- `/resume`: Re-enable swaps after maintenance
- `/whitelist [userid]`: Allow a user to use the bot during maintenance
- `/blacklist [userid]`: Prevent a user from using the bot
- `/show_order [swap_id]`: Show detailed information about a swap
- `/user_orders [userid]`: List all swaps initiated by a user

## Supported Cryptocurrencies

- Bitcoin (BTC)
- Ethereum (ETH)
- Litecoin (LTC)
- Ripple (XRP)
- Solana (SOL)
- Dogecoin (DOGE)
- Bitcoin Cash (BCH)
- Monero (XMR)
- Tron (TRX)

## DEX Integrations

The bot integrates with various decentralized exchanges to provide the best rates:

- SideShift
- Exolix
- 1inch
- Uniswap
- PancakeSwap

## Important Notes

- The minimum swap amount is $1
- The default service fee is 0.5%
- For support, contact @bammity on Telegram

- Copyright 2025 CoinKong 
