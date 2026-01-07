# Changelog - Reality2 Python Client

## Version 0.0.2 (2026-01-08) - Critical Fixes & Improvements

### 🔒 Security Improvements

**SSL Certificate Verification Now Enabled by Default**
- **Before:** SSL verification was globally disabled for all requests
- **After:** SSL verification enabled by default, can be disabled per-client
- **Migration:** Add `verify_ssl=False` parameter for self-signed certificates
- **Impact:** Better security, prevents MITM attacks in production

```python
# For development with self-signed certificates
r2 = Reality2("localhost", 4005, verify_ssl=False)

# For production with valid certificates
r2 = Reality2("production.example.com", 4005)  # verify_ssl=True is default
```

### 🐛 Bug Fixes

**1. Proper Exception Handling**
- **Fixed:** Bare `except:` clauses that caught all exceptions including KeyboardInterrupt
- **Fixed:** Silent failures returning empty dicts
- **Added:** Specific exception classes for different error types
- **Added:** Proper error messages with context

```python
# New exception hierarchy
Reality2Error (base)
├── Reality2ConnectionError
├── Reality2TimeoutError
├── Reality2ResponseError
└── Reality2GraphQLError
```

**2. Thread Safety**
- **Fixed:** Race conditions in subscription management
- **Added:** Thread locks for all shared data structures
- **Fixed:** Proper tracking of threads, event flags, and websockets

**3. Resource Cleanup**
- **Fixed:** Websockets not being closed on shutdown
- **Fixed:** Threads not being joined properly
- **Added:** Timeout-based cleanup to prevent hanging
- **Added:** Context manager support for automatic cleanup

```python
# Automatic cleanup with context manager
with Reality2("localhost", 4005, verify_ssl=False) as r2:
    r2.sentantLoad(definition)
# All resources automatically cleaned up here
```

**4. Error Handling in Loader Scripts**
- **Fixed:** Scripts now handle non-existent Sentants gracefully
- **Fixed:** Unload operations before load don't crash if Sentant doesn't exist
- **Added:** Better error messages showing what failed and why

### ✨ New Features

**1. Logging System**
- Replaced `print()` statements with proper logging
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- Better debugging capabilities

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # See all details

# Or suppress most messages
logging.basicConfig(level=logging.WARNING)
```

**2. Context Manager Support**
```python
with Reality2("localhost", 4005, verify_ssl=False) as r2:
    sentant = r2.sentantLoad(definition)
    # Use r2...
# Automatic cleanup on exit
```

**3. Named Daemon Threads**
- All threads now have descriptive names for easier debugging
- Format: `Reality2-{sentant_id[:8]}-{signal}`

**4. Better Error Messages**
- URLs included in connection errors
- GraphQL errors show full context
- Exception chaining shows root cause

### 📝 API Changes

**Constructor**
```python
# New parameter: verify_ssl
Reality2(domain_name, port, ssl=True, verify_ssl=True)
```

**close() Method**
```python
# New parameter: timeout
r2.close(timeout=5.0)  # Wait up to 5 seconds for threads
```

**Error Handling**
```python
# Before: Returns {} on error
result = r2.sentantLoad(definition)
if result:
    print("Success")

# After: Raises specific exceptions
try:
    result = r2.sentantLoad(definition)
    print("Success")
except Reality2GraphQLError as e:
    print(f"GraphQL error: {e}")
except Reality2ConnectionError as e:
    print(f"Connection failed: {e}")
```

### 🔧 Files Modified

- **reality2.py** - Core library with all critical fixes
- **load_sentant.py** - Updated for error handling and verify_ssl
- **load_swarm.py** - Updated for error handling and verify_ssl
- **geospatial.py** - Updated for verify_ssl
- **iotdemo_stress_test.py** - Updated for verify_ssl

### 📚 New Files

- **test_critical_fixes.py** - Test suite for critical fixes
- **test_error_handling.py** - Test suite for error handling
- **CRITICAL_FIXES.md** - Technical documentation
- **MIGRATION_GUIDE.md** - User-friendly migration guide
- **CHANGELOG.md** - This file

### ⚠️ Breaking Changes

1. **Methods now raise exceptions instead of returning `{}`**
   - Wrap calls in try/except blocks for error handling
   - See MIGRATION_GUIDE.md for examples

2. **SSL verification enabled by default**
   - Add `verify_ssl=False` for self-signed certificates
   - All included scripts already updated

### ✅ Testing

All tests pass:
```bash
python3 test_critical_fixes.py   # 5 passed, 0 failed
python3 test_error_handling.py   # 2 passed, 0 failed
```

### 📖 Documentation

- **CRITICAL_FIXES.md** - Detailed technical documentation of all fixes
- **MIGRATION_GUIDE.md** - Step-by-step migration guide with examples
- **CHANGELOG.md** - This changelog

### 🙏 Backward Compatibility

Scripts using the provided loaders (`load`, `load_sentant.py`, `load_swarm.py`) will continue to work without modification.

Custom scripts need minor updates:
1. Add `verify_ssl=False` if using self-signed certificates
2. Add try/except blocks for better error handling (recommended)

### 🚀 Performance Improvements

- More efficient resource management
- Proper thread cleanup prevents resource leaks
- Daemon threads don't block shutdown

### 🔍 Debugging Improvements

- All errors now logged with context
- Full exception chaining for root cause analysis
- Named threads for easier debugging
- Configurable log levels

---

## Version 0.0.1 (2024) - Initial Release

Initial Reality2 Python client implementation.
