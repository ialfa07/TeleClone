#!/usr/bin/env python3
"""
Telegram Channel Cloner - Main Entry Point
An improved Telegram channel cloning tool with error handling, logging, and configuration management.
"""

import argparse
import asyncio
import sys
import os
from datetime import datetime

from config import Config
from telegram_cloner import TelegramCloner
from logger_setup import setup_logger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Clone messages from source Telegram channel to target channel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --source @source_channel --target @target_channel
  python main.py --source source_username --target target_username --limit 100
  python main.py --source @source_channel --target @target_channel --resume
        """
    )
    
    parser.add_argument(
        '--source', '-s',
        required=True,
        help='Source channel username (with or without @)'
    )
    
    parser.add_argument(
        '--target', '-t',
        required=True,
        help='Target channel username (with or without @)'
    )
    
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=None,
        help='Limit number of messages to clone (default: all messages)'
    )
    
    parser.add_argument(
        '--resume', '-r',
        action='store_true',
        help='Resume from last cloned message'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=None,
        help='Delay between messages in seconds (overrides config)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=None,
        help='Number of messages to process in each batch (overrides config)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be cloned without actually sending messages'
    )
    
    return parser.parse_args()


async def main():
    """Main application entry point."""
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logger(args.log_level)
    
    try:
        # Load configuration
        config = Config()
        logger.info("Loading configuration...")
        
        # Override config with command line arguments if provided
        if args.delay is not None:
            config.rate_limit_delay = args.delay
        if args.batch_size is not None:
            config.batch_size = args.batch_size
            
        # Validate configuration
        if not config.validate():
            logger.error("Configuration validation failed. Please check your .env file.")
            return 1
            
        # Initialize Telegram cloner
        cloner = TelegramCloner(config, logger)
        
        logger.info("Starting Telegram Channel Cloner")
        logger.info(f"Source Channel: {args.source}")
        logger.info(f"Target Channel: {args.target}")
        logger.info(f"Message Limit: {args.limit or 'No limit'}")
        logger.info(f"Resume Mode: {'Enabled' if args.resume else 'Disabled'}")
        logger.info(f"Dry Run: {'Enabled' if args.dry_run else 'Disabled'}")
        
        # Start cloning process
        start_time = datetime.now()
        
        success = await cloner.clone_channel(
            source_channel=args.source,
            target_channel=args.target,
            message_limit=args.limit,
            resume=args.resume,
            dry_run=args.dry_run
        )
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        if success:
            logger.info(f"Cloning completed successfully in {duration}")
            return 0
        else:
            logger.error(f"Cloning failed after {duration}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return 1


if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)
