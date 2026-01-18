#!/usr/bin/env python3
"""
Quick Floor Sync Test
Verifies camera floor matches alert floor
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

API_URL = "http://localhost:8000/api/v1"

def main():
    print("=" * 50)
    print("  🔍 FLOOR SYNC CHECK")
    print("=" * 50)
    print()
    
    # Get camera info
    try:
        response = requests.get(f"{API_URL}/cameras/1")
        camera = response.json()['data']
        
        print(f"📹 Camera 1: {camera['name']}")
        print(f"   Assigned Floor: {camera['floor']['name']} (ID: {camera['floor_id']})")
        print()
    except Exception as e:
        print(f"❌ Error getting camera: {e}")
        return
    
    # Get recent alerts
    try:
        response = requests.get(f"{API_URL}/alerts?status=active")
        alerts = response.json()['alerts']
        
        if not alerts:
            print("✅ No active alerts - ready for testing!")
            print()
            print("👉 Start fire detection: START-FIRE-DETECTION.bat")
            print("   New alerts will appear on:", camera['floor']['name'])
            return
        
        print(f"🔥 Active Alerts: {len(alerts)}")
        print()
        
        # Check floor mismatch
        mismatch = False
        for alert in alerts[:3]:  # Check first 3
            if alert['floor_id'] != camera['floor_id']:
                mismatch = True
                print(f"   Alert #{alert['id']}: Floor {alert['floor_id']} ❌ MISMATCH")
            else:
                print(f"   Alert #{alert['id']}: Floor {alert['floor_id']} ✓")
        
        print()
        
        if mismatch:
            print("⚠️  FLOOR MISMATCH DETECTED!")
            print()
            print("Alerts are on wrong floor because fire detection")
            print("service is still running with old floor assignment.")
            print()
            print("🔧 FIX:")
            print("   1. Run: RESTART-FIRE-DETECTION.bat")
            print("   2. OR delete old alerts: delete-all-alerts-complete.bat")
            print()
        else:
            print("✅ All alerts match camera floor!")
            
    except Exception as e:
        print(f"❌ Error getting alerts: {e}")

if __name__ == "__main__":
    main()
