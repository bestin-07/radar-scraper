#!/usr/bin/env python3
"""
Kerala Radar Data Collection System

Professional radar data scraper with multi-type support, automated scheduling,
duplicate detection, and MOSDAC pattern analysis.

Features:
- Multi-type radar downloads (CAZ, PPZ, PPI, ZDR, VP2, 3DS)
- SHA256-based duplicate detection
- Flexible MOSDAC timestamp matching
- Reference-based pattern generation
- UTC time handling for accuracy
"""

import requests
from datetime import datetime, UTC
from pathlib import Path
import hashlib
import json


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

    # Check all existing .gif files in the directory
    for existing_file in save_directory.glob("*.gif"):
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

            # Save to appropriate directory
            radar_dir = radar_dirs[radar_type]
            filename = radar_dir / f"{radar_type}_radar_{timestamp}.gif"

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

            return True, filename
        else:
            print(f"❌ {radar_type}: HTTP {response.status_code}")
            return False, None

    except Exception as e:
        print(f"❌ {radar_type}: Error - {e}")
        return False, None


def download_all_radar_types():
    """
    Download all radar types and organize them properly.

    Returns:
        Dictionary with download results
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    print(f"🚀 Starting radar download session at {timestamp}")

    results = {}
    success_count = 0

    for radar_type, url in RADAR_URLS.items():
        success, filename = download_radar_type(radar_type, url, timestamp)
        results[radar_type] = {
            'success': success,
            'filename': filename,
            'url': url
        }
        if success:
            success_count += 1

    print("\n📊 Download Summary:")
    print(f"   ✅ Successful: {success_count}/{len(RADAR_URLS)}")
    print(f"   📁 Saved to: {base_save_dir}")

    if success_count > 0:
        print("\n📁 Directory structure:")
        for radar_type in RADAR_URLS.keys():
            if results[radar_type]['success']:
                print(f"   📂 {radar_type}/ - "
                      f"{radar_type.upper()} radar images")

    return results


# New radar URLs - hourly updates
RADAR_URLS = {
    'caz': 'http://117.221.70.132/dwr/radar/images/caz_koc.gif',
    'ppz': 'http://117.221.70.132/dwr/radar/images/ppz_koc.gif',
    'ppi': 'http://117.221.70.132/dwr/radar/images/ppi_koc.gif',
    'zdr': 'http://117.221.70.132/dwr/radar/images/zdr_koc.gif',
    'vp2': 'http://117.221.70.132/dwr/radar/images/vp2_koc.gif',
    '3ds': 'http://117.221.70.132/dwr/radar/images/3ds_koc.gif'
}

# Save directory structure
base_save_dir = Path("radar_images")
base_save_dir.mkdir(parents=True, exist_ok=True)

# Create subdirectories for each radar type
radar_dirs = {}
for radar_type in RADAR_URLS.keys():
    radar_dir = base_save_dir / radar_type
    radar_dir.mkdir(parents=True, exist_ok=True)
    radar_dirs[radar_type] = radar_dir

# MOSDAC data directory
save_dir = Path("radar_images/kochi")
save_dir.mkdir(parents=True, exist_ok=True)


def load_known_timestamps():
    """Load known valid timestamps from persistent storage."""
    known_file = Path("known_timestamps.json")
    if known_file.exists():
        try:
            with open(known_file, "r") as f:
                data = json.load(f)
                return (data.get("timestamps", []),
                        data.get("last_reference", "152541"))
        except Exception:
            pass
    
    # Default known timestamps from previous discoveries
    default_timestamps = [
        "151023", "151300", "152541"  # Known valid data points
    ]
    return default_timestamps, "152541"


def save_known_timestamps(timestamps, last_reference):
    """Save known valid timestamps to persistent storage."""
    try:
        known_file = Path("known_timestamps.json")
        data = {
            "timestamps": sorted(list(set(timestamps))),
            "last_reference": last_reference,
            "last_updated": datetime.now(UTC).isoformat()
        }
        with open(known_file, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"⚠️  Warning: Could not save timestamps: {e}")


def calculate_intervals_from_known(known_timestamps):
    """Calculate actual intervals from known valid timestamps."""
    if len(known_timestamps) < 2:
        # Default intervals if not enough data
        return {
            'intervals': [158, 761],
            'short_variants': [158, 157, 159],
            'long_variants': [761, 744, 778]
        }
    
    # Convert timestamps to seconds
    timestamps_sec = []
    for ts in sorted(known_timestamps):
        h, m, s = int(ts[:2]), int(ts[2:4]), int(ts[4:6])
        total_sec = h * 3600 + m * 60 + s
        timestamps_sec.append(total_sec)
    
    # Calculate intervals between consecutive timestamps
    intervals = []
    for i in range(1, len(timestamps_sec)):
        interval = timestamps_sec[i] - timestamps_sec[i-1]
        if interval > 0:  # Only positive intervals
            intervals.append(interval)
    
    if not intervals:
        # Fallback to defaults
        return {
            'intervals': [158, 761],
            'short_variants': [158, 157, 159],
            'long_variants': [761, 744, 778]
        }
    
    # Categorize intervals
    short_intervals = [i for i in intervals if i < 400]  # < ~6.5 minutes
    long_intervals = [i for i in intervals if i >= 400]  # >= ~6.5 minutes
    
    # Get most common intervals with variants
    def get_variants(interval_list, base_interval):
        variants = []
        for interval in interval_list:
            if abs(interval - base_interval) <= 20:  # Within 20 seconds
                variants.append(interval)
        return sorted(list(set(variants))) if variants else [base_interval]
    
    # Use most common intervals as base
    short_base = (max(set(short_intervals), key=short_intervals.count)
                  if short_intervals else 158)
    long_base = (max(set(long_intervals), key=long_intervals.count)
                 if long_intervals else 761)
    
    return {
        'intervals': intervals,
        'short_base': short_base,
        'long_base': long_base,
        'short_variants': get_variants(short_intervals, short_base),
        'long_variants': get_variants(long_intervals, long_base)
    }


# Known radar data timestamps from actual observation (UTC)
known_timestamps = [
    "064309",  # 06:43:09
    "065533",  # 06:55:33
    "065811",  # 06:58:11
    "071052",  # 07:10:52
    "071330",  # 07:13:30
    "072611",  # 07:26:11
    "072849",  # 07:28:49
    "074130",  # 07:41:30
    "132322",  # 13:23:22 (correct timestamp before 13:26:00)
    "132600",  # 13:26:00
    "133824",  # 13:38:24
    "134102",  # 13:41:02
    "135343",  # 13:53:43
    "135621",  # 13:56:21
    "140902",  # 14:09:02
    "141139"   # 14:11:39 (latest available)
]


def generate_forward_timestamps_from_latest(current_time,
                                            include_variants=True,
                                            known_timestamps=None,
                                            reference_timestamp=None):
    """
    Generate timestamps going forward/backward from the last known
    valid timestamp. Uses adaptive pattern matching based on known
    valid data points.

    Args:
        current_time: Current datetime object
        include_variants: If True, include timing variants for better coverage
        known_timestamps: List of known valid timestamps for pattern analysis
        reference_timestamp: Override reference timestamp (latest known valid)

    Returns:
        List of timestamps in HHMMSS format for recent/upcoming data
    """
    # Load known timestamps and reference if not provided
    if known_timestamps is None or reference_timestamp is None:
        loaded_timestamps, loaded_reference = load_known_timestamps()
        if known_timestamps is None:
            known_timestamps = loaded_timestamps
        if reference_timestamp is None:
            reference_timestamp = loaded_reference
    
    # Parse reference timestamp
    ref_h = int(reference_timestamp[:2])
    ref_m = int(reference_timestamp[2:4])
    ref_s = int(reference_timestamp[4:6])
    ref_total_sec = ref_h * 3600 + ref_m * 60 + ref_s

    # Current time in seconds
    current_total_sec = (
        current_time.hour * 3600 +
        current_time.minute * 60 +
        current_time.second
    )

    print(f"🔄 Using reference: {ref_h:02d}:{ref_m:02d}:{ref_s:02d} "
          f"(auto-updated from latest valid data)")
    print(f"🕐 Current time: {current_time.hour:02d}:{current_time.minute:02d}:"
          f"{current_time.second:02d}")
    print(f"📊 Known valid timestamps: {len(known_timestamps)}")
    
    # Calculate adaptive intervals from known data
    pattern_info = calculate_intervals_from_known(known_timestamps)
    short_base = pattern_info.get('short_base', 158)
    long_base = pattern_info.get('long_base', 761)
    print(f"🎯 Adaptive intervals: {short_base}s, {long_base}s")

    # Determine direction based on one-hour window
    one_hour_ago = current_total_sec - 3600
    one_hour_ahead = current_total_sec + 3600
    
    # Decide if we need forward, backward, or both
    if ref_total_sec < one_hour_ago:
        # Reference is too old, generate forward
        print("⏩ Generating forward from reference (reference is old)")
        direction = "forward"
    elif ref_total_sec > one_hour_ahead:
        # Reference is too new, generate backward
        print("⏪ Generating backward from reference (reference is ahead)")
        direction = "backward"
    else:
        # Reference is within window, generate both directions
        print("🔄 Generating both directions from reference (within window)")
        direction = "both"

    timestamps = [reference_timestamp]  # Start with the reference
    
    # Generate timestamps based on direction
    if direction in ["forward", "both"]:
        # Generate forward
        current_check_sec = ref_total_sec
        use_short = True
        iteration = 0
        
        while current_check_sec <= one_hour_ahead and iteration < 50:
            # Calculate next interval
            if use_short:
                if include_variants and pattern_info.get('short_variants'):
                    short_vars = pattern_info['short_variants']
                    variant_idx = iteration % len(short_vars)
                    interval = short_vars[variant_idx]
                else:
                    interval = pattern_info.get('short_base', 158)
            else:
                if include_variants and pattern_info.get('long_variants'):
                    long_vars = pattern_info['long_variants']
                    variant_idx = iteration % len(long_vars)
                    interval = long_vars[variant_idx]
                else:
                    interval = pattern_info.get('long_base', 761)

            current_check_sec += interval
            use_short = not use_short
            iteration += 1

            if current_check_sec >= 24 * 3600:
                break

            h = current_check_sec // 3600
            m = (current_check_sec % 3600) // 60
            s = current_check_sec % 60
            timestamp = f"{h:02d}{m:02d}{s:02d}"
            timestamps.append(timestamp)

    if direction in ["backward", "both"]:
        # Generate backward
        current_check_sec = ref_total_sec
        use_short = True
        iteration = 0
        
        while current_check_sec >= one_hour_ago and iteration < 50:
            # Calculate previous interval
            if use_short:
                if include_variants and pattern_info.get('short_variants'):
                    short_vars = pattern_info['short_variants']
                    variant_idx = iteration % len(short_vars)
                    interval = short_vars[variant_idx]
                else:
                    interval = pattern_info.get('short_base', 158)
            else:
                if include_variants and pattern_info.get('long_variants'):
                    long_vars = pattern_info['long_variants']
                    variant_idx = iteration % len(long_vars)
                    interval = long_vars[variant_idx]
                else:
                    interval = pattern_info.get('long_base', 761)

            current_check_sec -= interval
            use_short = not use_short
            iteration += 1

            if current_check_sec < 0:
                break

            h = current_check_sec // 3600
            m = (current_check_sec % 3600) // 60
            s = current_check_sec % 60
            timestamp = f"{h:02d}{m:02d}{s:02d}"
            timestamps.append(timestamp)

    # Filter for one-hour window around current time
    filtered_timestamps = []
    for ts in timestamps:
        ts_h = int(ts[:2])
        ts_m = int(ts[2:4])
        ts_s = int(ts[4:6])
        ts_total_sec = ts_h * 3600 + ts_m * 60 + ts_s

        # Include if it's within one hour window
        if one_hour_ago <= ts_total_sec <= one_hour_ahead:
            filtered_timestamps.append(ts)

    # Remove duplicates and sort
    unique_timestamps = sorted(list(set(filtered_timestamps)))

    print(f"📅 Generated {len(unique_timestamps)} candidate timestamps")
    if unique_timestamps:
        start_time = f"{unique_timestamps[0][:2]}:{unique_timestamps[0][2:4]}"
        end_time = f"{unique_timestamps[-1][:2]}:{unique_timestamps[-1][2:4]}"
        print(f"🔍 Range: {start_time} to {end_time}")

    return unique_timestamps


def check_timestamp_with_flexibility(base_timestamp, tolerance_seconds=20):
    """
    Check a timestamp and nearby variants for data availability.

    Args:
        base_timestamp: Base timestamp to check (HHMMSS format)
        tolerance_seconds: How many seconds +/- to check around base

    Returns:
        Tuple of (success, actual_timestamp, response) if found,
        else (False, None, None)
    """
    h = int(base_timestamp[:2])
    m = int(base_timestamp[2:4])
    s = int(base_timestamp[4:6])
    base_total_sec = h * 3600 + m * 60 + s

    # Generate candidate timestamps within tolerance
    candidates = []
    for offset in range(-tolerance_seconds, tolerance_seconds + 1, 1):
        new_total_sec = base_total_sec + offset

        # Skip if goes to different day
        if new_total_sec < 0 or new_total_sec >= 24 * 3600:
            continue

        new_h = new_total_sec // 3600
        new_m = (new_total_sec % 3600) // 60
        new_s = new_total_sec % 60
        candidate_timestamp = f"{new_h:02d}{new_m:02d}{new_s:02d}"
        candidates.append(candidate_timestamp)

    # Check candidates, starting with exact match
    base_url = "https://mosdac.gov.in/look/DWR/RCTLS/2025/28JUL/"

    # Try exact match first
    exact_url = base_url + f"RCTLS_28JUL2025_{base_timestamp}_L2B_STD_MAXZ.gif"
    try:
        r = requests.get(exact_url, timeout=5)
        if r.status_code == 200:
            return True, base_timestamp, r
    except Exception:
        pass

    # Try nearby timestamps if exact fails
    for candidate in candidates:
        if candidate == base_timestamp:  # Skip exact match (already tried)
            continue

        candidate_url = (base_url +
                         f"RCTLS_28JUL2025_{candidate}_L2B_STD_MAXZ.gif")
        try:
            r = requests.get(candidate_url, timeout=5)
            if r.status_code == 200:
                return True, candidate, r
        except Exception:
            continue

    return False, None, None


def smart_pattern_scan(current_time, target_hours, use_flexibility=True):
    """
    Intelligent scanning using reference-based generation with flexibility.

    Args:
        current_time: Current datetime object for generating recent timestamps
        target_hours: List of hours to scan
        use_flexibility: Whether to use flexible timestamp matching

    Returns:
        List of successful scan results
    """
    print("🔍 Smart Pattern Scan with Flexibility...")

    # Generate timestamps for the last hour based on current time
    all_timestamps = generate_forward_timestamps_from_latest(
        current_time, include_variants=True)

    # Filter for target hours
    target_timestamps = []
    for hour in target_hours:
        hour_timestamps = [ts for ts in all_timestamps if int(ts[:2]) == hour]
        target_timestamps.extend(hour_timestamps)
        print(f"   📅 Hour {hour:02d}: {len(hour_timestamps)} candidate "
              f"timestamps")

    print(f"🎯 Scanning {len(target_timestamps)} reference-based timestamps...")

    scan_results = []
    found_count = 0
    consecutive_not_found = 0  # Track consecutive failures
    max_consecutive_failures = 5  # Early exit threshold

    for i, timestamp in enumerate(target_timestamps, 1):
        time_str = f"{timestamp[:2]}:{timestamp[2:4]}:{timestamp[4:6]}"
        print(f"  [{i:2d}/{len(target_timestamps)}] {time_str}...", end=" ")

        if use_flexibility:
            # Use flexible matching with ±20s tolerance
            success, actual_timestamp, response = (
                check_timestamp_with_flexibility(
                    timestamp, tolerance_seconds=20))

            if success:
                consecutive_not_found = 0  # Reset counter on success
                
                if actual_timestamp == timestamp:
                    print("✅ Available (exact)")
                else:
                    actual_time_str = (f"{actual_timestamp[:2]}:"
                                       f"{actual_timestamp[2:4]}:"
                                       f"{actual_timestamp[4:6]}")
                    print(f"✅ Available ({actual_time_str})")

                scan_results.append({
                    'timestamp': actual_timestamp,
                    'time_str': (actual_time_str
                                 if actual_timestamp != timestamp
                                 else time_str),
                    'response': response,
                    'original_timestamp': timestamp,
                    'is_exact_match': actual_timestamp == timestamp
                })
                found_count += 1
            else:
                consecutive_not_found += 1
                print("❌ Not found")
                
                # Early exit if too many consecutive failures
                if consecutive_not_found >= max_consecutive_failures:
                    remaining = len(target_timestamps) - i
                    print(f"\n⚠️  Early exit: {consecutive_not_found} "
                          f"consecutive failures detected")
                    print(f"   Skipping {remaining} remaining timestamps")
                    break
        else:
            # Use exact matching only
            base_url = "https://mosdac.gov.in/look/DWR/RCTLS/2025/28JUL/"
            url = base_url + f"RCTLS_28JUL2025_{timestamp}_L2B_STD_MAXZ.gif"

            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    consecutive_not_found = 0  # Reset counter on success
                    print("✅ Available")
                    scan_results.append({
                        'timestamp': timestamp,
                        'time_str': time_str,
                        'response': r,
                        'original_timestamp': timestamp,
                        'is_exact_match': True
                    })
                    found_count += 1
                else:
                    consecutive_not_found += 1
                    print(f"❌ {r.status_code}")
                    
                    # Early exit check for exact matching too
                    if consecutive_not_found >= max_consecutive_failures:
                        remaining = len(target_timestamps) - i
                        print(f"\n⚠️  Early exit: {consecutive_not_found} "
                              f"consecutive failures detected")
                        print(f"   Skipping {remaining} remaining timestamps")
                        break
            except Exception:
                consecutive_not_found += 1
                print("❌ Error")
                
                # Early exit check for exceptions too
                if consecutive_not_found >= max_consecutive_failures:
                    remaining = len(target_timestamps) - i
                    print(f"\n⚠️  Early exit: {consecutive_not_found} "
                          f"consecutive failures detected")
                    print(f"   Skipping {remaining} remaining timestamps")
                    break

    if consecutive_not_found >= max_consecutive_failures:
        print(f"\n📊 Smart Scan Results (Early Exit): {found_count}/"
              f"{len(target_timestamps)} images found")
        print(f"⚠️  Stopped after {consecutive_not_found} consecutive "
              "failures")
    else:
        print(f"\n📊 Smart Scan Results: {found_count}/"
              f"{len(target_timestamps)} images found")
    return scan_results


# Main execution
if __name__ == "__main__":
    print("🌦️  Kerala Radar Scraper - Multi-Type Download")
    print("=" * 50)

    # Download all radar types
    results = download_all_radar_types()

    # Show detailed results
    print("\n📋 Detailed Results:")
    for radar_type, result in results.items():
        status = "✅" if result['success'] else "❌"
        print(f"   {status} {radar_type.upper()}: {result['url']}")
        if result['success']:
            print(f"      📁 {result['filename']}")

    print("\n🏁 Download session completed!")

    # MOSDAC hourly analysis - collect available data using one hour gap
    run_mosdac_analysis = True  # Run MOSDAC analysis hourly

    if run_mosdac_analysis:
        print("\n" + "=" * 50)
        print("🔬 Running MOSDAC Hourly Analysis...")
        print("📅 Using 13:23:22 reference with flexible ±20s matching...")
        print("🕐 Smart pattern generation with timing variants")
        print("📊 Checking entire last hour of data")

        current_time = datetime.now(UTC)  # Use UTC time explicitly

        # Check entire last hour: both previous hour and current hour
        # This ensures we get complete coverage for the last 60 minutes
        previous_hour = current_time.hour - 1 if current_time.hour > 0 else 23
        target_hours = [previous_hour, current_time.hour]  # Check both hours

        print(f"🕐 Current UTC time: {current_time.strftime('%H:%M')} UTC")
        print(f"🎯 Target: {previous_hour:02d}:xx and "
              f"{current_time.hour:02d}:xx UTC (last hour coverage)")

        # Use smart pattern scanning with flexibility for both hours
        quick_scan_results = smart_pattern_scan(current_time, target_hours,
                                                use_flexibility=True)

        if quick_scan_results:
            print("\n📋 Available times found:")
            exact_matches = 0
            flexible_matches = 0

            for result in quick_scan_results:
                if result.get('is_exact_match', True):
                    match_type = "🎯 exact"
                    exact_matches += 1
                else:
                    match_type = "🔄 flexible"
                    flexible_matches += 1
                print(f"  🟢 {result['time_str']} ({match_type})")

            print(f"\n📊 Match Summary: {exact_matches} exact, "
                  f"{flexible_matches} flexible")
            print(f"📥 Downloading all {len(quick_scan_results)} images...")

            download_count = 0

            for i, result in enumerate(quick_scan_results, 1):
                print(f"\n[{i}/{len(quick_scan_results)}] "
                      f"{result['time_str']}...")

                # Create filename with actual timestamp found
                ts = result['timestamp']
                filename = save_dir / f"kochi_radar_mosdac_{ts}.gif"

                try:
                    r = result['response']
                    if r.status_code == 200:
                        content_type = (r.headers.get('content-type', '')
                                        .lower())

                        if ('text/html' in content_type or
                            r.content.startswith(b'<!DOCTYPE')):
                            print("❌ Got HTML instead of image")
                            continue
                        else:
                            # Check for duplicate images before saving
                            duplicate_file = find_duplicate_image(
                                r.content, save_dir)
                            if duplicate_file:
                                print(f"🔄 Duplicate exists: "
                                      f"{duplicate_file.name}")
                                print("   Skipping duplicate save")
                                continue

                            # Check if file exists and show overwrite info
                            if filename.exists():
                                old_size = filename.stat().st_size
                                print(f"   🔄 Overwriting ({old_size} bytes)")

                            # Save new unique image
                            with open(filename, "wb") as f:
                                f.write(r.content)
                            print(f"✅ Saved: {filename}")
                            print(f"   Size: {len(r.content)} bytes")

                            # Show match type for clarity
                            if not result.get('is_exact_match', True):
                                orig_time = result.get(
                                    'original_timestamp', '')
                                orig_time_str = f"{orig_time[:2]}:{orig_time[2:4]}:{orig_time[4:6]}"
                                print(f"   📍 Flexible match (target: {orig_time_str})")

                            download_count += 1
                    else:
                        print(f"❌ HTTP {r.status_code}")
                except Exception as e:
                    print(f"❌ Error saving: {e}")

            print(f"\n🎉 Success: {download_count}/{len(quick_scan_results)} MOSDAC images")
            if flexible_matches > 0:
                print(f"🔧 Flexibility helped find {flexible_matches} additional images!")
        else:
            print("❌ No MOSDAC radar data found in target hour")

        print("\n📁 Check the 'radar_images/kochi/' folder for MOSDAC downloads")
        print("📁 Check the individual radar type folders for hourly downloads")
