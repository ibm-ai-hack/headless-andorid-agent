# BuckeyeBot — Unified OSU Student Agent

## Project Overview

A locally-hosted AI agent that unifies several endpoints used by Ohio State University students into a single SMS interface. Users text a Twilio phone number and the agent autonomously handles requests across campus services, food ordering, and academic tools.

**Core capabilities:**
- **Campus Services** — dining, bus tracking, parking, events, libraries, rec sports, and 50+ OSU APIs via the Ohio State MCP server
- **Food Ordering** — place Grubhub orders through Android emulation scripts
- **Academic Tools** — access BuckeyeLink services (scheduling, financial aid, grades) via browser automation
- **SMS Interface** — all interactions happen over text via Twilio

## Architecture

### Agent Layer — BeeAI Framework

Built on the **BeeAI Framework** (Linux Foundation) for multi-agent orchestration in Python.

- **Docs**: https://framework.beeai.dev
- **GitHub**: https://github.com/i-am-bee/beeai-framework

Use `RequirementAgent` as the default agent type with declarative rule-based constraints:

```python
from beeai_framework.agents.requirement import RequirementAgent
from beeai_framework.backend import ChatModel
from beeai_framework.memory import TokenMemory
```

Key conventions:
- Prefer `ChatModel.from_name()` for backend initialization
- Use `TokenMemory` for production; `UnconstrainedMemory` for prototyping
- Use `@tool` decorator for custom tools
- Wrap agent runs in `try/except FrameworkError`

### SMS Interface — Twilio

- **Twilio MCP Server** — `@twilio-alpha/mcp` provides SMS send/receive capabilities as MCP tools
- Users interact by texting the Twilio phone number
- Services loaded: `twilio_api_v2010`, `twilio_messaging_v1`

### Campus APIs — Ohio State MCP Server

The [ohio-state-mcp-server](https://mcpmarket.com/server/ohio-state) provides 50+ tools across 14 categories:

| Category | Key Tools |
|---|---|
| **Dining** | `get_dining_locations`, `get_dining_menu`, `get_dining_locations_with_menus` |
| **Bus Transportation** | `get_bus_routes`, `get_bus_stops`, `get_bus_vehicles` (real-time) |
| **Parking** | `get_parking_availability` (real-time garage availability) |
| **Classes** | `search_classes` (by keyword, subject, instructor) |
| **Campus Events** | `get_campus_events`, `search_campus_events`, `get_events_by_date_range` |
| **Libraries** | `get_library_locations`, `get_library_rooms`, `get_rooms_by_capacity` |
| **Rec Sports** | `get_recsports_facilities`, `get_facility_hours`, `get_facility_events` |
| **BuckID Merchants** | `get_buckid_merchants`, `get_merchants_with_meal_plan` |
| **Athletics** | `get_upcoming_games`, `search_sports` |
| **Buildings** | `get_buildings`, `search_buildings`, `find_room_type` |
| **Food Trucks** | `get_foodtruck_events`, `search_foodtrucks` |
| **Student Orgs** | `get_student_organizations`, `search_student_orgs` |
| **Calendar** | `get_academic_calendar`, `get_university_holidays` |
| **Directory** | `search_people` |

### Food Ordering — Grubhub via Android Emulation

Android emulation scripts to automate Grubhub ordering on behalf of the user. This handles the full order flow (restaurant selection, menu browsing, cart, checkout) through scripted UI interactions on an emulated Android device.

### Academic Tools — BuckeyeLink via Browser Automation

Browser automation (e.g., Playwright/Selenium) to access tools within http://buckeyelink.osu.edu/ including:
- Class scheduling and registration
- Financial aid status
- Grade and transcript access
- Student account and billing

## Environment

- Twilio credentials stored in `.env` (gitignored)
- MCP servers configured per-project in Claude Code's local config
- Ohio State MCP server: `ohio-state-mcp-server`
- BeeAI and LLM provider API keys in `.env`

### Required Environment Variables

```
# Twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# LLM Provider (pick one or more)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
# Or use local Ollama — no key needed
```

## Setup

1. Copy `.env.example` to `.env` and fill in credentials
2. Install Python dependencies: `pip install beeai-framework`
3. Install Node.js 20+ (for Twilio MCP server)
4. Install the Ohio State MCP server: `npx ohio-state-mcp-server` (or configure in MCP settings)
5. (Optional) Install Ollama and pull a model: `ollama pull granite3.3`
6. The Twilio MCP server starts automatically when Claude Code opens this project

## BeeAI Framework Quick Reference

### Agent Types

| Agent | When to Use |
|---|---|
| **RequirementAgent** | Default — declarative constraints, predictable execution (Python only) |
| **ReActAgent** | Fallback — classic reasoning + acting loop (Python & TypeScript) |

### Core Modules

| Module | Purpose |
|---|---|
| **Agents** | Core reasoning loop |
| **Backend** | Unified LLM provider interface (`ChatModel`) |
| **Tools** | Built-in + custom tools via `@tool` decorator |
| **Memory** | `TokenMemory` (production), `UnconstrainedMemory` (prototyping) |
| **Workflows** | Multi-agent orchestration via `@workflow.step()` |
| **Cache** | `SlidingCache`, `UnconstrainedCache` |
| **Errors** | `FrameworkError` hierarchy with `.explain()` |

### LLM Providers

```python
ChatModel.from_name("ollama:granite3.3")       # Local
ChatModel.from_name("anthropic:claude-sonnet-4") # Anthropic
ChatModel.from_name("openai:gpt-5-mini")        # OpenAI
ChatModel.from_name("watsonx:ibm/granite-3-8b-instruct")  # IBM watsonx
```

### Custom Tools

```python
from beeai_framework.tools import StringToolOutput, tool

@tool
def my_tool(param: str) -> StringToolOutput:
    """Tool description for the agent."""
    return StringToolOutput(result)
```

### Workflows (Multi-Agent)

```python
from beeai_framework.workflows import Workflow
from pydantic import BaseModel

class State(BaseModel):
    query: str
    result: str | None = None

workflow = Workflow(State)

@workflow.step()
async def handle(state: State) -> None:
    response = await agent.run(state.query)
    state.result = response.last_message.text
```

## Useful Commands

```bash
# Run the agent
uv run python main.py

# Start Ollama (if using local LLM)
ollama serve

# Install dependencies
pip install beeai-framework
npm install  # for Twilio MCP
```
