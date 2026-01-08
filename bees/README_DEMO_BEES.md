# Demo Bees for Reality2 Sentant System

This collection of demo bees showcases the capabilities of the Reality2 Sentant system by integrating with various free, public APIs. All these bees require no authentication and demonstrate different patterns of API integration.

## Name Intelligence Bees

### Agify
**File**: `agify.bee.yaml`
**API**: https://api.agify.io
**Purpose**: Predicts age from a person's name

**Public Events**:
- `Predict Age` - Accepts a `name` parameter

**Signals**:
- `Age Prediction` - Returns:
  - `name`: The analyzed name
  - `age`: Predicted age
  - `count`: Number of data points used in prediction

**Example Use Case**: Demographic analysis, user profiling, name research

---

### Genderize
**File**: `genderize.bee.yaml`
**API**: https://api.genderize.io
**Purpose**: Predicts gender from a person's name

**Public Events**:
- `Predict Gender` - Accepts a `name` parameter

**Signals**:
- `Gender Prediction` - Returns:
  - `name`: The analyzed name
  - `gender`: Predicted gender (male/female)
  - `probability`: Confidence level (0-1)
  - `count`: Number of data points used

**Example Use Case**: Personalization, demographic analysis, name research

---

### Nationalize
**File**: `nationalize.bee.yaml`
**API**: https://api.nationalize.io
**Purpose**: Predicts nationality from a person's name

**Public Events**:
- `Predict Nationality` - Accepts a `name` parameter

**Signals**:
- `Nationality Prediction` - Returns:
  - `name`: The analyzed name
  - `country_id`: Most likely country code (e.g., "US", "GB")
  - `probability`: Confidence level (0-1)

**Example Use Case**: Demographic analysis, localization, name origin research

---

## Life Coaching & Inspiration Bees

### Bored API
**File**: `boredapi.bee.yaml`
**API**: https://www.boredapi.com
**Purpose**: Suggests random activities when you're bored

**Public Events**:
- `Get Activity` - Get any random activity
- `Get Activity By Type` - Filter by type (education, recreational, social, etc.)
- `Get Activity By Participants` - Filter by number of participants

**Signals**:
- `Activity Suggestion` - Returns:
  - `activity`: Description of the activity
  - `type`: Category of activity
  - `participants`: Suggested number of participants
  - `price`: Cost estimate (0-1 scale)
  - `accessibility`: How accessible it is (0-1 scale)

**Example Use Case**: Lifestyle apps, boredom relief, activity planning

---

### Advice Slip
**File**: `adviceslip.bee.yaml`
**API**: https://api.adviceslip.com
**Purpose**: Provides random pieces of advice

**Public Events**:
- `Get Advice` - Get a random piece of advice

**Signals**:
- `Advice Received` - Returns:
  - `id`: Unique advice ID
  - `advice`: The advice text

**Example Use Case**: Daily motivation, decision support, wisdom sharing

---

### Quotable
**File**: `quotable.bee.yaml`
**API**: https://api.quotable.io
**Purpose**: Provides random inspirational quotes

**Public Events**:
- `Get Quote` - Get a random inspirational quote

**Signals**:
- `Quote Received` - Returns:
  - `id`: Unique quote ID
  - `quote`: The quote text
  - `author`: Author of the quote
  - `tags`: Array of topic tags

**Example Use Case**: Inspiration apps, daily quotes, motivational content

---

### JokeAPI
**File**: `jokeapi.bee.yaml`
**API**: https://v2.jokeapi.dev
**Purpose**: Provides random jokes

**Public Events**:
- `Get Joke` - Get a random safe joke

**Signals**:
- `Joke Received` - Returns:
  - `id`: Unique joke ID
  - `joke`: The joke text
  - `category`: Category (Programming, Misc, Pun, etc.)
  - `safe`: Whether the joke is work-safe

**Example Use Case**: Entertainment apps, mood lifting, social engagement

---

## Information & Knowledge Bees

### Numbers API
**File**: `numbersapi.bee.yaml`
**API**: http://numbersapi.com
**Purpose**: Provides interesting trivia facts about numbers

**Public Events**:
- `Get Number Fact` - Get a fact about a specific number (accepts `number` parameter)
- `Get Random Number Fact` - Get a fact about a random number

**Signals**:
- `Number Fact Received` - Returns:
  - `number`: The number (or "random")
  - `fact`: Interesting fact about the number

**Example Use Case**: Educational apps, trivia, number exploration

---

### REST Countries
**File**: `restcountries.bee.yaml`
**API**: https://restcountries.com
**Purpose**: Provides comprehensive information about countries

**Public Events**:
- `Get Country Info` - Accepts a `country` parameter (name or code)

**Signals**:
- `Country Info Received` - Returns:
  - `name`: Common country name
  - `official_name`: Official country name
  - `capital`: Capital city
  - `region`: Geographic region
  - `subregion`: Geographic subregion
  - `population`: Population count
  - `area`: Area in km²
  - `flag`: Flag emoji

**Example Use Case**: Geography apps, travel planning, educational tools

---

## Swarms

### Name Intelligence Swarm
**File**: `swarms/name_intelligence.swarm.yaml`
**Combines**: Agify + Genderize + Nationalize
**Purpose**: Comprehensive name analysis

This swarm coordinates all three name prediction services to provide a complete demographic profile from a single name.

**Public Events**:
- `Analyze Name` - Accepts a `name` parameter

**Signals**:
- `Analysis Started` - Indicates analysis has begun
- `Complete Name Analysis` - Returns combined results:
  - All age prediction data
  - All gender prediction data
  - All nationality prediction data

**Architecture**: Uses a coordinator sentant that:
1. Dispatches requests to all three bees in parallel
2. Collects responses from each service
3. Combines results into a unified response
4. Demonstrates parallel processing and data aggregation

---

### Life Coach Swarm
**File**: `swarms/life_coach.swarm.yaml`
**Combines**: Bored API + Advice Slip + Quotable
**Purpose**: Comprehensive life coaching and motivation

This swarm provides a complete motivational package combining activity suggestions, practical advice, and inspirational quotes.

**Public Events**:
- `Get Life Coaching` - No parameters needed

**Signals**:
- `Coaching Session Started` - Indicates session has begun
- `Complete Life Coaching` - Returns combined results:
  - Activity suggestion with type and participants
  - Practical advice
  - Inspirational quote with author

**Architecture**: Uses a coordinator sentant that:
1. Requests data from all three inspiration sources
2. Collects and aggregates responses
3. Provides a unified coaching experience
4. Demonstrates swarm coordination patterns

---

## Integration Patterns

These demo bees demonstrate several important Reality2 patterns:

### 1. Simple API Integration
- Basic GET requests to public APIs
- JSON response parsing with JSONPath
- Signal emission with structured data

### 2. Parameter Handling
- Optional parameters (activity type, participants)
- Required parameters (name, country)
- Default values (random number)

### 3. Swarm Coordination
- Parallel API calls
- Response aggregation
- Completion detection
- Unified result presentation

### 4. Error Handling
- Graceful degradation
- API response validation
- Data extraction patterns

---

## Testing

Each bee can be tested individually using the Python client:

```python
from reality2 import Reality2

r2 = Reality2("localhost", 4005, ssl=False)

# Test Name Intelligence
r2.sentantLoad("Agify", "agify")
r2.sentantSend("Agify", "Predict Age", {"name": "Michael"})

# Test Life Coach
r2.swarmLoad("Life Coach", "life_coach")
r2.sentantSend("Coach Coordinator", "Get Life Coaching", {})

# Subscribe to signals
for signal in r2.awaitSignal("Agify"):
    print(f"Received: {signal}")
```

---

## API Rate Limits

Most of these APIs have free tier rate limits:
- **Agify, Genderize, Nationalize**: 1000 requests/day
- **Bored API**: Unlimited
- **Advice Slip**: Unlimited
- **Quotable**: Unlimited
- **JokeAPI**: Unlimited
- **Numbers API**: Unlimited
- **REST Countries**: Unlimited

For production use, consider caching responses and implementing rate limiting in your application.

---

## Contributing

When adding new demo bees:
1. Choose APIs that require no authentication
2. Focus on text-based responses (avoid images for now)
3. Document all public events and signals
4. Update the appropriate `info.json` file
5. Follow the established naming patterns
6. Provide clear use case descriptions

---

## Resources

- [Reality2 Documentation](http://roycdavies.github.io)
- [Python Client Library](../client-python/README.md)
- [Antenna Development Guide](../antennae/README.md)
- [Swarm Patterns](../swarms/README.md)
