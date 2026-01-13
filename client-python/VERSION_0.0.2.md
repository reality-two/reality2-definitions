# Reality2 Python Client v0.0.2 - New Features

## Summary of Improvements

Version 0.0.2 adds significant improvements to the Reality2 Python client library, focusing on developer experience, reliability, and code quality.

---

## New Features

### 1. Comprehensive Type Hints ✨

**What:** Full type annotations throughout the codebase using Python's `typing` module.

**Why:** Better IDE autocomplete, static type checking with mypy/pyright, and improved code documentation.

**Example:**
```python
from typing import Dict, List, Optional, Any

def sentantLoad(self, definition: str, passthrough: Dict[str, Any] = {}, details: str = "id name") -> Dict[str, Any]:
    ...
```

**Benefits:**
- Catch type errors before runtime
- Better IDE support (autocomplete, inline documentation)
- Clearer API contracts
- Easier refactoring

---

### 2. Configuration Class 🔧

**What:** New `Reality2Config` class for centralized configuration management.

**Why:** Cleaner code organization, easier to pass configuration around, and better defaults management.

**Basic Usage:**
```python
from reality2 import Reality2, Reality2Config

# Old way (still supported):
r2 = Reality2("localhost", 4005, ssl=False, verify_ssl=False)

# New way with config object:
config = Reality2Config(
    domain_name="localhost",
    port=4005,
    ssl=False,
    verify_ssl=False,
    timeout=30.0,
    max_retries=3,
    retry_backoff=1.0
)
r2 = Reality2(config)
```

**Config Properties:**
- `domain_name`: Server hostname/IP
- `port`: Server port number
- `ssl`: Use SSL/TLS
- `verify_ssl`: Verify SSL certificates
- `timeout`: Request timeout in seconds
- `max_retries`: Maximum retry attempts
- `retry_backoff`: Initial backoff time for retries

**Auto-generated URLs:**
```python
config.graphql_http_url   # "https://localhost:4005/reality2"
config.graphql_ws_url     # "wss://localhost:4005/reality2/websocket"
```

**Benefits:**
- Single source of truth for configuration
- Easy to serialize/deserialize
- Type-safe configuration
- Backward compatible with old constructor

---

### 3. Retry Logic with Exponential Backoff 🔄

**What:** Automatic retries for failed network requests with exponential backoff and jitter.

**Why:** Improves reliability in unstable network conditions, handles transient failures gracefully.

**How It Works:**
1. Initial request fails (connection or timeout)
2. Wait: `backoff_time = initial_backoff * (2 ^ attempt) + random_jitter`
3. Retry up to `max_retries` times
4. Raise exception if all attempts fail

**Configuration:**
```python
r2 = Reality2(
    "api.example.com",
    4005,
    max_retries=5,          # Try up to 6 times total (initial + 5 retries)
    retry_backoff=1.0       # Start with 1 second backoff
)
```

**Retry Timeline Example:**
- Attempt 1: Immediate
- Attempt 2: After ~1.0s (1.0 * 2^0 + jitter)
- Attempt 3: After ~2.0s (1.0 * 2^1 + jitter)
- Attempt 4: After ~4.0s (1.0 * 2^2 + jitter)
- Total wait: ~7 seconds for 3 retries

**What Gets Retried:**
- Connection errors (`requests.exceptions.ConnectionError`)
- Timeout errors (`requests.exceptions.Timeout`)

**What Does NOT Get Retried:**
- GraphQL errors (invalid query, validation errors)
- HTTP errors (4xx, 5xx status codes)
- Invalid responses (parsing errors)

**Logging:**
```
WARNING: GraphQL request attempt 1/3 failed: Connection refused. Retrying in 1.05s...
WARNING: GraphQL request attempt 2/3 failed: Connection refused. Retrying in 2.12s...
ERROR: All 3 GraphQL request attempts failed
```

**Benefits:**
- Handles temporary network issues automatically
- Reduces failed requests due to transient errors
- Exponential backoff prevents overwhelming the server
- Jitter prevents thundering herd problem

---

## Backward Compatibility

All improvements are **100% backward compatible**:

```python
# Old code still works exactly the same:
r2 = Reality2("localhost", 4005, ssl=False, verify_ssl=False)
result = r2.sentantLoad(definition)

# New features are opt-in:
config = Reality2Config(
    "localhost", 4005,
    max_retries=5,  # New feature
    timeout=60.0    # New feature
)
r2 = Reality2(config)
```

---

## Migration Guide

### No Changes Required
If you're using the basic Reality2 constructor, no changes needed:
```python
# This continues to work unchanged
r2 = Reality2("localhost", 4005, verify_ssl=False)
```

### Optional Enhancements

**Use config object for cleaner code:**
```python
# Before:
r2 = Reality2("production.example.com", 4005, True, True)

# After:
config = Reality2Config(
    domain_name="production.example.com",
    port=4005,
    ssl=True,
    verify_ssl=True
)
r2 = Reality2(config)
```

**Configure retry behavior:**
```python
# For unstable networks, increase retries:
r2 = Reality2(
    "remote-server.com",
    4005,
    max_retries=10,
    retry_backoff=2.0
)

# For local development, disable retries:
r2 = Reality2(
    "localhost",
    4005,
    max_retries=0  # No retries
)
```

**Use type hints in your code:**
```python
from typing import Dict, Any
from reality2 import Reality2

def load_my_sentant(r2: Reality2, definition: str) -> Dict[str, Any]:
    return r2.sentantLoad(definition)
```

---

## Testing

All new features have comprehensive test coverage:

```bash
# Test critical fixes (from v0.0.1)
python3 test_critical_fixes.py

# Test new features (v0.0.2)
python3 test_new_features.py
```

**Test Results:**
```
✓ Config Class
✓ Config Integration
✓ Retry Logic
✓ New Constructor Params
✓ Backward Compatibility

Total: All tests passing
```

---

## Performance Impact

**Type Hints:** Zero runtime overhead (annotations are only used by static analysis tools)

**Configuration Class:** Negligible (single object allocation)

**Retry Logic:**
- No overhead on successful requests
- Adds latency only on failures (which would fail anyway)
- Configurable - can be disabled with `max_retries=0`

---

## Synced Locations

The improved `reality2.py` has been synced to all locations:
- `client-python/reality2.py` (main version)
- `client-SBC/unihiker/reality2.py`
- `client-SBC/raspberry_pi/python/reality2.py`

---

## What's Next?

Potential future improvements (not yet implemented):
1. **GraphQL client library** - Use `gql` instead of string templates
2. **Pagination support** - Handle paginated queries automatically
3. **Async/await** - Non-blocking async version using `asyncio`
4. **Connection pooling** - Reuse HTTP connections for better performance
5. **Request batching** - Combine multiple GraphQL operations
6. **Schema introspection** - Auto-generate types from GraphQL schema

---

## Questions?

For issues or questions:
- Check the test files for working examples
- See `CRITICAL_FIXES.md` for the v0.0.1 improvements
- See `MIGRATION_GUIDE.md` for upgrade instructions

---

**Version:** 0.0.2
**Date:** 2026-01-08
**Author:** Roy Davies with Claude Sonnet 4.5
