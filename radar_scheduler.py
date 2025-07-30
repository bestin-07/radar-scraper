#!/usr/bin/env python3
"""
Kerala Radar Scheduler - Automated Radar Data Collection

Professional scheduling system for automated hourly radar data collection.
Supports flexible timing options and robust error handling.
"""

import time
import schedule
from datetime import datetime
from radar_scraper import download_all_radar_types


def scheduled_radar_download():
    """Run the radar download and log the results"""
    print(f"\n{'='*60}")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"🕐 Scheduled radar download at {timestamp}")
    print(f"{'='*60}")

    try:
        results = download_all_radar_types()

        # Log success/failure
        success_count = sum(1 for r in results.values() if r['success'])
        total_count = len(results)

        if success_count == total_count:
            print(f"✅ All {total_count} radar types downloaded successfully!")
        else:
            print(f"⚠️  Downloaded {success_count}/{total_count} radar types")

            # Show which ones failed
            failed_types = [radar_type for radar_type, result in
                            results.items() if not result['success']]
            if failed_types:
                print(f"   ❌ Failed: {', '.join(failed_types)}")

        return True
    except Exception as e:
        print(f"❌ Error during scheduled download: {e}")
        return False


def run_scheduler():
    """Run the scheduler with hourly downloads"""
    print("🚀 Kerala Radar Scheduler Starting...")
    print("⏰ Scheduled to run every hour on the hour")
    print("📊 Will download 7 radar types: CAZ, PPZ, PPI, ZDR, VP2, 3DS, MAXZ")
    print("\nPress Ctrl+C to stop the scheduler\n")

    # Schedule downloads every hour at the start of the hour
    schedule.every().hour.at(":00").do(scheduled_radar_download)

    # Also run immediately when starting
    print("🏃 Running initial download...")
    scheduled_radar_download()

    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        print("\n\n🛑 Scheduler stopped by user")
        print("👋 Goodbye!")


def run_custom_interval(minutes=60):
    """Run with a custom interval in minutes"""
    print("🚀 Kerala Radar Scheduler Starting...")
    print(f"⏰ Scheduled to run every {minutes} minutes")
    print("📊 Will download 7 radar types: CAZ, PPZ, PPI, ZDR, VP2, 3DS, MAXZ")
    print("\nPress Ctrl+C to stop the scheduler\n")

    # Schedule downloads every specified minutes
    schedule.every(minutes).minutes.do(scheduled_radar_download)

    # Run immediately when starting
    print("🏃 Running initial download...")
    scheduled_radar_download()

    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        print("\n\n🛑 Scheduler stopped by user")
        print("👋 Goodbye!")


if __name__ == "__main__":
    # You can choose different scheduling options:

    # Option 1: Run every hour on the hour (recommended for radar data)
    run_scheduler()

    # Option 2: Run every 30 minutes (uncomment to use)
    # run_custom_interval(30)

    # Option 3: Run every 15 minutes (uncomment to use)
    # run_custom_interval(15)
