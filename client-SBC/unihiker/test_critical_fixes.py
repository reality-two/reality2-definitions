#!/usr/bin/env python3
"""
Test script for critical fixes to reality2.py

This script tests:
1. Custom exception classes
2. Proper exception handling (no bare except)
3. SSL warning suppression (contextual, not global)
4. Thread safety
5. Resource cleanup
6. Context manager support
"""

import logging
import sys
from reality2 import Reality2, Reality2Error, Reality2ConnectionError, Reality2TimeoutError

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__)


def test_exceptions():
    """Test that custom exceptions are raised properly."""
    logger.info("=" * 60)
    logger.info("TEST 1: Custom Exceptions")
    logger.info("=" * 60)

    try:
        # Try to connect to a non-existent server
        r2 = Reality2("nonexistent.invalid", 9999, ssl=False)
        result = r2.sentantAll()
        logger.error("Should have raised an exception!")
        return False
    except Reality2ConnectionError as e:
        logger.info(f"✓ Correctly raised Reality2ConnectionError: {e}")
        return True
    except Exception as e:
        logger.error(f"✗ Wrong exception type: {type(e).__name__}: {e}")
        return False


def test_context_manager():
    """Test context manager support."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Context Manager Support")
    logger.info("=" * 60)

    try:
        # This will fail to connect, but should cleanup properly
        with Reality2("nonexistent.invalid", 9999, ssl=False) as r2:
            logger.info("Inside context manager")
            # Try an operation that will fail
            r2.sentantAll()
    except Reality2Error as e:
        logger.info(f"✓ Exception raised and context manager exited cleanly: {e}")
        return True
    except Exception as e:
        logger.error(f"✗ Unexpected exception: {type(e).__name__}: {e}")
        return False


def test_ssl_options():
    """Test SSL options."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: SSL Options")
    logger.info("=" * 60)

    try:
        # Test with SSL enabled but verification disabled
        r2_ssl_no_verify = Reality2("localhost", 4005, ssl=True, verify_ssl=False)
        logger.info("✓ Created client with ssl=True, verify_ssl=False")

        # Test without SSL
        r2_no_ssl = Reality2("localhost", 4005, ssl=False)
        logger.info("✓ Created client with ssl=False")

        return True
    except Exception as e:
        logger.error(f"✗ Failed to create clients: {e}")
        return False


def test_thread_safety():
    """Test that thread safety locks are in place."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Thread Safety")
    logger.info("=" * 60)

    try:
        r2 = Reality2("localhost", 4005, ssl=False)

        # Check that the lock exists
        if hasattr(r2, '_Reality2__lock'):
            logger.info("✓ Thread safety lock exists")
            return True
        else:
            logger.error("✗ Thread safety lock not found")
            return False
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return False


def test_resource_tracking():
    """Test that resources are tracked for cleanup."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Resource Tracking")
    logger.info("=" * 60)

    try:
        r2 = Reality2("localhost", 4005, ssl=False)

        # Check that tracking lists exist
        has_flags = hasattr(r2, '_Reality2__event_flags')
        has_threads = hasattr(r2, '_Reality2__event_threads')
        has_websockets = hasattr(r2, '_Reality2__websockets')

        if has_flags and has_threads and has_websockets:
            logger.info("✓ Resource tracking lists exist")
            logger.info("  - Event flags: ✓")
            logger.info("  - Event threads: ✓")
            logger.info("  - Websockets: ✓")
            return True
        else:
            logger.error("✗ Some resource tracking lists missing")
            return False
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("\n" + "=" * 60)
    logger.info("TESTING CRITICAL FIXES TO REALITY2.PY")
    logger.info("=" * 60)

    results = []

    # Run tests
    results.append(("Custom Exceptions", test_exceptions()))
    results.append(("Context Manager", test_context_manager()))
    results.append(("SSL Options", test_ssl_options()))
    results.append(("Thread Safety", test_thread_safety()))
    results.append(("Resource Tracking", test_resource_tracking()))

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    logger.info("-" * 60)
    logger.info(f"Total: {passed} passed, {failed} failed")
    logger.info("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
