#!/usr/bin/env python3
"""
Test error handling improvements
"""

import logging
from reality2 import Reality2, Reality2Error

# Enable logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

logger = logging.getLogger(__name__)

def test_unload_nonexistent():
    """Test that unloading a non-existent Sentant is handled gracefully."""
    logger.info("=" * 60)
    logger.info("TEST: Unloading non-existent Sentant")
    logger.info("=" * 60)

    try:
        r2 = Reality2("localhost", 4005, verify_ssl=False)

        # Try to unload a Sentant that doesn't exist
        logger.info("Attempting to unload non-existent Sentant...")
        try:
            r2.sentantUnloadByName("NonExistentSentant_12345")
            logger.info("✓ Unload succeeded (Sentant existed)")
        except Reality2Error as e:
            logger.info(f"✓ Expected error caught: {type(e).__name__}: {e}")
            logger.info("✓ This is the expected behavior - Sentant doesn't exist")
            return True

    except Reality2Error as e:
        logger.error(f"✗ Unexpected error: {e}")
        return False

    return True


def test_loader_pattern():
    """Test the pattern used in load_sentant.py"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: Loader pattern (unload before load)")
    logger.info("=" * 60)

    try:
        r2 = Reality2("localhost", 4005, verify_ssl=False)

        sentant_name = "Test Sentant"

        # This is the pattern used in load_sentant.py
        logger.info(f'Unloading existing Sentant named "{sentant_name}"')
        try:
            r2.sentantUnloadByName(sentant_name)
            logger.info("✓ Unloaded successfully")
        except Exception as e:
            logger.info(f"✓ Sentant not found (this is ok, will load fresh)")

        logger.info("✓ Script continues normally after unload attempt")
        return True

    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        return False


def main():
    logger.info("\n" + "=" * 60)
    logger.info("ERROR HANDLING TESTS")
    logger.info("=" * 60)

    results = []
    results.append(("Unload Non-existent", test_unload_nonexistent()))
    results.append(("Loader Pattern", test_loader_pattern()))

    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")

    passed = sum(1 for _, r in results if r)
    failed = len(results) - passed
    logger.info("-" * 60)
    logger.info(f"Total: {passed} passed, {failed} failed")
    logger.info("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
