#!/usr/bin/env python3
"""
Kerala Radar Data Collection System

Professional radar data scraper with multi-type support, automated scheduling,
duplicate detection, and MOSDAC pattern analysis.

Features:
- Multi-type radar downloads (CAZ, PPZ, PPI, ZDR, VP2, 3DS, MAXZ)
- SHA256-based duplicate detection
- Flexible MOSDAC timestamp matching (imported from mosdac_only.py)
- Reference-based pattern generation
- UTC time handling for accuracy
- Option to run with or without MOSDAC data collection
- WMS-based high-resolution Max Z reflectivity (MAXZ)
"""

import requests
from datetime import datetime, UTC
from pathlib import Path
import hashlib
import argparse

# Import MOSDAC functions to avoid code duplication
from mosdac_only import (
    smart_pattern_scan,
    download_mosdac_only
)


def calculate_image_hash(image_data):
    """Calculate SHA256 hash of image data for duplicate detection."""
    return hashlib.sha256(image_data).hexdigest()


def find_duplicate_image(image_data, save_directory):
    """
    Check if an identical image already exists in the directory.

    Args:
        image_data: Binary image data to check
        save_directory: Directory to search for duplicates

    Returns:
        Path to duplicate file if found, None otherwise
    """
    new_hash = calculate_image_hash(image_data)

    # Check all existing image files in the directory (both .gif and .png)
    for existing_file in save_directory.glob("*"):
        if existing_file.suffix.lower() in ['.gif', '.png']:
            try:
                with open(existing_file, "rb") as f:
                    existing_data = f.read()
                    existing_hash = calculate_image_hash(existing_data)

                    if new_hash == existing_hash:
                        return existing_file
            except Exception:
                continue

    return None


def download_radar_type(radar_type, url, timestamp):
    """
    Download a specific radar type and save it with proper naming.

    Args:
        radar_type: Type of radar (caz, ppz, ppi, etc.)
        url: URL to download from
        timestamp: Timestamp for filename

    Returns:
        Success status and filename
    """
    print(f"\n📡 Downloading {radar_type.upper()} radar...")

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Check content type
            content_type = response.headers.get('content-type', '').lower()

            if ('text/html' in content_type or
                    response.content.startswith(b'<!DOCTYPE')):
                print(f"❌ {radar_type}: Got HTML instead of image")
                return False, None

            # Determine file extension based on radar type and content
            if radar_type == 'maxz' or 'image/png' in content_type:
                file_ext = "png"
            else:
                file_ext = "gif"

            # Save to appropriate directory
            radar_dir = radar_dirs[radar_type]
            filename = radar_dir / f"{radar_type}_radar_{timestamp}.{file_ext}"

            # Check for duplicate images
            duplicate_file = find_duplicate_image(response.content, radar_dir)
            if duplicate_file:
                print(f"🔄 {radar_type}: Identical image exists:")
                print(f"   {duplicate_file.name}")
                print("   Skipping duplicate save")
                return True, duplicate_file

            with open(filename, "wb") as f:
                f.write(response.content)

            print(f"✅ {radar_type}: Saved {filename}")
            print(f"   File size: {len(response.content)} bytes")

            # Special note for maxz (WMS) type
            if radar_type == 'maxz':
                print(f"   📊 WMS Max Z Reflectivity (1024x1024 PNG)")

            return True, filename
        else:
            print(f"❌ {radar_type}: HTTP {response.status_code}")
            return False, None

    except Exception as e:
        print(f"❌ {radar_type}: Error - {e}")
        return False, None


def download_all_radar_types(include_mosdac=False):
    """
    Download all radar types for the most recent available timestamp.

    Args:
        include_mosdac: Whether to include MOSDAC data collection
                       (default: False)
    """
    print("🌦️  Kerala Radar Data Collection System")
    print("=" * 50)

    # Setup directories
    global radar_dirs
    radar_dirs = {
        'caz': Path("radar_images/caz"),
        'ppz': Path("radar_images/ppz"),
        'ppi': Path("radar_images/ppi"),
        'zdr': Path("radar_images/zdr"),
        'vp2': Path("radar_images/vp2"),
        '3ds': Path("radar_images/3ds"),
        'maxz': Path("radar_images/maxz")  # New WMS-based Max Z reflectivity
    }

    # Create all directories
    for radar_dir in radar_dirs.values():
        radar_dir.mkdir(parents=True, exist_ok=True)

    # Current timestamp for downloads (only used for local filenames)
    current_time = datetime.now(UTC)
    timestamp_str = current_time.strftime("%Y%m%d_%H%M")

    print(f"🕐 Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"📅 Using timestamp: {timestamp_str} (for local filenames)")
    print("📁 Save directory: radar_images/")
    print()

    # Radar type configurations - Static URLs (no timestamps)
    radar_configs = {
        'caz': "http://117.221.70.132/dwr/radar/images/caz_koc.gif",
        'ppz': "http://117.221.70.132/dwr/radar/images/ppz_koc.gif",
        'ppi': "http://117.221.70.132/dwr/radar/images/ppi_koc.gif",
        'zdr': "http://117.221.70.132/dwr/radar/images/zdr_koc.gif",
        'vp2': "http://117.221.70.132/dwr/radar/images/vp2_koc.gif",
        '3ds': "http://117.221.70.132/dwr/radar/images/3ds_koc.gif",
        'maxz': ("http://117.221.70.132/geoserver/dwr_kochi/wms?"
                 "service=WMS&request=GetMap&layers=dwr_kochi:maxz_image"
                 "&styles=&format=image/png&transparent=true&version=1.1.1"
                 "&width=1024&height=1024&srs=EPSG:4326&bbox=74.0,8.0,78.0,12.0")
    }

    # Download each radar type
    results = {}
    for radar_type, url in radar_configs.items():
        success, filename = download_radar_type(radar_type, url, timestamp_str)
        results[radar_type] = {
            'success': success,
            'filename': filename,
            'url': url
        }

    # Show detailed results
    print("\n📋 Detailed Results:")
    for radar_type, result in results.items():
        status = "✅" if result['success'] else "❌"
        print(f"   {status} {radar_type.upper()}: {result['url']}")
        if result['success']:
            print(f"      📁 {result['filename']}")

    print("\n🏁 Multi-radar download session completed!")

    # MOSDAC data collection (optional)
    if include_mosdac:
        print("\n" + "=" * 50)
        print("🔬 Running MOSDAC Data Collection...")
        print("📅 Using adaptive timestamp matching with 2-hour window...")
        print("🕐 Smart pattern generation with timing variants")
        print("📊 Checking entire last two hours of data")

        current_time = datetime.now(UTC)  # Use UTC time explicitly

        # Check entire last two hours: current hour + previous 2 hours
        # This ensures we get complete coverage for the last 120 minutes
        current_hour = current_time.hour
        previous_hour = current_hour - 1 if current_hour > 0 else 23
        two_hours_ago = (current_hour - 2 if current_hour >= 2
                         else (24 + current_hour - 2))
        target_hours = [two_hours_ago, previous_hour, current_hour]

        print(f"🕐 Current UTC time: {current_time.strftime('%H:%M')} UTC")
        print(f"🎯 Target: {two_hours_ago:02d}:xx, {previous_hour:02d}:xx and "
              f"{current_hour:02d}:xx UTC (last two hours coverage)")

        # Use smart pattern scanning with flexibility for all hours
        quick_scan_results = smart_pattern_scan(current_time, target_hours,
                                                use_flexibility=True)

        if quick_scan_results:
            print("\n📋 Available MOSDAC times found:")
            exact_matches = 0
            flexible_matches = 0

            for result in quick_scan_results:
                timestamp = result['timestamp']
                time_str = result['time_str']
                is_exact = result.get('is_exact_match', True)

                if is_exact:
                    print(f"   ✅ {time_str} (exact)")
                    exact_matches += 1
                else:
                    print(f"   🔄 {time_str} (flexible)")
                    flexible_matches += 1

            print(f"\n📊 Found {len(quick_scan_results)} available times:")
            print(f"   🎯 Exact matches: {exact_matches}")
            print(f"   🔄 Flexible matches: {flexible_matches}")

            # Download all found MOSDAC images
            download_count = 0
            save_dir = Path("radar_images/kochi")
            save_dir.mkdir(parents=True, exist_ok=True)

            print(f"\n📥 Downloading {len(quick_scan_results)} MOSDAC images...")

            for i, result in enumerate(quick_scan_results, 1):
                print(f"[{i}/{len(quick_scan_results)}] {result['time_str']}...",
                      end=" ", flush=True)

                ts = result['timestamp']
                filename = save_dir / f"kochi_radar_mosdac_{ts}.gif"

                try:
                    r = result['response']
                    if r.status_code == 200:
                        content_type = (
                            r.headers.get('content-type', '').lower()
                        )

                        if ('text/html' in content_type or
                                r.content.startswith(b'<!DOCTYPE')):
                            print("❌ HTML response")
                            continue

                        # Check for duplicates
                        duplicate_file = find_duplicate_image(r.content,
                                                              save_dir)
                        if duplicate_file:
                            print(f"🔄 Duplicate ({duplicate_file.name})")
                            continue

                        # Save image
                        with open(filename, "wb") as f:
                            f.write(r.content)

                        size_kb = len(r.content) / 1024
                        print(f"✅ Saved ({size_kb:.1f} KB)")

                        if not result.get('is_exact_match', True):
                            orig_time = result.get('original_timestamp', ts)
                            if orig_time != ts:
                                orig_time_str = (f"{orig_time[:2]}:"
                                                 f"{orig_time[2:4]}:"
                                                 f"{orig_time[4:6]}")
                                print(f"   📍 Flexible match "
                                      f"(target: {orig_time_str})")

                        download_count += 1
                    else:
                        print(f"❌ HTTP {r.status_code}")
                except Exception as e:
                    print(f"❌ Error: {e}")

            print(f"\n🎉 Success: {download_count}/"
                  f"{len(quick_scan_results)} MOSDAC images")
            if flexible_matches > 0:
                print(f"🔧 Flexibility helped find {flexible_matches} "
                      "additional images!")

        else:
            print("\n❌ No MOSDAC radar data found in target time range")

        print(f"\n📁 Check the 'radar_images/kochi/' folder for "
              "MOSDAC downloads")
    else:
        print("\n📊 MOSDAC data collection disabled "
              "(use --mosdac flag to enable)")


def main():
    """Main function with command-line argument support."""
    parser = argparse.ArgumentParser(
        description="Kerala Radar Data Collection System"
    )
    parser.add_argument(
        '--mosdac',
        action='store_true',
        help='Include MOSDAC data collection (default: disabled)'
    )
    parser.add_argument(
        '--no-mosdac',
        action='store_true',
        help='Skip MOSDAC data collection (legacy option, now default)'
    )
    parser.add_argument(
        '--mosdac-only',
        action='store_true',
        help='Only run MOSDAC data collection (skip IMD radar types)'
    )

    args = parser.parse_args()

    if args.mosdac_only:
        # Run only MOSDAC collection
        print("🌦️  MOSDAC-Only Data Collection")
        print("=" * 50)
        download_mosdac_only()
    else:
        # Run multi-radar collection with optional MOSDAC
        # MOSDAC is now disabled by default, enabled with --mosdac flag
        include_mosdac_data = args.mosdac and not args.no_mosdac
        download_all_radar_types(include_mosdac=include_mosdac_data)


if __name__ == "__main__":
    main()
