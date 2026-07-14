"""
Outlook Bulk Mail Bot - Main Entry Point
"""
import os
import asyncio
import logging
from dotenv import load_dotenv
from services.outlook_service import OutlookMailService
from services.scheduler import MailScheduler
from bot.discord_bot import start_discord_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mail_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def main():
    """Main application entry point"""
    logger.info("Starting Outlook Bulk Mail Bot...")
    
    # Initialize Outlook service
    outlook_service = OutlookMailService(
        client_id=os.getenv('MICROSOFT_CLIENT_ID'),
        client_secret=os.getenv('MICROSOFT_CLIENT_SECRET'),
        tenant_id=os.getenv('MICROSOFT_TENANT_ID')
    )
    
    # Initialize scheduler
    scheduler = MailScheduler(outlook_service)
    
    # Start bot (Discord/Slack/CLI)
    bot_choice = os.getenv('BOT_TYPE', 'cli')
    
    if bot_choice == 'discord':
        await start_discord_bot(scheduler)
    else:
        await scheduler.start()

if __name__ == "__main__":
    asyncio.run(main())