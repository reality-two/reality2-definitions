# Bored API Bee Documentation

## Overview

The **Bored API Bee** is a Reality2 sentant that provides random activity suggestions when you're bored. It uses the free BoredAPI.com service to suggest fun things to do.

**No API key or registration required!**

---

## Features

- 🎲 Get random activity suggestions
- 🏷️ Filter activities by type (education, recreational, social, etc.)
- 👥 Filter by number of participants
- 💰 Get price level information (free to expensive)
- ♿ Accessibility ratings
- 🔗 Sometimes includes helpful links

---

## API Information

**Endpoint:** https://www.boredapi.com/api/activity

**Method:** GET

**Authentication:** None required

**Response Example:**
```json
{
  "activity": "Learn Express.js",
  "type": "education",
  "participants": 1,
  "price": 0.1,
  "link": "https://expressjs.com/",
  "key": "3943506",
  "accessibility": 0.1
}
```

---

## Usage

### Load the Bee

Using Python client:
```python
from reality2 import Reality2

with Reality2("localhost", 4005, verify_ssl=False) as r2:
    with open('bees/boredapi.bee.yaml', 'r') as f:
        bee_def = f.read()

    result = r2.sentantLoad(bee_def)
    sentant_id = result["sentantLoad"]["id"]
```

### Get Random Activity

Send the "Get Activity" event:
```python
r2.sentantSend(sentant_id, "Get Activity", {})
```

### Subscribe to Activity Suggestions

```python
def on_activity(data):
    signal = data["awaitSignal"]
    params = signal["parameters"]
    print(f"Activity: {params['activity']}")
    print(f"Type: {params['type']}")
    print(f"Participants: {params['participants']}")

r2.awaitSignal(sentant_id, "Activity Suggestion", on_activity)
```

### Filter by Type

Available types: `education`, `recreational`, `social`, `diy`, `charity`, `cooking`, `relaxation`, `music`, `busywork`

```python
r2.sentantSend(sentant_id, "Get Activity By Type", {
    "activity_type": "education"
})
```

### Filter by Participants

Get activities for a specific number of people:
```python
r2.sentantSend(sentant_id, "Get Activity By Participants", {
    "num_participants": 2
})
```

---

## Events

### Public Events (You Send)

| Event | Parameters | Description |
|-------|------------|-------------|
| `Get Activity` | None | Get a random activity |
| `Get Activity By Type` | `activity_type: string` | Filter by activity type |
| `Get Activity By Participants` | `num_participants: number` | Filter by number of participants |

### Signal Events (You Receive)

| Event | Parameters | Description |
|-------|------------|-------------|
| `Activity Suggestion` | `activity`, `type`, `participants`, `price`, `accessibility` | Activity suggestion with details |

---

## Response Fields

| Field | Type | Description | Range |
|-------|------|-------------|-------|
| `activity` | string | Description of the activity | - |
| `type` | string | Category of activity | education, recreational, etc. |
| `participants` | number | Number of people needed | 1-N |
| `price` | number | Cost level | 0.0 (free) to 1.0 (expensive) |
| `accessibility` | number | How accessible/easy | 0.0 (easy) to 1.0 (hard) |
| `link` | string | Optional helpful link | URL or empty |

---

## Example Activities

The Bored API can suggest activities like:

**Education:**
- "Learn Express.js"
- "Learn a new programming language"
- "Learn how to solder"

**Recreational:**
- "Go stargazing"
- "Compliment someone"
- "Take your dog on a walk"

**Social:**
- "Invite some friends over for a game night"
- "Host a potluck"
- "Organize a group hike"

**DIY:**
- "Organize your closet"
- "Rearrange your furniture"
- "Fix something that's broken"

**Relaxation:**
- "Take a bubble bath"
- "Meditate for 15 minutes"
- "Watch a classic movie"

---

## State Machine

```
Idle State
    ↓
[Get Activity] event
    ↓
Send request to BoredAPI
    ↓
[activity_response] event
    ↓
Extract activity details
    ↓
Signal "Activity Suggestion"
    ↓
Back to Idle
```

---

## Testing

Run the test script:
```bash
cd client-python
python3 test_boredapi.py
```

Expected output:
```
Testing Bored API Bee
✓ Connected to Reality2
✓ Loaded bee: Bored API
📡 Subscribing to activity suggestions...
🎲 Requesting random activity...
🎯 Activity Suggestion Received!
Activity: Learn Express.js
Type: education
Participants: 1
Price Level: 0.1
Accessibility: 0.1
```

---

## Swarm Ideas

This bee works great in swarms:

**1. Daily Motivation Swarm**
- Bored API (activity)
- Zenquote (inspiration)
- Weather API (plan outdoor activities)

**2. Social Planner**
- Bored API filtered by participants
- Calendar integration
- SMS notifications to friends

**3. Kids Activity Suggester**
- Bored API filtered by price=0 (free)
- Filter by type (educational, recreational)
- Generate QR codes for activity links

---

## Notes

- **Rate Limiting:** The API is free but please be respectful with request rates
- **No Authentication:** Perfect for demos and learning
- **Random Results:** Each call returns a different random activity
- **Reliable:** Well-maintained API with good uptime
- **Family Friendly:** All suggestions are appropriate for all ages

---

## Links

- **API Documentation:** https://www.boredapi.com/documentation
- **Website:** https://www.boredapi.com/
- **Source Code:** Open source API

---

## Version History

- **v1.0** (2026-01-08) - Initial release
  - Basic random activity support
  - Type filtering
  - Participant filtering

---

**Created:** 2026-01-08
**Author:** Reality2 Team
**License:** MIT
