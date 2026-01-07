#!/usr/bin/env python3
"""
Test script for the Bored API bee

This script loads the Bored API bee and tests its functionality.
"""

import sys
import time
from reality2 import Reality2

def test_boredapi():
    """Test the Bored API bee."""
    print("=" * 60)
    print("Testing Bored API Bee")
    print("=" * 60)

    # Connect to Reality2
    with Reality2("localhost", 4005, verify_ssl=False) as r2:
        print("\n✓ Connected to Reality2")

        # Load the bee definition
        print("\n📝 Loading Bored API bee...")
        with open('../bees/boredapi.bee.yaml', 'r') as f:
            bee_definition = f.read()

        result = r2.sentantLoad(bee_definition)

        if "sentantLoad" in result and result["sentantLoad"]:
            sentant_id = result["sentantLoad"]["id"]
            sentant_name = result["sentantLoad"]["name"]
            print(f"✓ Loaded bee: {sentant_name} (ID: {sentant_id})")

            # Define callback for activity suggestions
            def on_activity(data):
                print("\n🎯 Activity Suggestion Received!")
                print("-" * 60)
                if "awaitSignal" in data:
                    signal_data = data["awaitSignal"]
                    params = signal_data.get("parameters", {})

                    activity = params.get("activity")
                    activity_type = params.get("type")
                    participants = params.get("participants")
                    price = params.get("price")
                    accessibility = params.get("accessibility")

                    print(f"Activity: {activity}")
                    print(f"Type: {activity_type}")
                    print(f"Participants: {participants}")
                    print(f"Price Level: {price} (0=free, 1=expensive)")
                    print(f"Accessibility: {accessibility} (0=easy, 1=hard)")
                print("-" * 60)

            # Subscribe to activity suggestions
            print("\n📡 Subscribing to activity suggestions...")
            r2.awaitSignal(sentant_id, "Activity Suggestion", on_activity)

            # Request a random activity
            print("\n🎲 Requesting random activity...")
            r2.sentantSend(sentant_id, "Get Activity", {})

            # Wait for response
            print("⏳ Waiting for activity suggestion...")
            time.sleep(3)

            # Request another activity
            print("\n🎲 Requesting another random activity...")
            r2.sentantSend(sentant_id, "Get Activity", {})

            # Wait for response
            time.sleep(3)

            # Cleanup
            print("\n🧹 Cleaning up...")
            r2.sentantUnload(sentant_id)
            print("✓ Bee unloaded")

        else:
            print("✗ Failed to load bee")
            print(f"Response: {result}")
            return False

    print("\n" + "=" * 60)
    print("✅ Bored API Test Complete!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_boredapi()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
