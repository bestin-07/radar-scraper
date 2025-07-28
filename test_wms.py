#!/usr/bin/env python3
"""
Test script to analyze the WMS URL provided by the user.
"""

import requests
from datetime import datetime

def test_wms_url():
    """Test the WMS URL and analyze its response."""

    url = ("http://117.221.70.132/geoserver/dwr_kochi/wms?"
           "service=WMS&request=GetMap&layers=dwr_kochi:maxz_image"
           "&styles=&format=image/png&transparent=true&version=1.1.1"
           "&width=1024&height=1024&srs=EPSG:4326&bbox=74.0,8.0,78.0,12.0")

    print("🔍 WMS URL Analysis")
    print("=" * 50)
    print(f"URL: {url}")
    print()

    try:
        # Test with HEAD request first
        print("📡 Testing with HEAD request...")
        response = requests.head(url, timeout=15)

        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Content-Length: {response.headers.get('content-length', 'N/A')}")
        print(f"Server: {response.headers.get('server', 'N/A')}")
        print()

        if response.status_code == 200:
            # Test with GET request to analyze actual data
            print("📥 Testing with GET request...")
            response = requests.get(url, timeout=15)

            content_type = response.headers.get('content-type', '').lower()
            print(f"Actual Content-Type: {content_type}")
            print(f"Response size: {len(response.content)} bytes")

            if 'image/png' in content_type:
                # Save the image for inspection
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"wms_test_{timestamp}.png"

                with open(filename, 'wb') as f:
                    f.write(response.content)

                print(f"✅ PNG image saved as: {filename}")
                print(f"   Image size: {len(response.content)} bytes")

                # Analyze if this could be integrated into radar scraper
                print()
                print("🔬 Integration Analysis:")
                print("   ✅ Valid PNG image format")
                print("   ✅ Same server as existing radar URLs")
                print("   ✅ Geographic data (WMS with EPSG:4326)")
                print("   📊 Coordinates: Kerala region (74°-78°E, 8°-12°N)")
                print("   🛰️ Layer: maxz_image (Maximum Z reflectivity)")

            elif 'text/html' in content_type:
                print("⚠️ Received HTML instead of image")
                print("First 500 chars of response:")
                print(response.text[:500])

            else:
                print(f"⚠️ Unexpected content type: {content_type}")

        else:
            print(f"❌ Request failed with status {response.status_code}")

    except requests.exceptions.Timeout:
        print("⏰ Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def analyze_wms_parameters():
    """Analyze the WMS parameters in the URL."""

    print("\n🔧 WMS Parameters Analysis:")
    print("=" * 30)

    params = {
        'service': 'WMS',
        'request': 'GetMap',
        'layers': 'dwr_kochi:maxz_image',
        'format': 'image/png',
        'transparent': 'true',
        'version': '1.1.1',
        'width': '1024',
        'height': '1024',
        'srs': 'EPSG:4326',
        'bbox': '74.0,8.0,78.0,12.0'
    }

    for key, value in params.items():
        print(f"   {key:12}: {value}")

    print("\n📍 Geographic Coverage:")
    print("   📐 Bounding Box: 74°-78°E, 8°-12°N")
    print("   🗺️  Covers: Kerala, India")
    print("   📏 Resolution: 1024x1024 pixels")
    print("   🌍 Projection: WGS84 (EPSG:4326)")

    print("\n🛰️ Radar Data Type:")
    print("   📊 Layer: dwr_kochi:maxz_image")
    print("   🌦️  Type: Maximum Z Reflectivity")
    print("   📈 Purpose: Weather radar composite")

def test_timestamp_behavior():
    """Test if the WMS endpoint provides updated data over time."""

    print("\n🕐 Timestamp Behavior Analysis:")
    print("=" * 35)

    base_url = ("http://117.221.70.132/geoserver/dwr_kochi/wms?"
                "service=WMS&request=GetMap&layers=dwr_kochi:maxz_image"
                "&styles=&format=image/png&transparent=true&version=1.1.1"
                "&width=1024&height=1024&srs=EPSG:4326&bbox=74.0,8.0,78.0,12.0")

    # Test 1: Multiple requests to check if data changes
    print("📡 Testing multiple requests for data changes...")

    images = []
    for i in range(3):
        try:
            response = requests.get(base_url, timeout=10)
            if response.status_code == 200:
                images.append(response.content)
                print(f"   Request {i+1}: {len(response.content)} bytes")
            else:
                print(f"   Request {i+1}: Failed ({response.status_code})")
        except Exception as e:
            print(f"   Request {i+1}: Error - {e}")

    # Check if images are identical
    if len(images) >= 2:
        identical = all(img == images[0] for img in images[1:])
        print(f"   📊 Images identical: {'Yes' if identical else 'No'}")
        if identical:
            print("   ⚠️  Data appears static (same image returned)")
        else:
            print("   ✅ Data appears dynamic (different images)")

    # Test 2: Check for timestamp parameters
    print("\n🔍 Testing timestamp parameters...")

    from datetime import datetime, UTC
    import urllib.parse

    current_time = datetime.now(UTC)

    # Test various timestamp formats
    timestamp_formats = [
        ('time', current_time.strftime('%Y-%m-%dT%H:%M:%SZ')),  # ISO format
        ('TIME', current_time.strftime('%Y-%m-%dT%H:%M:%SZ')),  # Uppercase
        ('timestamp', current_time.strftime('%Y%m%d%H%M%S')),   # Compact format
        ('t', current_time.strftime('%Y-%m-%d %H:%M:%S')),      # Simple format
        ('datetime', current_time.strftime('%Y-%m-%d_%H-%M-%S')) # Alternative
    ]

    for param_name, timestamp_value in timestamp_formats:
        test_url = f"{base_url}&{param_name}={urllib.parse.quote(timestamp_value)}"

        try:
            response = requests.head(test_url, timeout=5)
            print(f"   {param_name:10}: HTTP {response.status_code}")

            if response.status_code == 200:
                # Test with actual GET to see if it affects content
                get_response = requests.get(test_url, timeout=5)
                size = len(get_response.content)
                print(f"              Content size: {size} bytes")

        except Exception as e:
            print(f"   {param_name:10}: Error - {e}")

    # Test 3: Check WMS GetCapabilities for temporal information
    print("\n📋 Checking WMS Capabilities...")

    capabilities_url = ("http://117.221.70.132/geoserver/dwr_kochi/wms?"
                       "service=WMS&request=GetCapabilities")

    try:
        response = requests.get(capabilities_url, timeout=10)
        if response.status_code == 200:
            capabilities_text = response.text
            print(f"   ✅ GetCapabilities successful ({len(capabilities_text)} chars)")

            # Look for temporal/time-related information
            time_keywords = ['time', 'temporal', 'dimension', 'extent', 'default']
            found_keywords = []

            for keyword in time_keywords:
                if keyword.lower() in capabilities_text.lower():
                    found_keywords.append(keyword)

            if found_keywords:
                print(f"   🕐 Found time-related keywords: {', '.join(found_keywords)}")

                # Extract relevant sections
                lines = capabilities_text.split('\n')
                for i, line in enumerate(lines):
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in ['time', 'temporal', 'dimension']):
                        print(f"   📄 Line {i+1}: {line.strip()[:100]}...")
            else:
                print("   ⚠️  No obvious time-related parameters found")

        else:
            print(f"   ❌ GetCapabilities failed: HTTP {response.status_code}")

    except Exception as e:
        print(f"   ❌ GetCapabilities error: {e}")

if __name__ == "__main__":
    test_wms_url()
    analyze_wms_parameters()
    test_timestamp_behavior()

    print("\n💡 Integration Recommendations:")
    print("   1. Add as new radar type: 'maxz'")
    print("   2. Use base URL without timestamp (appears to be real-time)")
    print("   3. Higher quality PNG format (vs current GIF)")
    print("   4. Monitor for any data freshness patterns")
    print("   5. Consider as primary radar source due to quality")
