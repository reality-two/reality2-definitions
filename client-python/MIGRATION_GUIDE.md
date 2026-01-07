# Migration Guide for Updated reality2.py

## TL;DR

If you're using the Reality2 Python client with **self-signed certificates** (development), you need to add `verify_ssl=False` when creating the client:

```python
# OLD (will now fail with SSL error)
r2 = Reality2("localhost", 4005)

# NEW (for self-signed certificates)
r2 = Reality2("localhost", 4005, verify_ssl=False)
```

**All provided loader scripts have already been updated** - no changes needed if you're using `load_sentant.py`, `load_swarm.py`, or the `./load` wrapper.

---

## What Changed?

### SSL Certificate Verification Now Enabled by Default

**Why:** Better security - prevents man-in-the-middle attacks

**Before:**
```python
# SSL verification was always disabled
requests.post(..., verify=False)  # Hardcoded
```

**After:**
```python
# SSL verification enabled by default, can be disabled
r2 = Reality2("localhost", 4005, ssl=True, verify_ssl=True)   # Default
r2 = Reality2("localhost", 4005, verify_ssl=False)            # Self-signed certs
```

---

## When to Use `verify_ssl=False`

### Development Environments ✓
- Local Reality2 node with self-signed certificate
- Testing on localhost
- Internal development servers

```python
r2 = Reality2("localhost", 4005, verify_ssl=False)
```

### Production Environments ✗
- Reality2 node with valid CA-signed certificate
- Public-facing servers
- Production deployments

```python
# Use default (verify_ssl=True)
r2 = Reality2("production.example.com", 4005)
```

---

## Updated Files

All example scripts have been updated to work with self-signed certificates:

### ✅ load_sentant.py
```python
r2_node = R2(host, port, verify_ssl=False)
```

### ✅ load_swarm.py
```python
r2_node = R2(host, port, verify_ssl=False)
```

### ✅ geospatial.py
```python
r2_node = R2(host, 4005, verify_ssl=False)
```

### ✅ iotdemo_stress_test.py
```python
r2_node = R2(host, 4005, verify_ssl=False)
```

---

## Example Usage

### Basic Connection (Self-Signed Cert)
```python
from reality2 import Reality2

# Connect to local node with self-signed certificate
r2 = Reality2("localhost", 4005, verify_ssl=False)

# Load a Sentant
with open('my_sentant.yaml') as f:
    definition = f.read()
result = r2.sentantLoad(definition)
print(result)
```

### With Context Manager (Automatic Cleanup)
```python
from reality2 import Reality2

# Context manager ensures cleanup even on errors
with Reality2("localhost", 4005, verify_ssl=False) as r2:
    result = r2.sentantLoad(definition)
    r2.sentantSend(result["sentantLoad"]["id"], "my_event", {})
# Automatically calls r2.close() here
```

### With Error Handling
```python
from reality2 import Reality2, Reality2ConnectionError, Reality2GraphQLError

try:
    with Reality2("localhost", 4005, verify_ssl=False) as r2:
        result = r2.sentantLoad(definition)
        print("Success:", result)
except Reality2ConnectionError as e:
    print(f"Connection failed: {e}")
except Reality2GraphQLError as e:
    print(f"GraphQL error: {e}")
```

---

## Error: SSL Certificate Verification Failed

If you see this error:

```
requests.exceptions.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
certificate verify failed: unable to get local issuer certificate
```

**Solution:** Add `verify_ssl=False` to your Reality2 client creation:

```python
r2 = Reality2("localhost", 4005, verify_ssl=False)
```

---

## Error: Reality2ConnectionError

If you see:

```
reality2.Reality2ConnectionError: Failed to connect to https://localhost:4005/reality2
```

**Possible causes:**
1. Reality2 node is not running
2. Wrong host or port
3. SSL certificate issue (add `verify_ssl=False`)
4. Network connectivity problem

**Debug steps:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now you'll see detailed error messages
r2 = Reality2("localhost", 4005, verify_ssl=False)
```

---

## Differences from Old Version

### Error Handling

**OLD:**
```python
# Returns empty dict on error - no way to know what failed
result = r2.sentantLoad(definition)
if result:
    print("Success")
else:
    print("Failed... but why?")
```

**NEW:**
```python
# Raises specific exceptions with error messages
try:
    result = r2.sentantLoad(definition)
    print("Success")
except Reality2ConnectionError as e:
    print(f"Connection failed: {e}")
except Reality2GraphQLError as e:
    print(f"GraphQL error: {e}")
```

### Resource Cleanup

**OLD:**
```python
r2 = Reality2("localhost", 4005)
# ... use r2 ...
r2.close()  # Often forgotten, incomplete cleanup
```

**NEW:**
```python
# Context manager ensures proper cleanup
with Reality2("localhost", 4005, verify_ssl=False) as r2:
    # ... use r2 ...
# Automatically closes all websockets and joins threads
```

### Logging

**OLD:**
```python
print(f"Joined: {server}")  # Uncontrolled output
```

**NEW:**
```python
import logging
logging.basicConfig(level=logging.INFO)  # You control log level

# Now library uses proper logging
# Set to DEBUG for verbose output, WARNING to suppress
```

---

## Testing Your Migration

### Quick Test
```bash
cd client-python
python3 -c "from reality2 import Reality2; r2 = Reality2('localhost', 4005, verify_ssl=False); print('✓ Connection configured')"
```

### Run Test Suite
```bash
python3 test_critical_fixes.py
```

Should output:
```
✓ PASS: Custom Exceptions
✓ PASS: Context Manager
✓ PASS: SSL Options
✓ PASS: Thread Safety
✓ PASS: Resource Tracking
Total: 5 passed, 0 failed
```

---

## Need Help?

### Common Questions

**Q: Do I need to change my existing scripts?**
A: Only if you create Reality2 clients directly. All provided loader scripts already updated.

**Q: Can I use the old code?**
A: The old `reality2.py` is replaced. Use `verify_ssl=False` for backward compatibility.

**Q: Will this work with production certificates?**
A: Yes! Remove `verify_ssl=False` and it will properly verify CA-signed certificates.

**Q: Why did you make this breaking change?**
A: Security best practice. SSL verification should be enabled by default, disabled only when needed.

---

## Summary Checklist

- [ ] Updated scripts to use `verify_ssl=False` (if using self-signed certs)
- [ ] Wrapped operations in try/except blocks for better error handling
- [ ] Consider using context managers (`with` statement) for automatic cleanup
- [ ] Enable logging to see detailed error messages during debugging
- [ ] Tested that existing functionality still works

---

For full technical details, see [CRITICAL_FIXES.md](CRITICAL_FIXES.md).
