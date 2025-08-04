#!/usr/bin/env python3
"""
Telegram News Scraper CLI Tool

A professional CLI tool for scraping news from Ethiopian Telegram channels.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.settings import Config
from src.core.database import db_manager
from src.scrapers.telegram_scraper import TelegramScraper
from src.utils.logger import logger

app = typer.Typer(
    name="telegram-scraper",
    help="Professional Telegram news scraper for Ethiopian channels",
    add_completion=False
)

console = Console()

@app.command()
def clear():
    """Clear all data from the database"""
    try:
        with db_manager.get_session() as session:
            from src.models.database import TelegramChannel, TelegramPost, ScrapingLog
            
            # Clear all data
            session.query(ScrapingLog).delete()
            session.query(TelegramPost).delete()
            session.query(TelegramChannel).delete()
            session.commit()
            
            console.print("🗑️  All data cleared from database!", style="green")
            
    except Exception as e:
        console.print(f"❌ Error clearing database: {e}", style="red")
        raise typer.Exit(1)

@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Force recreate database tables")
):
    """Initialize the database and create tables"""
    try:
        if force:
            console.print("🗑️  Dropping existing tables...", style="red")
            db_manager.drop_tables()
        
        console.print("🏗️  Creating database tables...", style="blue")
        db_manager.create_tables()
        console.print("✅ Database initialized successfully!", style="green")
        
    except Exception as e:
        console.print(f"❌ Error initializing database: {e}", style="red")
        raise typer.Exit(1)

@app.command()
def scrape(
    channels: Optional[List[str]] = typer.Option(None, "--channel", "-c", help="Specific channels to scrape"),
    posts: int = typer.Option(10, "--posts", "-p", help="Number of posts to scrape per channel"),
    concurrent: int = typer.Option(3, "--concurrent", "-n", help="Number of concurrent channel scrapes"),
    force: bool = typer.Option(False, "--force", "-f", help="Force scrape even if posts exist (skip deduplication)")
):
    """Scrape posts from Telegram channels"""
    
    # Validate configuration
    if not all([Config.TELEGRAM_API_ID, Config.TELEGRAM_API_HASH, Config.TELEGRAM_PHONE]):
        console.print("❌ Telegram API credentials not configured!", style="red")
        console.print("Please set the following environment variables:", style="yellow")
        console.print("  - TELEGRAM_API_ID", style="cyan")
        console.print("  - TELEGRAM_API_HASH", style="cyan")
        console.print("  - TELEGRAM_PHONE", style="cyan")
        raise typer.Exit(1)
    
    async def run_scraping():
        scraper = TelegramScraper()
        
        try:
            # Start Telegram client
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Starting Telegram client...", total=None)
                await scraper.start()
                progress.update(task, description="Telegram client started successfully")
            
            # Filter channels if specified
            channels_to_scrape = Config.TELEGRAM_CHANNELS
            if channels:
                channels_to_scrape = [
                    ch for ch in Config.TELEGRAM_CHANNELS 
                    if ch.username in channels or ch.name.lower() in [c.lower() for c in channels]
                ]
                
                if not channels_to_scrape:
                    console.print("❌ No matching channels found!", style="red")
                    return
            
            # Scrape channels
            console.print(f"\n📡 Scraping {len(channels_to_scrape)} channels...", style="blue")
            
            results = []
            for i, channel_config in enumerate(channels_to_scrape):
                if not channel_config.is_active:
                    continue
                
                console.print(f"\n📺 Scraping: {channel_config.name} (@{channel_config.username})", style="cyan")
                
                result = await scraper.scrape_channel(channel_config, posts, force)
                results.append(result)
                
                # Rate limiting
                if i < len(channels_to_scrape) - 1:
                    await asyncio.sleep(Config.RATE_LIMIT_DELAY)
            
            # Display results
            display_results(results)
            
        except Exception as e:
            console.print(f"❌ Error during scraping: {e}", style="red")
            logger.error(f"Scraping error: {e}")
        finally:
            await scraper.stop()
    
    asyncio.run(run_scraping())

@app.command()
def status():
    """Show scraping status and statistics"""
    try:
        with db_manager.get_session() as session:
            from src.models.database import TelegramChannel, TelegramPost, ScrapingLog
            
            # Get statistics
            total_channels = session.query(TelegramChannel).count()
            total_posts = session.query(TelegramPost).count()
            total_logs = session.query(ScrapingLog).count()
            
            # Get recent activity
            recent_posts = session.query(TelegramPost).order_by(
                TelegramPost.scraped_date.desc()
            ).limit(5).all()
            
            recent_logs = session.query(ScrapingLog).order_by(
                ScrapingLog.created_at.desc()
            ).limit(5).all()
            
            # Display status
            console.print("\n📊 Scraping Status", style="bold blue")
            
            # Statistics table
            stats_table = Table(title="Statistics")
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Count", style="green")
            
            stats_table.add_row("Total Channels", str(total_channels))
            stats_table.add_row("Total Posts", str(total_posts))
            stats_table.add_row("Total Scraping Logs", str(total_logs))
            
            console.print(stats_table)
            
            # Recent posts
            if recent_posts:
                console.print("\n📰 Recent Posts", style="bold blue")
                posts_table = Table()
                posts_table.add_column("Channel", style="cyan")
                posts_table.add_column("Title", style="white")
                posts_table.add_column("Date", style="green")
                
                for post in recent_posts:
                    title = post.title or post.content[:50] + "..." if post.content else "No title"
                    posts_table.add_row(
                        post.channel.name,
                        title,
                        post.scraped_date.strftime("%Y-%m-%d %H:%M")
                    )
                
                console.print(posts_table)
            
            # Recent logs
            if recent_logs:
                console.print("\n📋 Recent Scraping Logs", style="bold blue")
                logs_table = Table()
                logs_table.add_column("Channel", style="cyan")
                logs_table.add_column("Status", style="green")
                logs_table.add_column("Posts Found", style="yellow")
                logs_table.add_column("New Posts", style="green")
                logs_table.add_column("Date", style="blue")
                
                for log in recent_logs:
                    status_color = "green" if log.status == "success" else "red"
                    logs_table.add_row(
                        log.channel.name,
                        log.status,
                        str(log.posts_found),
                        str(log.posts_new),
                        log.created_at.strftime("%Y-%m-%d %H:%M")
                    )
                
                console.print(logs_table)
    
    except Exception as e:
        console.print(f"❌ Error getting status: {e}", style="red")
        raise typer.Exit(1)

@app.command()
def channels():
    """List configured channels"""
    console.print("\n📺 Configured Channels", style="bold blue")
    
    channels_table = Table()
    channels_table.add_column("Name", style="cyan")
    channels_table.add_column("Username", style="green")
    channels_table.add_column("Category", style="yellow")
    channels_table.add_column("Language", style="blue")
    channels_table.add_column("Status", style="red")
    
    for channel in Config.TELEGRAM_CHANNELS:
        status = "✅ Active" if channel.is_active else "❌ Inactive"
        channels_table.add_row(
            channel.name,
            f"@{channel.username}",
            channel.category,
            channel.language,
            status
        )
    
    console.print(channels_table)

def display_results(results: List[dict]):
    """Display scraping results in a nice format"""
    console.print("\n📊 Scraping Results", style="bold blue")
    
    results_table = Table()
    results_table.add_column("Channel", style="cyan")
    results_table.add_column("Posts Found", style="yellow")
    results_table.add_column("New Posts", style="green")
    results_table.add_column("Duplicates", style="red")
    results_table.add_column("Images", style="blue")
    results_table.add_column("Status", style="white")
    
    total_found = 0
    total_new = 0
    total_duplicates = 0
    total_images = 0
    
    for result in results:
        status = "✅ Success" if not result['error'] else f"❌ {result['error']}"
        
        results_table.add_row(
            result['channel_name'],
            str(result['posts_found']),
            str(result['posts_new']),
            str(result['posts_duplicate']),
            str(result['images_downloaded']),
            status
        )
        
        total_found += result['posts_found']
        total_new += result['posts_new']
        total_duplicates += result['posts_duplicate']
        total_images += result['images_downloaded']
    
    console.print(results_table)
    
    # Summary
    summary_text = Text()
    summary_text.append(f"Total Posts Found: {total_found}\n", style="yellow")
    summary_text.append(f"New Posts: {total_new}\n", style="green")
    summary_text.append(f"Duplicates: {total_duplicates}\n", style="red")
    summary_text.append(f"Images Downloaded: {total_images}", style="blue")
    
    console.print(Panel(summary_text, title="Summary", border_style="blue"))

@app.command()
def config():
    """Show current configuration"""
    console.print("\n⚙️  Configuration", style="bold blue")
    
    config_table = Table()
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    
    config_table.add_row("Database URL", Config.DATABASE_URL)
    config_table.add_row("Telegram API ID", Config.TELEGRAM_API_ID or "Not set")
    config_table.add_row("Telegram API Hash", "Set" if Config.TELEGRAM_API_HASH else "Not set")
    config_table.add_row("Telegram Phone", Config.TELEGRAM_PHONE or "Not set")
    config_table.add_row("GCS Bucket", Config.GCS_BUCKET_NAME)
    config_table.add_row("Log Level", Config.LOG_LEVEL)
    config_table.add_row("Rate Limit Delay", f"{Config.RATE_LIMIT_DELAY}s")
    
    console.print(config_table)

if __name__ == "__main__":
    app() 