# NYC MTA Bus & Train Tracker

A Python application that provides real-time arrival times for NYC MTA buses and subway trains.

## Features

- **Simultaneous tracking** of both buses and trains
- Real-time arrival predictions with color-coded timing
- Filter by specific routes for both buses and trains
- Display arrival times in minutes with stops away (buses) and direction (trains)
- Human-friendly location aliases
- Configurable display limits
- User-friendly command-line interface with auto-refresh

## Prerequisites

- Python 3.7 or higher
- MTA API keys (free):
  - Bus tracking: MTA Bus Time API key
  - Train tracking: MTA GTFS-realtime API key

## Getting Your API Keys

### For Bus Tracking
1. Visit [MTA Bus Time Developer Portal](https://bustime.mta.info/wiki/Developers/Index)
2. Register for a free API key
3. You'll receive your API key via email

### For Train Tracking
1. Visit [MTA API Portal](https://api.mta.info/)
2. Sign up for a free account
3. Get your API key from the dashboard

## Installation

1. Clone this repository or download the files

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables in a `.env` file (or export them):
```bash
# API Keys
export MTA_API_KEY='your-api-key'              # Used as fallback for both
export MTA_BUS_API_KEY='your-bus-api-key'      # Optional: specific bus API key
export MTA_TRAIN_API_KEY='your-train-api-key'  # Optional: specific train API key

# Bus Configuration
export MTA_STOP_ID='MTA_305804'                # Your bus stop ID
export MTA_STOP_NAME='DeKalb Ave & Flatbush'   # Optional: human-friendly name
export MTA_ROUTE='B69'                         # Optional: filter by route

# Train Configuration
export MTA_TRAIN_STATION_ID='D25'              # Station ID
export MTA_TRAIN_STATION_NAME='DeKalb Avenue'  # Optional: human-friendly name
export MTA_TRAIN_ROUTE='Q'                     # Optional: filter by route

# Common Configuration
export MTA_REFRESH_INTERVAL='30'               # Refresh interval in seconds
export MTA_MAX_TRAINS='10'                     # Max trains to display
export MTA_MAX_BUSES='10'                      # Max buses to display
```

## Usage

### Basic Usage

Run the application:
```bash
python mta_bus_tracker.py
```

The app will automatically track whatever you've configured in your environment variables:
- **Both** buses and trains if both are configured
- **Only buses** if only bus variables are set
- **Only trains** if only train variables are set

The app will continuously refresh and display updated arrival times. Press `Ctrl+C` to exit.

### Finding Stop/Station IDs

#### For Bus Stops
1. Visit [MTA Bus Time](https://bustime.mta.info/)
2. Search for your stop
3. The stop ID will be in the URL or displayed on the page
4. Format: `MTA_` followed by the stop code (e.g., `MTA_305423`)

#### For Train Stations
1. Visit [MTA GTFS Data](https://api.mta.info/)
2. Look up station IDs in the static GTFS feed
3. Station IDs are typically 3-4 characters (e.g., `127` for Times Square, `D25` for DeKalb Ave)
4. Note: Some stations may have direction suffixes (N/S) which are handled automatically

### Using as a Module

You can also import and use the trackers in your own Python code:

```python
from mta_bus_tracker import MTABusTracker, MTATrainTracker
import os

# Initialize bus tracker
bus_api_key = os.environ.get("MTA_BUS_API_KEY")
bus_tracker = MTABusTracker(bus_api_key)

# Get bus arrivals
bus_data = bus_tracker.get_bus_arrivals("MTA_305423")
bus_arrivals = bus_tracker.parse_arrivals(bus_data)

# Display formatted bus arrivals
bus_tracker.display_arrivals("MTA_305423")

# Filter by specific route
bus_tracker.display_arrivals("MTA_305423", line_ref="MTA NYCT_M15")

# Initialize train tracker
train_api_key = os.environ.get("MTA_TRAIN_API_KEY")
train_tracker = MTATrainTracker(train_api_key)

# Get train arrivals
train_arrivals = train_tracker.get_train_arrivals("127", route="1")

# Display formatted train arrivals
train_tracker.display_arrivals("127", route="1")

# Start continuous monitoring
bus_tracker.monitor_arrivals("MTA_305423", line_ref="MTA NYCT_M15", refresh_interval=30)
train_tracker.monitor_arrivals("127", route="1", refresh_interval=30)
```

## Example Output

```
=== NYC MTA Bus & Train Tracker ===

✓ Bus tracking enabled: DeKalb Ave & Flatbush, Route B69
✓ Train tracking enabled: DeKalb Avenue, Route Q
Refresh interval: 30 seconds

Press Ctrl+C to exit

===========================================================================
=== NYC MTA Bus & Train Tracker - Live Monitoring ===
===========================================================================

[Last updated: 2025-12-19 16:45:23]

🚌 BUS ARRIVALS - DeKalb Ave & Flatbush - Route B69
---------------------------------------------------------------------------
Route      Bus Location                   Arriving In     Stops Away
--------------------------------------------------------------------
B69        approaching                    Arriving now    0
B69        2 stops away                   3 minutes       2
B69        at Fulton St                   5 minutes       4
B69        6 stops away                   8 minutes       6

🚇 TRAIN ARRIVALS - DeKalb Avenue - Route Q
---------------------------------------------------------------------------
Route      Direction       Arriving In
----------------------------------------
Q          Uptown          2 minutes
Q          Downtown        4 minutes
Q          Uptown          7 minutes
Q          Downtown        11 minutes

Refreshing in 30 seconds... (Press Ctrl+C to exit)
```bus tracker with your API key.

#### `get_bus_arrivals(stop_id: str, line_ref: Optional[str] = None) -> Dict`
Fetch raw arrival data from the MTA Bus Time API.
- `stop_id`: MTA bus stop ID (e.g., "MTA_305423")
- `line_ref`: Optional route filter (e.g., "MTA NYCT_M15")

#### `parse_arrivals(data: Dict) -> List[Dict]`
Parse API response into a readable format with route, location, arrival time, and stops away.

#### `display_arrivals(stop_id: str, line_ref: Optional[str] = None, show_header: bool = True)`
Fetch and display bus arrivals in a formatted table.

#### `monitor_arrivals(stop_id: str, line_ref: Optional[str] = None, refresh_interval: int = 30)`
Continuously monitor and display bus arrivals with automatic refresh until interrupted (Ctrl+C).

### MTATrainTracker Class

#### `__iNo trackers configured**
- Make sure you've set at least one set of tracker credentials in your environment variables
- For buses: Set `MTA_BUS_API_KEY` (or `MTA_API_KEY`) and `MTA_STOP_ID`
- For trains: Set `MTA_TRAIN_API_KEY` (or `MTA_API_KEY`) and `MTA_TRAIN_STATION_ID`

**Error: MTA_API_KEY environment variable not set**
- Make sure you've set the environment variable: `export MTA_API_KEY='your-key'`
- Or set specific keys: `MTA_BUS_API_KEY` and `MTA_TRAIN_API_KEY`
- To make it permanent, add it to your `~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`

**No upcoming buses/trains found**
- Verify the stop/station ID is correct
- Check if service is currently running (service hours, planned work)
- The stop/station might not have upcoming arrivals at this time

**Import error: google.transit**
- Make sure you've installed all dependencies: `pip install -r requirements.txt`
- The `gtfs-realtime-bindings` package is required for train tracking

**Request timeout or connection errors**
- Check your internet connection
- The MTA API might be temporarily unavailable
- Try again in a few moments

## Configuration Tips

- **Human-friendly names**: Use `MTA_STOP_NAME` and `MTA_TRAIN_STATION_NAME` to display readable location names instead of IDs
- **Display limits**: Use `MTA_MAX_TRAINS` and `MTA_MAX_BUSES` to control how many arrivals are shown (useful for small terminal windows)
- **Shared API key**: If your API key works for both buses and trains, just set `MTA_API_KEY` once
- **Track only what you need**: Set only the environment variables for buses or trains if you don't need both

## Notes

- Arrival times are predictions and may change due to traffic and operational conditions
- The APIs update in real-time but may have occasional delays
- Some stops/stations may not have real-time tracking available
- Train direction (Uptown/Downtown) is determined by the stop ID suffix (N/S)
- Bus arrivals show current bus location when
#### `display_arrivals(stop_id: str, line_ref: Optional[str] = None, show_header: bool = True)`
Fetch and display arrivals in a formatted table.

#### `monitor_arrivals(stop_id: str, line_ref: Optional[str] = None, refresh_interval: int = 30)`
Continuously monitor and display bus arrivals with automatic refresh until interrupted (Ctrl+C).

## Troubleshooting

**Error: MTA_API_KEY environment variable not set**
- Make sure you've set the environment variable: `export MTA_API_KEY='your-key'`
- To make it permanent, add it to your `~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`

**No upcoming buses found**
- Verify the stop ID is correct
- Check if buses are currently running (service hours)
- The stop might not have upcoming arrivals at this time

**Request timeout or connection errors**
- Check your internet connection
- The MTA API might be temporarily unavailable
- Try again in a few moments

## Notes

- Arrival times are predictions and may change due to traffic conditions
- The API updates in real-time but may have occasional delays
- Some stops may not have real-time tracking available

## License

MIT
