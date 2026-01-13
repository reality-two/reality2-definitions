#!/usr/bin/env python3
"""
Test script for all demo bees in the Reality2 Sentant system.

This script demonstrates:
- Individual bee functionality
- Swarm coordination
- Signal handling
- API integration patterns
"""

import sys
import time
from reality2 import Reality2

def print_separator(title=""):
    """Print a visual separator."""
    print("\n" + "="*80)
    if title:
        print(f"  {title}")
        print("="*80)
    print()

def test_agify(r2):
    """Test the Agify bee for age prediction."""
    print_separator("Testing Agify (Age Prediction)")

    try:
        # Load the bee
        r2.sentantLoad("Agify", "agify")
        print("✓ Agify bee loaded successfully")

        # Test with a common name
        test_name = "Michael"
        print(f"Predicting age for '{test_name}'...")
        r2.sentantSend("Agify", "Predict Age", {"name": test_name})

        # Wait for response
        for signal in r2.awaitSignal("Agify"):
            if signal.get("event") == "Age Prediction":
                print(f"✓ Age Prediction received:")
                print(f"  Name: {signal['parameters'].get('name')}")
                print(f"  Predicted Age: {signal['parameters'].get('age')}")
                print(f"  Data Points: {signal['parameters'].get('count')}")
                break

        # Unload
        r2.sentantUnload("Agify")
        print("✓ Agify bee unloaded")
        return True

    except Exception as e:
        print(f"✗ Error testing Agify: {e}")
        return False

def test_genderize(r2):
    """Test the Genderize bee for gender prediction."""
    print_separator("Testing Genderize (Gender Prediction)")

    try:
        r2.sentantLoad("Genderize", "genderize")
        print("✓ Genderize bee loaded successfully")

        test_name = "Sarah"
        print(f"Predicting gender for '{test_name}'...")
        r2.sentantSend("Genderize", "Predict Gender", {"name": test_name})

        for signal in r2.awaitSignal("Genderize"):
            if signal.get("event") == "Gender Prediction":
                print(f"✓ Gender Prediction received:")
                print(f"  Name: {signal['parameters'].get('name')}")
                print(f"  Predicted Gender: {signal['parameters'].get('gender')}")
                print(f"  Probability: {signal['parameters'].get('probability')}")
                print(f"  Data Points: {signal['parameters'].get('count')}")
                break

        r2.sentantUnload("Genderize")
        print("✓ Genderize bee unloaded")
        return True

    except Exception as e:
        print(f"✗ Error testing Genderize: {e}")
        return False

def test_nationalize(r2):
    """Test the Nationalize bee for nationality prediction."""
    print_separator("Testing Nationalize (Nationality Prediction)")

    try:
        r2.sentantLoad("Nationalize", "nationalize")
        print("✓ Nationalize bee loaded successfully")

        test_name = "Hans"
        print(f"Predicting nationality for '{test_name}'...")
        r2.sentantSend("Nationalize", "Predict Nationality", {"name": test_name})

        for signal in r2.awaitSignal("Nationalize"):
            if signal.get("event") == "Nationality Prediction":
                print(f"✓ Nationality Prediction received:")
                print(f"  Name: {signal['parameters'].get('name')}")
                print(f"  Country Code: {signal['parameters'].get('country_id')}")
                print(f"  Probability: {signal['parameters'].get('probability')}")
                break

        r2.sentantUnload("Nationalize")
        print("✓ Nationalize bee unloaded")
        return True

    except Exception as e:
        print(f"✗ Error testing Nationalize: {e}")
        return False

def test_adviceslip(r2):
    """Test the Advice Slip bee."""
    print_separator("Testing Advice Slip")

    try:
        r2.sentantLoad("Advice Slip", "adviceslip")
        print("✓ Advice Slip bee loaded successfully")

        print("Getting random advice...")
        r2.sentantSend("Advice Slip", "Get Advice", {})

        for signal in r2.awaitSignal("Advice Slip"):
            if signal.get("event") == "Advice Received":
                print(f"✓ Advice received:")
                print(f"  ID: {signal['parameters'].get('id')}")
                print(f"  Advice: {signal['parameters'].get('advice')}")
                break

        r2.sentantUnload("Advice Slip")
        print("✓ Advice Slip bee unloaded")
        return True

    except Exception as e:
        print(f"✗ Error testing Advice Slip: {e}")
        return False

def test_jokeapi(r2):
    """Test the JokeAPI bee."""
    print_separator("Testing JokeAPI")

    try:
        r2.sentantLoad("JokeAPI", "jokeapi")
        print("✓ JokeAPI bee loaded successfully")

        print("Getting a random joke...")
        r2.sentantSend("JokeAPI", "Get Joke", {})

        for signal in r2.awaitSignal("JokeAPI"):
            if signal.get("event") == "Joke Received":
                print(f"✓ Joke received:")
                print(f"  Category: {signal['parameters'].get('category')}")
                print(f"  Joke: {signal['parameters'].get('joke')}")
                print(f"  Safe: {signal['parameters'].get('safe')}")
                break

        r2.sentantUnload("JokeAPI")
        print("✓ JokeAPI bee unloaded")
        return True

    except Exception as e:
        print(f"✗ Error testing JokeAPI: {e}")
        return False

def test_uselessfacts(r2):
    """Test the Useless Facts bee."""
    print_separator("Testing Useless Facts")

    try:
        r2.sentantLoad("Useless Facts", "uselessfacts")
        print("✓ Useless Facts bee loaded successfully")

        print("Getting a random fact...")
        r2.sentantSend("Useless Facts", "Get Fact", {})

        for signal in r2.awaitSignal("Useless Facts"):
            if signal.get("event") == "Fact Received":
                print(f"✓ Fact received:")
                print(f"  ID: {signal['parameters'].get('id')}")
                print(f"  Fact: {signal['parameters'].get('fact')}")
                print(f"  Source: {signal['parameters'].get('source')}")
                break

        r2.sentantUnload("Useless Facts")
        print("✓ Useless Facts bee unloaded")
        return True

    except Exception as e:
        print(f"✗ Error testing Useless Facts: {e}")
        return False

def test_quotable(r2):
    """Test the Quotable bee."""
    print_separator("Testing Quotable")

    try:
        r2.sentantLoad("Quotable", "quotable")
        print("✓ Quotable bee loaded successfully")

        print("Getting a random quote...")
        r2.sentantSend("Quotable", "Get Quote", {})

        for signal in r2.awaitSignal("Quotable"):
            if signal.get("event") == "Quote Received":
                print(f"✓ Quote received:")
                print(f"  Quote: {signal['parameters'].get('quote')}")
                print(f"  Author: {signal['parameters'].get('author')}")
                print(f"  Tags: {signal['parameters'].get('tags')}")
                break

        r2.sentantUnload("Quotable")
        print("✓ Quotable bee unloaded")
        return True

    except Exception as e:
        print(f"✗ Error testing Quotable: {e}")
        return False

def test_restcountries(r2):
    """Test the REST Countries bee."""
    print_separator("Testing REST Countries")

    try:
        r2.sentantLoad("REST Countries", "restcountries")
        print("✓ REST Countries bee loaded successfully")

        test_country = "Japan"
        print(f"Getting information about {test_country}...")
        r2.sentantSend("REST Countries", "Get Country Info", {"country": test_country})

        for signal in r2.awaitSignal("REST Countries"):
            if signal.get("event") == "Country Info Received":
                print(f"✓ Country information received:")
                print(f"  Name: {signal['parameters'].get('name')}")
                print(f"  Official Name: {signal['parameters'].get('official_name')}")
                print(f"  Capital: {signal['parameters'].get('capital')}")
                print(f"  Region: {signal['parameters'].get('region')}")
                print(f"  Population: {signal['parameters'].get('population')}")
                print(f"  Area: {signal['parameters'].get('area')} km²")
                print(f"  Flag: {signal['parameters'].get('flag')}")
                break

        r2.sentantUnload("REST Countries")
        print("✓ REST Countries bee unloaded")
        return True

    except Exception as e:
        print(f"✗ Error testing REST Countries: {e}")
        return False

def test_name_intelligence_swarm(r2):
    """Test the Name Intelligence Swarm."""
    print_separator("Testing Name Intelligence Swarm")

    try:
        r2.swarmLoad("Name Intelligence", "name_intelligence")
        print("✓ Name Intelligence swarm loaded successfully")

        test_name = "Maria"
        print(f"Analyzing name '{test_name}'...")
        r2.sentantSend("Name Coordinator", "Analyze Name", {"name": test_name})

        for signal in r2.awaitSignal("Name Coordinator"):
            if signal.get("event") == "Complete Name Analysis":
                print(f"✓ Complete analysis received:")
                params = signal['parameters']
                print(f"  Name: {params.get('name')}")
                print(f"  Age: {params.get('age')} (based on {params.get('age_data_points')} data points)")
                print(f"  Gender: {params.get('gender')} (probability: {params.get('gender_probability')})")
                print(f"  Country: {params.get('country')} (probability: {params.get('nationality_probability')})")
                break

        r2.sentantUnload("Name Intelligence")
        print("✓ Name Intelligence swarm unloaded")
        return True

    except Exception as e:
        print(f"✗ Error testing Name Intelligence swarm: {e}")
        return False

def test_life_coach_swarm(r2):
    """Test the Life Coach Swarm."""
    print_separator("Testing Life Coach Swarm")

    try:
        r2.swarmLoad("Life Coach", "life_coach")
        print("✓ Life Coach swarm loaded successfully")

        print("Getting life coaching session...")
        r2.sentantSend("Coach Coordinator", "Get Life Coaching", {})

        for signal in r2.awaitSignal("Coach Coordinator"):
            if signal.get("event") == "Complete Life Coaching":
                print(f"✓ Life coaching session received:")
                params = signal['parameters']
                print(f"\n  Activity Suggestion:")
                print(f"    {params.get('activity')}")
                print(f"    Type: {params.get('activity_type')}")
                print(f"    Participants: {params.get('participants')}")
                print(f"\n  Advice:")
                print(f"    {params.get('advice')}")
                print(f"\n  Inspirational Quote:")
                print(f"    \"{params.get('quote')}\"")
                print(f"    - {params.get('quote_author')}")
                break

        r2.sentantUnload("Life Coach")
        print("✓ Life Coach swarm unloaded")
        return True

    except Exception as e:
        print(f"✗ Error testing Life Coach swarm: {e}")
        return False

def main():
    """Run all tests."""
    print_separator("Reality2 Demo Bees Test Suite")
    print("This script tests all demo bees and swarms")
    print("Make sure the Reality2 server is running on localhost:4005")

    # Connect to Reality2
    try:
        r2 = Reality2("localhost", 4005, ssl=False)
        print("✓ Connected to Reality2 server")
    except Exception as e:
        print(f"✗ Failed to connect to Reality2 server: {e}")
        return 1

    # Track results
    results = {}

    # Test individual bees
    print("\n" + "="*80)
    print("TESTING INDIVIDUAL BEES")
    print("="*80)

    results["Agify"] = test_agify(r2)
    results["Genderize"] = test_genderize(r2)
    results["Nationalize"] = test_nationalize(r2)
    results["Advice Slip"] = test_adviceslip(r2)
    results["JokeAPI"] = test_jokeapi(r2)
    results["Useless Facts"] = test_uselessfacts(r2)
    results["Quotable"] = test_quotable(r2)
    results["REST Countries"] = test_restcountries(r2)

    # Test swarms
    print("\n" + "="*80)
    print("TESTING SWARMS")
    print("="*80)

    results["Name Intelligence Swarm"] = test_name_intelligence_swarm(r2)
    results["Life Coach Swarm"] = test_life_coach_swarm(r2)

    # Print summary
    print_separator("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"Tests Passed: {passed}/{total}")
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
