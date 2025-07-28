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
import json


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
    # Load known timestamps and reference
    if known_timestamps is None or reference_timestamp is None:
        known_timestamps, reference_timestamp = load_known_timestamps()

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

    # Determine direction based on two-hour window
    two_hours_ago = current_total_sec - 7200  # 2 hours = 7200 seconds
    two_hours_ahead = current_total_sec + 7200

    # Decide if we need forward, backward, or both
    if ref_total_sec < two_hours_ago:
        # Reference is too old, generate forward
        print("⏩ Generating forward from reference (reference is old)")
        direction = "forward"
    elif ref_total_sec > two_hours_ahead:
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

        while current_check_sec <= two_hours_ahead and iteration < 50:
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

        while current_check_sec >= two_hours_ago and iteration < 50:
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

    # Filter for two-hour window around current time
    filtered_timestamps = []
    for ts in timestamps:
        ts_h = int(ts[:2])
        ts_m = int(ts[2:4])
        ts_s = int(ts[4:6])
        ts_total_sec = ts_h * 3600 + ts_m * 60 + ts_s

        # Include if it's within two hour window
        if two_hours_ago <= ts_total_sec <= two_hours_ahead:
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
    """Download only MOSDAC data with adaptive reference updates."""
    print("🌦️  MOSDAC Radar Data Downloader")
    print("=" * 50)

    # Setup save directory
    save_dir = Path("radar_images/kochi")
    save_dir.mkdir(parents=True, exist_ok=True)

    current_time = datetime.now(UTC)
    current_hour = current_time.hour
    previous_hour = current_hour - 1 if current_hour > 0 else 23
    two_hours_ago = (current_hour - 2 if current_hour >= 2
                     else (24 + current_hour - 2))

    # Target the last 2 hours plus current hour for comprehensive coverage
    target_hours = [two_hours_ago, previous_hour, current_hour]

    print(f"🕐 Current UTC time: {current_time.strftime('%H:%M')} UTC")
    print(f"🎯 Target hours: {two_hours_ago:02d}:xx, {previous_hour:02d}:xx "
          f"and {current_hour:02d}:xx UTC")
    print(f"📁 Save directory: {save_dir}")
    print()

    # Load existing known timestamps and reference
    known_timestamps, reference_timestamp = load_known_timestamps()
    print(f"📊 Starting with {len(known_timestamps)} known valid timestamps")

    # Generate timestamps
    print("🔍 Generating adaptive timestamps...")
    all_timestamps = generate_forward_timestamps_from_latest(
        current_time, include_variants=True,
        known_timestamps=known_timestamps,
        reference_timestamp=reference_timestamp)

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
    consecutive_not_found = 0  # Track consecutive failures
    max_consecutive_failures = 5  # Early exit threshold
    # Copy existing known timestamps
    new_valid_timestamps = list(known_timestamps)
    latest_found_timestamp = reference_timestamp

    for i, timestamp in enumerate(target_timestamps, 1):
        time_str = f"{timestamp[:2]}:{timestamp[2:4]}:{timestamp[4:6]}"
        print(f"  [{i:2d}/{len(target_timestamps)}] {time_str}...",
              end=" ", flush=True)

        success, actual_timestamp, response = (
            check_timestamp_with_flexibility(timestamp, tolerance_seconds=20))

        if success:
            consecutive_not_found = 0  # Reset counter on success

            if actual_timestamp == timestamp:
                print("✅ Available (exact)")
            else:
                actual_time_str = (
                    f"{actual_timestamp[:2]}:"
                    f"{actual_timestamp[2:4]}:"
                    f"{actual_timestamp[4:6]}"
                )
                print(f"✅ Available ({actual_time_str})")

            # Add to new valid timestamps if not already known
            if actual_timestamp not in new_valid_timestamps:
                new_valid_timestamps.append(actual_timestamp)
                print("    🆕 New timestamp added to known list")

            # Update latest found timestamp
            actual_h = int(actual_timestamp[:2])
            actual_m = int(actual_timestamp[2:4])
            actual_s = int(actual_timestamp[4:6])
            actual_total_sec = actual_h * 3600 + actual_m * 60 + actual_s

            latest_h = int(latest_found_timestamp[:2])
            latest_m = int(latest_found_timestamp[2:4])
            latest_s = int(latest_found_timestamp[4:6])
            latest_total_sec = latest_h * 3600 + latest_m * 60 + latest_s

            if actual_total_sec > latest_total_sec:
                old_ref = latest_found_timestamp
                latest_found_timestamp = actual_timestamp
                old_time = f"{old_ref[:2]}:{old_ref[2:4]}:{old_ref[4:6]}"
                new_time = (f"{actual_timestamp[:2]}:"
                            f"{actual_timestamp[2:4]}:"
                            f"{actual_timestamp[4:6]}")
                print(f"    📈 Reference updated: {old_time} → {new_time}")

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
            consecutive_not_found += 1
            print("❌ Not found")

            # Early exit if too many consecutive failures
            if consecutive_not_found >= max_consecutive_failures:
                remaining = len(target_timestamps) - i
                print(f"\n⚠️  Early exit: {consecutive_not_found} consecutive "
                      f"failures detected")
                print(f"   Skipping {remaining} remaining timestamps")

                # If no data found, adjust reference to most recent known
                if found_count == 0 and new_valid_timestamps:
                    # Find most recent known timestamp within reasonable time
                    current_total_sec = (
                        current_time.hour * 3600 +
                        current_time.minute * 60 +
                        current_time.second
                    )

                    # Sort known timestamps and find the most recent one
                    # that's not too far in the future
                    best_reference = None
                    best_distance = float('inf')

                    for known_ts in new_valid_timestamps:
                        known_h = int(known_ts[:2])
                        known_m = int(known_ts[2:4])
                        known_s = int(known_ts[4:6])
                        known_sec = known_h * 3600 + known_m * 60 + known_s

                        # Calculate distance (prefer past timestamps)
                        distance = abs(current_total_sec - known_sec)

                        # Prefer timestamps in past but not too old
                        if (known_sec <= current_total_sec and
                                distance < best_distance and
                                distance <= 7200):  # Within 2 hours
                            best_distance = distance
                            best_reference = known_ts

                    ref_changed = (best_reference and
                                   best_reference != reference_timestamp)
                    if ref_changed:
                        latest_found_timestamp = best_reference
                        old_time = (f"{reference_timestamp[:2]}:"
                                    f"{reference_timestamp[2:4]}:"
                                    f"{reference_timestamp[4:6]}")
                        new_time = (f"{best_reference[:2]}:"
                                    f"{best_reference[2:4]}:"
                                    f"{best_reference[4:6]}")
                        print(f"   📍 Adjusting reference to known point: "
                              f"{old_time} → {new_time}")
                        print("   💡 This will improve next run's predictions")

                break

    # Save updated known timestamps and reference
    timestamps_changed = new_valid_timestamps != known_timestamps
    reference_changed = latest_found_timestamp != reference_timestamp

    if timestamps_changed or reference_changed:
        save_known_timestamps(new_valid_timestamps, latest_found_timestamp)
        added_count = len(new_valid_timestamps) - len(known_timestamps)
        if added_count > 0:
            print(f"📊 Added {added_count} new timestamps to knowledge base")
        if reference_changed:
            old_time = (f"{reference_timestamp[:2]}:"
                        f"{reference_timestamp[2:4]}:"
                        f"{reference_timestamp[4:6]}")
            new_time = (f"{latest_found_timestamp[:2]}:"
                        f"{latest_found_timestamp[2:4]}:"
                        f"{latest_found_timestamp[4:6]}")
            print(f"📈 Final reference update: {old_time} → {new_time}")

    print()
    print(f"📊 Found {found_count}/{len(target_timestamps)} images")

    if not scan_results:
        if consecutive_not_found >= max_consecutive_failures:
            print("❌ No new MOSDAC data found - early exit after "
                  f"{consecutive_not_found} consecutive failures")
            print("💡 Reference time has been adjusted for better "
                  "predictions next time")
        else:
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
    if len(new_valid_timestamps) > len(known_timestamps):
        total_timestamps = len(new_valid_timestamps)
        print(f"🧠 Knowledge base updated with {total_timestamps} "
              "total timestamps")
    print("=" * 50)


if __name__ == "__main__":
    download_mosdac_only()
