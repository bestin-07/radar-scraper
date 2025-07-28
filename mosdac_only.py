#!/usr/bin/env python3
"""
MOSDAC-Only Radar Data Downloader

Specialized script for downloading only MOSDAC radar data with smart
pattern matching. Optimized for speed and focused on Kochi radar station data.
"""

import requests
from datetime import datetime, UTC
from pathlib import Path
import hashlib


def calculate_image_hash(image_data):
    """Calculate SHA256 hash of image data for duplicate detection."""
    return hashlib.sha256(image_data).hexdigest()


def find_duplicate_image(image_data, save_directory):
    """Check if an identical image already exists in the directory."""
    new_hash = calculate_image_hash(image_data)

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


def generate_forward_timestamps_from_latest(current_time,
                                            include_variants=True):
    """
    Generate timestamps going forward from the last known valid timestamp.
    Uses the 158s/761s pattern to predict when new data should be available.

    Args:
        current_time: Current datetime object
        include_variants: If True, include timing variants for better coverage

    Returns:
        List of timestamps in HHMMSS format for recent/upcoming data
    """
    # Last known valid timestamp: 15:25:41 (latest confirmed data)
    ref_timestamp = "152541"
    ref_h, ref_m, ref_s = 15, 25, 41
    ref_total_sec = ref_h * 3600 + ref_m * 60 + ref_s

    # Current time in seconds
    current_total_sec = (
        current_time.hour * 3600 +
        current_time.minute * 60 +
        current_time.second
    )

    print(f"🔄 Using reference: {ref_h:02d}:{ref_m:02d}:{ref_s:02d} "
          f"(last known valid data)")
    print(f"🕐 Current time: {current_time.hour:02d}:{current_time.minute:02d}:"
          f"{current_time.second:02d}")
    print("🎯 Generating timestamps forward from reference to current time")

    # Fine-tuned intervals based on real data analysis
    intervals = {
        'short_base': 158,      # ~2:38 minutes
        'long_base': 761,       # ~12:41 minutes
        'short_variants': [158, 157, 159],
        'long_variants': [761, 744, 778]
    }

    timestamps = [ref_timestamp]  # Start with the reference

    # Generate forward from reference point
    current_check_sec = ref_total_sec
    use_short = True  # Start with short interval after reference
    iteration = 0

    while current_check_sec <= current_total_sec + 3600 and iteration < 100:
        # Calculate next interval to add
        if use_short:
            if include_variants and iteration % 3 == 2:
                variant_idx = iteration % len(intervals['short_variants'])
                interval = intervals['short_variants'][variant_idx]
            else:
                interval = intervals['short_base']
        else:
            if include_variants and iteration % 4 == 1:
                variant_idx = iteration % len(intervals['long_variants'])
                interval = intervals['long_variants'][variant_idx]
            else:
                interval = intervals['long_base']

        # Move forward in time
        current_check_sec += interval
        use_short = not use_short
        iteration += 1

        # Skip if time goes out of bounds
        if current_check_sec >= 24 * 3600:
            break

        # Convert to timestamp
        h = current_check_sec // 3600
        m = (current_check_sec % 3600) // 60
        s = current_check_sec % 60
        timestamp = f"{h:02d}{m:02d}{s:02d}"
        timestamps.append(timestamp)

        # Stop if we've gone too far into the future
        if current_check_sec > current_total_sec + 3600:
            break

    # Filter for timestamps that are >= current time - 2 hours
    two_hours_ago = current_total_sec - 7200
    recent_timestamps = []

    for ts in timestamps:
        ts_h = int(ts[:2])
        ts_m = int(ts[2:4])
        ts_s = int(ts[4:6])
        ts_total_sec = ts_h * 3600 + ts_m * 60 + ts_s

        # Include if it's within the last 2 hours or future
        if ts_total_sec >= two_hours_ago:
            recent_timestamps.append(ts)

    # Remove duplicates and sort
    unique_timestamps = sorted(list(set(recent_timestamps)))

    print(f"📅 Generated {len(unique_timestamps)} candidate timestamps")
    print(f"🔍 Range: {unique_timestamps[0][:2]}:{unique_timestamps[0][2:4]} "
          f"to {unique_timestamps[-1][:2]}:{unique_timestamps[-1][2:4]}")

    return unique_timestamps


def check_timestamp_with_flexibility(base_timestamp, tolerance_seconds=20):
    """Check timestamp with flexible matching."""
    h = int(base_timestamp[:2])
    m = int(base_timestamp[2:4])
    s = int(base_timestamp[4:6])
    base_total_sec = h * 3600 + m * 60 + s

    candidates = []
    for offset in range(-tolerance_seconds, tolerance_seconds + 1, 1):
        new_total_sec = base_total_sec + offset
        if new_total_sec < 0 or new_total_sec >= 24 * 3600:
            continue

        new_h = new_total_sec // 3600
        new_m = (new_total_sec % 3600) // 60
        new_s = new_total_sec % 60
        candidate_timestamp = f"{new_h:02d}{new_m:02d}{new_s:02d}"
        candidates.append(candidate_timestamp)

    base_url = "https://mosdac.gov.in/look/DWR/RCTLS/2025/28JUL/"

    # Try exact match first
    exact_url = base_url + f"RCTLS_28JUL2025_{base_timestamp}_L2B_STD_MAXZ.gif"
    try:
        r = requests.get(exact_url, timeout=5)
        if r.status_code == 200:
            return True, base_timestamp, r
    except Exception:
        pass

    # Try nearby timestamps
    for candidate in candidates:
        if candidate == base_timestamp:
            continue

        candidate_url = (
            base_url +
            f"RCTLS_28JUL2025_{candidate}_L2B_STD_MAXZ.gif"
        )
        try:
            r = requests.get(candidate_url, timeout=5)
            if r.status_code == 200:
                return True, candidate, r
        except Exception:
            continue

    return False, None, None


def download_mosdac_only():
    """Download only MOSDAC data with enhanced user feedback."""
    print("🌦️  MOSDAC Radar Data Downloader")
    print("=" * 50)

    # Setup save directory
    save_dir = Path("radar_images/kochi")
    save_dir.mkdir(parents=True, exist_ok=True)

    current_time = datetime.now(UTC)
    previous_hour = current_time.hour - 1 if current_time.hour > 0 else 23
    target_hours = [previous_hour, current_time.hour]

    print(f"🕐 Current UTC time: {current_time.strftime('%H:%M')} UTC")
    print(f"🎯 Target hours: {previous_hour:02d}:xx and "
          f"{current_time.hour:02d}:xx UTC")
    print(f"📁 Save directory: {save_dir}")
    print()

    # Generate timestamps
    print("🔍 Generating smart timestamps...")
    all_timestamps = generate_forward_timestamps_from_latest(
        current_time, include_variants=True)

    # Filter for target hours
    target_timestamps = []
    for hour in target_hours:
        hour_timestamps = [ts for ts in all_timestamps if int(ts[:2]) == hour]
        target_timestamps.extend(hour_timestamps)
        print(f"   📅 Hour {hour:02d}: {len(hour_timestamps)} candidates")

    print(f"🎯 Scanning {len(target_timestamps)} timestamps...")
    print()

    scan_results = []
    found_count = 0

    for i, timestamp in enumerate(target_timestamps, 1):
        time_str = f"{timestamp[:2]}:{timestamp[2:4]}:{timestamp[4:6]}"
        print(f"  [{i:2d}/{len(target_timestamps)}] {time_str}...",
              end=" ", flush=True)

        success, actual_timestamp, response = (
            check_timestamp_with_flexibility(timestamp, tolerance_seconds=20))

        if success:
            if actual_timestamp == timestamp:
                print("✅ Available (exact)")
            else:
                actual_time_str = (
                    f"{actual_timestamp[:2]}:"
                    f"{actual_timestamp[2:4]}:"
                    f"{actual_timestamp[4:6]}"
                )
                print(f"✅ Available ({actual_time_str})")

            scan_results.append({
                'timestamp': actual_timestamp,
                'time_str': (
                    actual_time_str
                    if actual_timestamp != timestamp
                    else time_str
                ),
                'response': response,
                'original_timestamp': timestamp,
                'is_exact_match': actual_timestamp == timestamp
            })
            found_count += 1
        else:
            print("❌ Not found")

    print()
    print(f"📊 Found {found_count}/{len(target_timestamps)} images")

    if not scan_results:
        print("❌ No MOSDAC radar data found in target hours")
        return

    print(f"📥 Downloading {len(scan_results)} images...")
    print()

    download_count = 0
    exact_matches = 0
    flexible_matches = 0

    for i, result in enumerate(scan_results, 1):
        print(f"[{i}/{len(scan_results)}] {result['time_str']}...",
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
                duplicate_file = find_duplicate_image(r.content, save_dir)
                if duplicate_file:
                    print(f"🔄 Duplicate ({duplicate_file.name})")
                    continue

                # Save image
                with open(filename, "wb") as f:
                    f.write(r.content)

                size_kb = len(r.content) / 1024
                print(f"✅ Saved ({size_kb:.1f} KB)")

                if result.get('is_exact_match', True):
                    exact_matches += 1
                else:
                    flexible_matches += 1

                download_count += 1
            else:
                print(f"❌ HTTP {r.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

    print()
    print("=" * 50)
    print("🎉 Download completed!")
    print(f"📊 Downloaded: {download_count} images")
    print(f"   🎯 Exact matches: {exact_matches}")
    print(f"   🔄 Flexible matches: {flexible_matches}")
    if flexible_matches > 0:
        print(f"🔧 Flexibility helped find {flexible_matches} "
              "additional images!")
    print(f"📁 Saved to: {save_dir}")
    print("=" * 50)


if __name__ == "__main__":
    download_mosdac_only()
