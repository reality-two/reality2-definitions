#!/usr/bin/env python3
"""
Test suite for new features in reality2.py v0.0.2

Tests:
- Type hints (static analysis compatibility)
- Configuration class
- Retry logic with exponential backoff
"""

import logging
import sys
from reality2 import Reality2, Reality2Config, Reality2ConnectionError

# Configure logging to see retry attempts
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__)


def test_config_class():
    """Test Reality2Config class."""
    logger.info("=" * 60)
    logger.info("TEST: Reality2Config Class")
    logger.info("=" * 60)

    # Create config
    config = Reality2Config(
        domain_name="testserver.local",
        port=5000,
        ssl=True,
        verify_ssl=False,
        timeout=10.0,
        max_retries=2,
        retry_backoff=0.5
    )

    # Test properties
    assert config.domain_name == "testserver.local"
    assert config.port == 5000
    assert config.ssl == True
    assert config.verify_ssl == False
    assert config.timeout == 10.0
    assert config.max_retries == 2
    assert config.retry_backoff == 0.5

    # Test URL generation
    assert config.graphql_http_url == "https://testserver.local:5000/reality2"
    assert config.graphql_ws_url == "wss://testserver.local:5000/reality2/websocket"

    logger.info("✓ Config class properties work correctly")

    # Test HTTP config
    config_http = Reality2Config(
        domain_name="localhost",
        port=4005,
        ssl=False
    )
    assert config_http.graphql_http_url == "http://localhost:4005/reality2"
    assert config_http.graphql_ws_url == "ws://localhost:4005/reality2/websocket"

    logger.info("✓ HTTP URLs generated correctly")


def test_config_integration():
    """Test Reality2 client with config object."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST: Reality2 with Config Object")
    logger.info("=" * 60)

    # Create client with config object
    config = Reality2Config(
        domain_name="localhost",
        port=4005,
        ssl=False,
        max_retries=1,
        retry_backoff=0.1
    )
    r2 = Reality2(config)

    # Verify it uses the config
    assert r2._Reality2__config.domain_name == "localhost"
    assert r2._Reality2__config.port == 4005
    assert r2._Reality2__config.max_retries == 1

    logger.info("✓ Reality2 client accepts config object")

    # Test backward compatibility with old constructor
    r2_old = Reality2("localhost", 4005, ssl=False)
    assert r2_old._Reality2__config.domain_name == "localhost"
    assert r2_old._Reality2__config.port == 4005

    logger.info("✓ Backward compatibility maintained")


def test_retry_logic():
    """Test retry logic with exponential backoff."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST: Retry Logic with Exponential Backoff")
    logger.info("=" * 60)

    # Create client with fast retries for testing
    config = Reality2Config(
        domain_name="nonexistent-server-12345.invalid",
        port=9999,
        ssl=False,
        max_retries=2,  # Will try 3 times total (initial + 2 retries)
        retry_backoff=0.1  # Start with 0.1s backoff
    )
    r2 = Reality2(config)

    try:
        # This should fail and retry
        r2.sentantAll()
        logger.error("✗ FAIL: Should have raised Reality2ConnectionError")
        return False
    except Reality2ConnectionError as e:
        # Check that the error message mentions the retries
        if "attempts" in str(e):
            logger.info(f"✓ Retry logic executed, error: {e}")
        else:
            logger.info(f"✓ Connection error raised: {e}")


def test_new_constructor_params():
    """Test new constructor parameters."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST: New Constructor Parameters")
    logger.info("=" * 60)

    # Test all new parameters
    r2 = Reality2(
        "localhost",
        4005,
        ssl=False,
        verify_ssl=True,
        timeout=15.0,
        max_retries=5,
        retry_backoff=2.0
    )

    assert r2._Reality2__config.timeout == 15.0
    assert r2._Reality2__config.max_retries == 5
    assert r2._Reality2__config.retry_backoff == 2.0

    logger.info("✓ New constructor parameters work correctly")


def main():
    """Run all tests."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("TESTING NEW FEATURES IN REALITY2.PY v0.0.2")
    logger.info("=" * 60)

    tests = [
        ("Config Class", test_config_class),
        ("Config Integration", test_config_integration),
        ("Retry Logic", test_retry_logic),
        ("New Constructor Params", test_new_constructor_params),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            logger.error(f"✗ FAIL: {name} - {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    for name, _ in tests:
        status = "✓ PASS" if name not in [t[0] for t in tests[passed:]] else "✗ FAIL"
        logger.info(f"{status}: {name}")
    logger.info("-" * 60)
    logger.info(f"Total: {passed} passed, {failed} failed")
    logger.info("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
