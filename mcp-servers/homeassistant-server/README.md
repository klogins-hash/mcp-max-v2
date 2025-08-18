# Home Assistant MCP Server

Control your Home Assistant smart home devices through the MCP protocol.

## Features

- **Device Control**: Turn lights on/off, adjust thermostats, control switches
- **State Management**: Read and update entity states
- **Service Calls**: Execute any Home Assistant service
- **History**: Query historical data for any entity
- **Events**: Fire custom events and monitor the event bus
- **Configuration**: Access Home Assistant configuration
- **Logbook**: View logbook entries

## Setup

### 1. Get Your Home Assistant Token

1. Open Home Assistant web interface
2. Click on your profile (bottom left)
3. Scroll down to "Long-Lived Access Tokens"
4. Click "Create Token"
5. Give it a name (e.g., "MCP Server")
6. Copy the token - you'll need it for configuration

### 2. Install Dependencies

```bash
cd /Users/dp/CascadeProjects/mcp\ max\ v2/mcp-servers/homeassistant-server
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Set these environment variables:

```bash
export HOMEASSISTANT_URL="http://localhost:8123"  # Your HA URL
export HOMEASSISTANT_TOKEN="YOUR_LONG_LIVED_ACCESS_TOKEN"
```

### 4. Test the Server

```bash
python3 server.py
```

### 5. Register with MCP Hub

```bash
python3 register.py
```

## Available Tools

### `ha_get_states`
Get all entity states or filter by domain.

**Parameters:**
- `domain` (optional): Filter by domain (e.g., "light", "switch", "sensor")

**Example:**
```json
{
  "name": "ha_get_states",
  "arguments": {
    "domain": "light"
  }
}
```

### `ha_get_state`
Get the state of a specific entity.

**Parameters:**
- `entity_id` (required): Entity ID (e.g., "light.living_room")

**Example:**
```json
{
  "name": "ha_get_state",
  "arguments": {
    "entity_id": "light.living_room"
  }
}
```

### `ha_set_state`
Set the state of an entity.

**Parameters:**
- `entity_id` (required): Entity ID
- `state` (required): New state value
- `attributes` (optional): Additional attributes

**Example:**
```json
{
  "name": "ha_set_state",
  "arguments": {
    "entity_id": "input_boolean.vacation_mode",
    "state": "on"
  }
}
```

### `ha_call_service`
Call a Home Assistant service.

**Parameters:**
- `domain` (required): Service domain (e.g., "light", "switch")
- `service` (required): Service name (e.g., "turn_on", "toggle")
- `entity_id` (optional): Target entity ID(s)
- `service_data` (optional): Additional service data

**Example:**
```json
{
  "name": "ha_call_service",
  "arguments": {
    "domain": "light",
    "service": "turn_on",
    "entity_id": "light.living_room",
    "service_data": {
      "brightness": 255,
      "color_name": "blue"
    }
  }
}
```

### `ha_get_services`
List all available services.

**Parameters:**
- `domain` (optional): Filter by domain

### `ha_get_history`
Get entity state history.

**Parameters:**
- `entity_id` (required): Entity ID
- `start_time` (optional): Start time in ISO format
- `end_time` (optional): End time in ISO format

### `ha_get_config`
Get Home Assistant configuration.

### `ha_fire_event`
Fire a custom event.

**Parameters:**
- `event_type` (required): Event type name
- `event_data` (optional): Event data

### `ha_get_logbook`
Get logbook entries.

**Parameters:**
- `entity_id` (optional): Filter by entity
- `start_time` (optional): Start time in ISO format
- `end_time` (optional): End time in ISO format

## Common Use Cases

### Turn on all lights
```json
{
  "name": "ha_call_service",
  "arguments": {
    "domain": "light",
    "service": "turn_on",
    "entity_id": "all"
  }
}
```

### Set thermostat temperature
```json
{
  "name": "ha_call_service",
  "arguments": {
    "domain": "climate",
    "service": "set_temperature",
    "entity_id": "climate.living_room",
    "service_data": {
      "temperature": 72
    }
  }
}
```

### Activate a scene
```json
{
  "name": "ha_call_service",
  "arguments": {
    "domain": "scene",
    "service": "turn_on",
    "entity_id": "scene.movie_time"
  }
}
```

## Troubleshooting

1. **Connection refused**: Make sure Home Assistant is running and accessible
2. **401 Unauthorized**: Check your access token is correct
3. **Entity not found**: Verify the entity_id exists in your HA instance

## Security Notes

- Never commit your access token to version control
- Use environment variables or secure credential storage
- Consider using HTTPS if accessing HA remotely
- Tokens don't expire but can be revoked from HA interface
