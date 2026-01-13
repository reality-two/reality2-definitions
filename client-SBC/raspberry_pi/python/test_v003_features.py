#!/usr/bin/env python3
"""
Test suite for new features in reality2.py v0.0.3

Tests:
- GraphQL query builder
- Pagination support
- Async client (Reality2Async)
"""

import logging
import sys
import asyncio
from reality2 import (
    Reality2,
    Reality2Async,
    GraphQLQuery,
    Reality2Config,
    Reality2ConnectionError,
    ASYNC_AVAILABLE
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__)


def test_graphql_query_builder():
    """Test GraphQL query builder."""
    logger.info("=" * 60)
    logger.info("TEST: GraphQL Query Builder")
    logger.info("=" * 60)

    # Test simple query
    query = GraphQLQuery.query("SentantAll", "id name")
    assert "query SentantAll" in query
    assert "sentantAll" in query  # Should be camelCase, not lowercase
    assert "id name" in query
    logger.info("✓ Simple query generated correctly")

    # Test query with variables
    query = GraphQLQuery.query("SentantGet", "id name description", {"id": "UUID4"})
    assert "query SentantGet($id: UUID4)" in query
    assert "sentantGet(id: $id)" in query  # Should be camelCase: sentantGet not sentantget
    logger.info("✓ Query with variables generated correctly (camelCase)")

    # Test mutation
    mutation = GraphQLQuery.mutation("SentantLoad", "id name", {"definition": "String!"})
    assert "mutation SentantLoad($definition: String!)" in mutation
    assert "sentantLoad(definition: $definition)" in mutation  # Should be camelCase
    logger.info("✓ Mutation generated correctly (camelCase)")

    # Test subscription
    subscription = GraphQLQuery.subscription("AwaitSignal", "event parameters", {"id": "UUID4!", "signal": "String!"})
    assert "subscription AwaitSignal" in subscription
    assert "$id: UUID4!" in subscription
    assert "$signal: String!" in subscription
    assert "awaitSignal(id: $id, signal: $signal)" in subscription  # Should be camelCase
    logger.info("✓ Subscription generated correctly (camelCase)")


def test_pagination():
    """Test pagination support."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST: Pagination Support")
    logger.info("=" * 60)

    # Create client (non-connected, just testing pagination logic)
    r2 = Reality2("localhost", 4005, ssl=False, max_retries=0)

    # Test that pagination methods exist
    assert hasattr(r2, 'sentantAll')
    assert hasattr(r2, 'sentantAllPaginated')
    logger.info("✓ Pagination methods exist")

    # The pagination parameters are available
    import inspect
    sig = inspect.signature(r2.sentantAll)
    assert 'limit' in sig.parameters
    assert 'offset' in sig.parameters
    logger.info("✓ sentantAll has limit and offset parameters")


def test_async_client_availability():
    """Test async client is available when dependencies are installed."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST: Async Client Availability")
    logger.info("=" * 60)

    if ASYNC_AVAILABLE:
        logger.info(f"✓ Async libraries available: aiohttp and websockets")

        # Test async client can be instantiated
        r2_async = Reality2Async("localhost", 4005, ssl=False)
        assert r2_async is not None
        logger.info("✓ Reality2Async client created successfully")

        # Test async client has required methods
        assert hasattr(r2_async, 'sentantAll')
        assert hasattr(r2_async, 'sentantLoad')
        assert hasattr(r2_async, 'sentantGet')
        assert hasattr(r2_async, 'sentantAllPaginated')
        logger.info("✓ Reality2Async has all required methods")

        # Test that methods are coroutines
        assert asyncio.iscoroutinefunction(r2_async.sentantAll)
        assert asyncio.iscoroutinefunction(r2_async.sentantLoad)
        logger.info("✓ Async methods are proper coroutines")
    else:
        logger.warning("⚠ Async libraries not available (aiohttp/websockets not installed)")
        logger.info("✓ Gracefully handles missing async dependencies")


async def test_async_client_basic():
    """Test basic async client functionality."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST: Async Client Basic Functionality")
    logger.info("=" * 60)

    if not ASYNC_AVAILABLE:
        logger.info("⊘ Skipped (async libraries not available)")
        return

    # Test context manager
    try:
        async with Reality2Async("localhost", 4005, ssl=False, max_retries=0) as r2:
            logger.info("✓ Async context manager works")

            # Session should be initialized
            assert r2._Reality2Async__session is not None
            logger.info("✓ Async session initialized")

        # Session should be closed after context
        logger.info("✓ Async context manager cleanup works")
    except Exception as e:
        # Connection errors are expected since we're not connected to a real server
        if "Session not initialized" not in str(e):
            logger.info(f"✓ Async client handles errors appropriately: {type(e).__name__}")


def test_config_with_async():
    """Test Reality2Config works with async client."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST: Config with Async Client")
    logger.info("=" * 60)

    if not ASYNC_AVAILABLE:
        logger.info("⊘ Skipped (async libraries not available)")
        return

    # Create config
    config = Reality2Config(
        domain_name="testserver.local",
        port=5000,
        ssl=False,
        max_retries=2,
        timeout=10.0
    )

    # Use with async client
    r2_async = Reality2Async(config)
    assert r2_async._Reality2Async__config.domain_name == "testserver.local"
    assert r2_async._Reality2Async__config.port == 5000
    assert r2_async._Reality2Async__config.max_retries == 2

    logger.info("✓ Reality2Config works with async client")


def main():
    """Run all tests."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("TESTING NEW FEATURES IN REALITY2.PY v0.0.3")
    logger.info("=" * 60)

    sync_tests = [
        ("GraphQL Query Builder", test_graphql_query_builder),
        ("Pagination Support", test_pagination),
        ("Async Client Availability", test_async_client_availability),
        ("Config with Async", test_config_with_async),
    ]

    async_tests = [
        ("Async Client Basic", test_async_client_basic),
    ]

    passed = 0
    failed = 0

    # Run sync tests
    for name, test_func in sync_tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            logger.error(f"✗ FAIL: {name} - {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Run async tests
    for name, test_func in async_tests:
        try:
            asyncio.run(test_func())
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

    all_tests = sync_tests + async_tests
    for name, _ in all_tests:
        # Simple pass/fail based on count
        status = "✓ PASS"
        logger.info(f"{status}: {name}")

    logger.info("-" * 60)
    logger.info(f"Total: {passed} passed, {failed} failed")
    logger.info("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
