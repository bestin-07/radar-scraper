#!/usr/bin/env python3
"""
Radar Data Analyzer - Analyze and report on downloaded radar data

This utility helps you understand what radar data you have collected,
file sizes, timestamps, and provides cleanup options.
"""

from pathlib import Path
from datetime import datetime


def analyze_radar_directory():
    """Analyze all downloaded radar data"""
    base_dir = Path("radar_images")
    if not base_dir.exists():
        print("❌ No radar_images directory found!")
        return

    print("📊 Kerala Radar Data Analysis")
    print("=" * 50)

    total_files = 0
    total_size = 0
    radar_types = {}

    # Analyze each radar type directory
    for radar_dir in base_dir.iterdir():
        if not radar_dir.is_dir():
            continue

        radar_type = radar_dir.name
        files = list(radar_dir.glob("*.gif"))

        if not files:
            continue

        radar_types[radar_type] = {
            'files': files,
            'count': len(files),
            'total_size': sum(f.stat().st_size for f in files),
            'latest': max(files, key=lambda x: x.stat().st_mtime),
            'oldest': min(files, key=lambda x: x.stat().st_mtime)
        }

        total_files += len(files)
        total_size += radar_types[radar_type]['total_size']

    # Overall summary
    print(f"📁 Total radar files: {total_files}")
    print(f"💾 Total storage used: {format_size(total_size)}")
    print(f"🎯 Radar types collected: {len(radar_types)}")

    print(f"\n📋 Detailed Breakdown:")

    for radar_type, data in radar_types.items():
        print(f"\n🔸 {radar_type.upper()} Radar:")
        print(f"   📊 Files: {data['count']}")
        print(f"   💾 Size: {format_size(data['total_size'])}")
        print(f"   📅 Latest: {format_timestamp(data['latest'])}")
        print(f"   📅 Oldest: {format_timestamp(data['oldest'])}")

        # Show file info
        print(f"   � Latest file: {data['latest'].name}")


def format_size(bytes_size):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def format_timestamp(file_path):
    """Extract and format timestamp from filename or file modification time"""
    try:
        # Try to extract from filename first
        filename = file_path.stem
        parts = filename.split('_')
        if len(parts) >= 3:
            date_part = parts[-2]  # YYYYMMDD
            time_part = parts[-1]  # HHMM
            if len(date_part) == 8 and len(time_part) == 4:
                dt_str = date_part + time_part
                dt = datetime.strptime(dt_str, "%Y%m%d%H%M")
                return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        pass

    # Fall back to file modification time
    mtime = file_path.stat().st_mtime
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")


def show_latest_downloads():
    """Show the most recent downloads for each radar type"""
    base_dir = Path("radar_images")
    if not base_dir.exists():
        print("❌ No radar_images directory found!")
        return

    print("🕐 Latest Downloads:")
    print("-" * 30)

    for radar_dir in sorted(base_dir.iterdir()):
        if not radar_dir.is_dir():
            continue

        files = list(radar_dir.glob("*.gif"))
        if files:
            latest = max(files, key=lambda x: x.stat().st_mtime)
            timestamp = format_timestamp(latest)
            size = format_size(latest.stat().st_size)
            print(f"📡 {radar_dir.name.upper()}: {timestamp} ({size})")


def cleanup_old_files(days_to_keep=7):
    """Remove files older than specified days"""
    base_dir = Path("radar_images")
    if not base_dir.exists():
        print("❌ No radar_images directory found!")
        return

    from datetime import timedelta
    cutoff_time = datetime.now() - timedelta(days=days_to_keep)
    cutoff_timestamp = cutoff_time.timestamp()

    total_removed = 0
    total_size_freed = 0

    print(f"🧹 Cleaning up files older than {days_to_keep} days...")
    print(f"   Cutoff date: {cutoff_time.strftime('%Y-%m-%d %H:%M')}")

    for radar_dir in base_dir.iterdir():
        if not radar_dir.is_dir():
            continue

        files = list(radar_dir.glob("*.gif"))
        old_files = [f for f in files if f.stat().st_mtime < cutoff_timestamp]

        if old_files:
            print(f"\n📂 {radar_dir.name.upper()}:")
            for old_file in old_files:
                size = old_file.stat().st_size
                timestamp = format_timestamp(old_file)
                print(f"   🗑️  Removing: {old_file.name} ({timestamp})")
                total_size_freed += size
                old_file.unlink()
                total_removed += 1

    if total_removed > 0:
        print(f"\n✅ Cleanup completed:")
        print(f"   🗑️  Files removed: {total_removed}")
        print(f"   💾 Space freed: {format_size(total_size_freed)}")
    else:
        print(f"\n✅ No old files found to remove")


def main():
    """Main menu for radar data analysis"""
    while True:
        print("\n" + "=" * 50)
        print("📊 Kerala Radar Data Analyzer")
        print("=" * 50)
        print("\n1. 📋 Full analysis report")
        print("2. 🕐 Show latest downloads")
        print("3. 🧹 Cleanup old files (7+ days)")
        print("4. 🧹 Cleanup old files (30+ days)")
        print("5. 🚪 Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            print()
            analyze_radar_directory()
        elif choice == "2":
            print()
            show_latest_downloads()
        elif choice == "3":
            print()
            cleanup_old_files(7)
        elif choice == "4":
            print()
            cleanup_old_files(30)
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please try again.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
