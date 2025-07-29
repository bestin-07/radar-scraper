#!/usr/bin/env python3
"""
Kerala Radar Data Collection System

Professional radar data scraper with multi-type support, automated scheduling,
and duplicate detection.

Features:
- Multi-type radar downloads (CAZ, PPZ, PPI, ZDR, VP2, 3DS, MAXZ)
- SHA256-based duplicate detection
- Reference-based pattern generation
- UTC time handling for accuracy
- WMS-based high-resolution Max Z reflectivity (MAXZ)
"""

import requests
from datetime import datetime, UTC
from pathlib import Path
import hashlib


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
                print("   📊 WMS Max Z Reflectivity (1024x1024 PNG)")

            return True, filename
        else:
            print(f"❌ {radar_type}: HTTP {response.status_code}")
            return False, None

    except Exception as e:
        print(f"❌ {radar_type}: Error - {e}")
        return False, None


def download_all_radar_types():
    """
    Download all radar types for the most recent available timestamp.
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
                 "&width=1024&height=1024&srs=EPSG:4326"
                 "&bbox=74.0,8.0,78.0,12.0")
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


def main():
    """Main function for Kerala Radar Data Collection System."""
    # Run multi-radar collection
    download_all_radar_types()


if __name__ == "__main__":
    main()
