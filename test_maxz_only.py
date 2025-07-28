#!/usr/bin/env python3
"""
Quick test of MAXZ radar download
"""

import requests
from datetime import datetime, UTC
from pathlib import Path

def test_maxz_download():
    """Test downloading MAXZ radar specifically."""

    print("🧪 Testing MAXZ Radar Download")
    print("=" * 35)

    url = ("http://117.221.70.132/geoserver/dwr_kochi/wms?"
           "service=WMS&request=GetMap&layers=dwr_kochi:maxz_image"
           "&styles=&format=image/png&transparent=true&version=1.1.1"
           "&width=1024&height=1024&srs=EPSG:4326&bbox=74.0,8.0,78.0,12.0")

    print(f"URL: {url[:80]}...")
    print()

    # Create directory
    maxz_dir = Path("radar_images/maxz")
    maxz_dir.mkdir(parents=True, exist_ok=True)

    # Get current time for filename
    current_time = datetime.now(UTC)
    timestamp_str = current_time.strftime("%Y%m%d_%H%M")
    filename = maxz_dir / f"maxz_radar_{timestamp_str}.png"

    print(f"📁 Target file: {filename}")
    print()

    try:
        print("📡 Downloading MAXZ radar...")
        response = requests.get(url, timeout=15)

        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Content-Length: {len(response.content)} bytes")

        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()

            if 'image/png' in content_type:
                # Save the file
                with open(filename, 'wb') as f:
                    f.write(response.content)

                print(f"✅ Successfully saved: {filename}")
                print(f"   File size: {len(response.content)} bytes")
                print(f"   📊 WMS Max Z Reflectivity (1024x1024 PNG)")

                return True
            else:
                print(f"❌ Unexpected content type: {content_type}")
                if content_type.startswith('text'):
                    print("Response preview:")
                    print(response.text[:500])
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_maxz_download()

    if success:
        print("\n🎉 MAXZ radar download successful!")
        print("   Ready for integration into main radar scraper")
    else:
        print("\n⚠️ MAXZ radar download failed")
        print("   Check network connection and server status")
