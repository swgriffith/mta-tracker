# NYC MTA Bus Tracker

A Python application that provides real-time arrival times for NYC MTA buses at any bus stop.

## Features

- Get real-time bus arrival predictions
- Filter by specific bus routes
- Display arrival times in minutes and stops away
- User-friendly command-line interface

## Prerequisites

- Python 3.7 or higher
- MTA Bus Time API key (free)

## Getting Your API Key

1. Visit [MTA Bus Time Developer Portal](https://bustime.mta.info/wiki/Developers/Index)
2. Register for a free API key
3. You'll receive your API key via email

## Installation

1. Clone this repository or download the files

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your API key as an environment variable:
```bash
export MTA_API_KEY=''
```

### Optional: Configure with Environment Variables

You can skip interactive prompts by setting these environment variables:

```bash
export MTA_STOP_ID='MTA_305804'           # Your bus stop ID
export MTA_ROUTE='B69'                     # Optional: filter by route
export MTA_REFRESH_INTERVAL='30'           # Optional: refresh interval in seconds
```

When these are set, the app will start monitoring immediately without prompting for input

## Usage

### Basic Usage

Run the application:
```bash
python mta_bus_tracker.py
```

You'll be prompted to enter:
1. A bus stop ID (e.g., `MTA_305423`)
2. Optional: A specific route to filter (e.g., `M15`)
3. Refresh interval in seconds (default: 30)

The app will continuously refresh and display updated arrival times. Press `Ctrl+C` to exit

### Finding Stop IDs

To find bus stop IDs:
1. Visit [MTA Bus Time](https://bustime.mta.info/)
2. Search for your stop
3. The stop ID will be in the URL or displayed on the page
4. Format: `MTA_` followed by the stop code (e.g., `MTA_305423`)

### Quick Start with Environment Variables

For automated/unattended monitoring, set all environment variables and run:

```bash
export MTA_API_KEY='your-api-key'
export MTA_STOP_ID='MTA_305423'
export MTA_ROUTE='M15'
export MTA_REFRESH_INTERVAL='30'
python mta_bus_tracker.py
```

### Using as a Module

You can also import and use the tracker in your own Python code:

```python
from mta_bus_tracker import MTABusTracker
import os

# Initialize tracker
api_key = os.environ.get("MTA_API_KEY")
tracker = MTABusTracker(api_key)

# Get arrivals for a stop
data = tracker.get_bus_arrivals("MTA_305423")
arrivals = tracker.parse_arrivals(data)

# Display formatted arrivals
tracker.display_arrivals("MTA_305423")

# Filter by specific route
tracker.display_arrivals("MTA_305423", line_ref="MTA NYCT_M15")

# Start continuous monitoring
tracker.monitor_arrivals("MTA_305423", line_ref="MTA NYCT_M15", refresh_interval=30)
```

## Example Output

```
=== NYC MTA Bus Tracker ===

Enter bus stop ID (e.g., MTA_305423): MTA_305423
Enter route to filter (e.g., M15) or press Enter for all routes: 
Enter refresh interval in seconds (default: 30): 

===========================================================================
=== NYC MTA Bus Tracker - Live Monitoring ===
===========================================================================

Monitoring stop: MTA_305423
===========================================================================

[Last updated: 2025-12-18 14:32:15]

Route      Bus Location                   Arriving In     Stops Away
--------------------------------------------------------------------
M15        2 stops away                   3 minutes       2
M15        4 stops away                   5 minutes       4
M15-SBS    6 stops away                   8 minutes       6
M15        10 stops away                  15 minutes      10

Refreshing in 30 seconds... (Press Ctrl+C to exit)
```

The display automatically refreshes at your specified interval and updates the arrival times in real-time

## API Reference

### MTABusTracker Class

#### `__init__(api_key: str)`
Initialize the tracker with your API key.

#### `get_bus_arrivals(stop_id: str, line_ref: Optional[str] = None) -> Dict`
Fetch raw arrival data from the MTA API.
- `stop_id`: MTA bus stop ID
- `line_ref`: Optional route filter (e.g., "MTA NYCT_M15")

#### `parse_arrivals(data: Dict) -> List[Dict]`
Parse API response into a readable format.

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
