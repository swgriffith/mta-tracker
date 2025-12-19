#!/usr/bin/env python3
"""
NYC MTA Bus and Train Arrival Time Tracker
Uses the MTA Bus Time API and GTFS-realtime API to get real-time arrival predictions.
"""

import requests
import json
from datetime import datetime
from typing import Optional, List, Dict
import os
import time
import sys
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'


class MTATrainTracker:
    """Track NYC MTA subway/train arrivals using the MTA GTFS-realtime API."""
    
    # Subway feed URLs
    FEED_URLS = {
        "1": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
        "2": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
        "3": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
        "4": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
        "5": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
        "6": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
        "7": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-7",
        "A": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
        "C": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
        "E": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
        "B": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
        "D": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
        "F": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
        "M": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
        "G": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g",
        "J": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
        "Z": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
        "N": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
        "Q": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
        "R": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
        "W": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
        "L": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l",
        "S": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si",
    }
    
    def __init__(self, api_key: str):
        """
        Initialize the MTA Train Tracker.
        
        Args:
            api_key: Your MTA API key from api.mta.info
        """
        self.api_key = api_key
    
    def get_train_arrivals(self, station_id: str, route: Optional[str] = None) -> List[Dict]:
        """
        Get train arrival times for a specific station.
        
        Args:
            station_id: The station ID (e.g., "127" for Times Square)
            route: Optional train route filter (e.g., "1", "2", "3")
        
        Returns:
            List of dictionaries containing arrival information
        """
        # Determine which feed to use
        if route and route.upper() in self.FEED_URLS:
            feed_url = self.FEED_URLS[route.upper()]
        else:
            # Use the main feed (1/2/3/4/5/6)
            feed_url = self.FEED_URLS["1"]
        
        headers = {"x-api-key": self.api_key}
        
        try:
            response = requests.get(feed_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse GTFS-realtime feed
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)
            
            arrivals = []
            now = datetime.now().timestamp()
            
            for entity in feed.entity:
                if entity.HasField('trip_update'):
                    trip = entity.trip_update.trip
                    trip_route = trip.route_id
                    
                    # Filter by route if specified
                    if route and trip_route != route.upper():
                        continue
                    
                    for stop_update in entity.trip_update.stop_time_update:
                        # Match station (remove direction suffix N/S)
                        stop_id = stop_update.stop_id.rstrip('NS')
                        
                        if stop_id == station_id:
                            if stop_update.HasField('arrival'):
                                arrival_time = stop_update.arrival.time
                            elif stop_update.HasField('departure'):
                                arrival_time = stop_update.departure.time
                            else:
                                continue
                            
                            minutes_away = int((arrival_time - now) / 60)
                            
                            # Only show upcoming trains
                            if minutes_away >= 0:
                                arrivals.append({
                                    "route": trip_route,
                                    "minutes_away": minutes_away,
                                    "arrival_time": arrival_time,
                                    "direction": "Uptown" if stop_update.stop_id.endswith("N") else "Downtown"
                                })
            
            # Sort by arrival time
            arrivals.sort(key=lambda x: x["arrival_time"])
            return arrivals
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching train data: {e}")
            return []
        except Exception as e:
            print(f"Error parsing train data: {e}")
            return []
    
    def display_arrivals(self, station_id: str, route: Optional[str] = None, show_header: bool = True):
        """
        Fetch and display train arrivals in a user-friendly format.
        
        Args:
            station_id: The station ID
            route: Optional train route filter
            show_header: Whether to show the fetching header message
        """
        if show_header:
            print(f"\nFetching arrivals for station {station_id}...")
            if route:
                print(f"Filtering for route: {route}")
        
        arrivals = self.get_train_arrivals(station_id, route)
        
        if not arrivals:
            print("No upcoming trains found.")
            return
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'Route':<10} {'Direction':<15} {'Arriving In':<15}{Colors.RESET}")
        print(Colors.CYAN + "-" * 40 + Colors.RESET)
        
        for arrival in arrivals[:10]:  # Show up to 10 trains
            route = f"{Colors.YELLOW}{arrival['route']}{Colors.RESET}"
            direction = arrival["direction"]
            
            if arrival["minutes_away"] <= 0:
                time_str = f"{Colors.RED}{Colors.BOLD}Arriving now{Colors.RESET}"
            elif arrival["minutes_away"] <= 5:
                time_str = f"{Colors.RED}{arrival['minutes_away']} minute{'s' if arrival['minutes_away'] != 1 else ''}{Colors.RESET}"
            elif arrival["minutes_away"] <= 10:
                time_str = f"{Colors.YELLOW}{arrival['minutes_away']} minutes{Colors.RESET}"
            else:
                time_str = f"{Colors.GREEN}{arrival['minutes_away']} minutes{Colors.RESET}"
            
            print(f"{route:<19} {direction:<15} {time_str:<24}")
    
    def monitor_arrivals(self, station_id: str, route: Optional[str] = None, refresh_interval: int = 30):
        """
        Continuously monitor and display train arrivals until interrupted.
        
        Args:
            station_id: The station ID
            route: Optional train route filter
            refresh_interval: Seconds between updates (default: 30)
        """
        def clear_screen():
            """Clear the terminal screen."""
            os.system('clear' if os.name == 'posix' else 'cls')
        
        print("\n" + Colors.CYAN + "="*75 + Colors.RESET)
        print(f"{Colors.BOLD}{Colors.BLUE}=== NYC MTA Train Tracker - Live Monitoring ==={Colors.RESET}")
        print(Colors.CYAN + "="*75 + Colors.RESET)
        print(f"{Colors.GREEN}Monitoring station: {Colors.BOLD}{station_id}{Colors.RESET}")
        if route:
            print(f"{Colors.GREEN}Route filter: {Colors.BOLD}{route}{Colors.RESET}")
        print(f"{Colors.GREEN}Refresh interval: {Colors.BOLD}{refresh_interval} seconds{Colors.RESET}")
        print(f"\n{Colors.RED}Press Ctrl+C to exit{Colors.RESET}")
        print(Colors.CYAN + "="*75 + Colors.RESET)
        
        try:
            while True:
                # Display current time
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n{Colors.CYAN}[Last updated: {Colors.BOLD}{current_time}{Colors.RESET}{Colors.CYAN}]{Colors.RESET}")
                
                # Get and display arrivals
                arrivals = self.get_train_arrivals(station_id, route)
                
                if not arrivals:
                    print("\nNo upcoming trains found.")
                else:
                    print(f"\n{Colors.BOLD}{Colors.CYAN}{'Route':<10} {'Direction':<15} {'Arriving In':<15}{Colors.RESET}")
                    print(Colors.CYAN + "-" * 40 + Colors.RESET)
                    
                    for arrival in arrivals[:10]:  # Show up to 10 trains
                        route_colored = f"{Colors.YELLOW}{arrival['route']}{Colors.RESET}"
                        direction = arrival["direction"]
                        
                        if arrival["minutes_away"] <= 0:
                            time_str = f"{Colors.RED}{Colors.BOLD}Arriving now{Colors.RESET}"
                        elif arrival["minutes_away"] <= 5:
                            time_str = f"{Colors.RED}{arrival['minutes_away']} minute{'s' if arrival['minutes_away'] != 1 else ''}{Colors.RESET}"
                        elif arrival["minutes_away"] <= 10:
                            time_str = f"{Colors.YELLOW}{arrival['minutes_away']} minutes{Colors.RESET}"
                        else:
                            time_str = f"{Colors.GREEN}{arrival['minutes_away']} minutes{Colors.RESET}"
                        
                        print(f"{route_colored:<19} {direction:<15} {time_str:<24}")
                
                print(f"\nRefreshing in {refresh_interval} seconds... (Press Ctrl+C to exit)")
                time.sleep(refresh_interval)
                clear_screen()
                
                # Reprint header after clear
                print("\n" + Colors.CYAN + "="*75 + Colors.RESET)
                print(f"{Colors.BOLD}{Colors.BLUE}=== NYC MTA Train Tracker - Live Monitoring ==={Colors.RESET}")
                print(Colors.CYAN + "="*75 + Colors.RESET)
                print(f"{Colors.GREEN}Monitoring station: {Colors.BOLD}{station_id}{Colors.RESET}")
                if route:
                    print(f"{Colors.GREEN}Route filter: {Colors.BOLD}{route}{Colors.RESET}")
                print(Colors.CYAN + "="*75 + Colors.RESET)
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Monitoring stopped. Goodbye!{Colors.RESET}")
            sys.exit(0)


class MTABusTracker:
    """Track NYC MTA bus arrivals using the MTA Bus Time API."""
    
    def __init__(self, api_key: str):
        """
        Initialize the MTA Bus Tracker.
        
        Args:
            api_key: Your MTA Bus Time API key
        """
        self.api_key = api_key
        self.base_url = "http://bustime.mta.info/api/siri/stop-monitoring.json"
    
    def get_bus_arrivals(self, stop_id: str, line_ref: Optional[str] = None) -> Dict:
        """
        Get bus arrival times for a specific stop.
        
        Args:
            stop_id: The MTA bus stop ID (e.g., "MTA_305423")
            line_ref: Optional bus route filter (e.g., "MTA NYCT_M15")
        
        Returns:
            Dictionary containing arrival information
        """
        params = {
            "key": self.api_key,
            "MonitoringRef": stop_id,
            "MaximumStopVisits": 10
        }
        
        if line_ref:
            params["LineRef"] = line_ref
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching bus data: {e}")
            return {}
    
    def parse_arrivals(self, data: Dict) -> List[Dict]:
        """
        Parse the API response into a readable format.
        
        Args:
            data: Raw API response data
        
        Returns:
            List of dictionaries containing parsed arrival information
        """
        arrivals = []
        
        try:
            stop_visits = data.get("Siri", {}).get("ServiceDelivery", {}).get("StopMonitoringDelivery", [{}])[0].get("MonitoredStopVisit", [])
            
            for visit in stop_visits:
                journey = visit.get("MonitoredVehicleJourney", {})
                
                # Get arrival time
                call = journey.get("MonitoredCall", {})
                expected_arrival = call.get("ExpectedArrivalTime")
                stops_away = call.get("Extensions", {}).get("Distances", {}).get("StopsFromCall", 0)
                
                # Get route info
                line_ref = journey.get("LineRef", "Unknown")
                
                # Get the bus's current location (where the bus actually is now)
                progress_status = journey.get("ProgressStatus", "")
                
                # The PresentableDistance shows where the bus currently is
                presentable_distance = call.get("Extensions", {}).get("Distances", {}).get("PresentableDistance", "")
                
                # Try to extract current location from various fields
                current_location = "Unknown"
                if presentable_distance:
                    current_location = presentable_distance
                elif progress_status:
                    current_location = progress_status
                else:
                    # Fallback to OriginRef or VehicleLocation
                    origin_ref = journey.get("OriginRef", "")
                    if origin_ref:
                        current_location = f"From {origin_ref}"
                
                # Calculate minutes until arrival
                minutes_away = None
                if expected_arrival:
                    arrival_time = datetime.fromisoformat(expected_arrival.replace("Z", "+00:00"))
                    now = datetime.now(arrival_time.tzinfo)
                    minutes_away = int((arrival_time - now).total_seconds() / 60)
                
                arrivals.append({
                    "route": line_ref.replace("MTA NYCT_", ""),
                    "current_location": current_location,
                    "minutes_away": minutes_away,
                    "stops_away": stops_away,
                    "expected_arrival": expected_arrival
                })
        
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error parsing arrival data: {e}")
        
        return arrivals
    
    def display_arrivals(self, stop_id: str, line_ref: Optional[str] = None, show_header: bool = True):
        """
        Fetch and display bus arrivals in a user-friendly format.
        
        Args:
            stop_id: The MTA bus stop ID
            line_ref: Optional bus route filter
            show_header: Whether to show the fetching header message
        """
        if show_header:
            print(f"\nFetching arrivals for stop {stop_id}...")
            if line_ref:
                print(f"Filtering for route: {line_ref}")
        
        data = self.get_bus_arrivals(stop_id, line_ref)
        arrivals = self.parse_arrivals(data)
        
        if not arrivals:
            print("No upcoming buses found.")
            return
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'Route':<10} {'Bus Location':<30} {'Arriving In':<15} {'Stops Away'}{Colors.RESET}")
        print(Colors.CYAN + "-" * 68 + Colors.RESET)
        
        for arrival in arrivals:
            # Skip rows with unknown arrival times
            if arrival["minutes_away"] is None:
                continue
                
            route = f"{Colors.YELLOW}{arrival['route']}{Colors.RESET}"
            current_location = arrival["current_location"][:28]
            
            if arrival["minutes_away"] <= 0:
                time_str = f"{Colors.RED}{Colors.BOLD}Arriving now{Colors.RESET}"
            elif arrival["minutes_away"] <= 5:
                time_str = f"{Colors.RED}{arrival['minutes_away']} minute{'s' if arrival['minutes_away'] != 1 else ''}{Colors.RESET}"
            elif arrival["minutes_away"] <= 10:
                time_str = f"{Colors.YELLOW}{arrival['minutes_away']} minutes{Colors.RESET}"
            else:
                time_str = f"{Colors.GREEN}{arrival['minutes_away']} minutes{Colors.RESET}"
            
            stops = arrival["stops_away"] or "Unknown"
            stops_colored = f"{Colors.MAGENTA}{stops}{Colors.RESET}"
            
            print(f"{route:<19} {current_location:<30} {time_str:<24} {stops_colored}")
    
    def monitor_arrivals(self, stop_id: str, line_ref: Optional[str] = None, refresh_interval: int = 30):
        """
        Continuously monitor and display bus arrivals until interrupted.
        
        Args:
            stop_id: The MTA bus stop ID
            line_ref: Optional bus route filter
            refresh_interval: Seconds between updates (default: 30)
        """
        def clear_screen():
            """Clear the terminal screen."""
            os.system('clear' if os.name == 'posix' else 'cls')
        
        print("\n" + Colors.CYAN + "="*75 + Colors.RESET)
        print(f"{Colors.BOLD}{Colors.BLUE}=== NYC MTA Bus Tracker - Live Monitoring ==={Colors.RESET}")
        print(Colors.CYAN + "="*75 + Colors.RESET)
        print(f"{Colors.GREEN}Monitoring stop: {Colors.BOLD}{stop_id}{Colors.RESET}")
        if line_ref:
            print(f"{Colors.GREEN}Route filter: {Colors.BOLD}{line_ref.replace('MTA NYCT_', '')}{Colors.RESET}")
        print(f"{Colors.GREEN}Refresh interval: {Colors.BOLD}{refresh_interval} seconds{Colors.RESET}")
        print(f"\n{Colors.RED}Press Ctrl+C to exit{Colors.RESET}")
        print(Colors.CYAN + "="*75 + Colors.RESET)
        
        try:
            while True:
                # Display current time
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n{Colors.CYAN}[Last updated: {Colors.BOLD}{current_time}{Colors.RESET}{Colors.CYAN}]{Colors.RESET}")
                
                # Get and display arrivals
                data = self.get_bus_arrivals(stop_id, line_ref)
                arrivals = self.parse_arrivals(data)
                
                if not arrivals:
                    print("\nNo upcoming buses found.")
                else:
                    print(f"\n{Colors.BOLD}{Colors.CYAN}{'Route':<10} {'Bus Location':<30} {'Arriving In':<15} {'Stops Away'}{Colors.RESET}")
                    print(Colors.CYAN + "-" * 68 + Colors.RESET)
                    
                    for arrival in arrivals:
                        # Skip rows with unknown arrival times
                        if arrival["minutes_away"] is None:
                            continue
                            
                        route = f"{Colors.YELLOW}{arrival['route']}{Colors.RESET}"
                        current_location = arrival["current_location"][:28]
                        
                        if arrival["minutes_away"] <= 0:
                            time_str = f"{Colors.RED}{Colors.BOLD}Arriving now{Colors.RESET}"
                        elif arrival["minutes_away"] <= 5:
                            time_str = f"{Colors.RED}{arrival['minutes_away']} minute{'s' if arrival['minutes_away'] != 1 else ''}{Colors.RESET}"
                        elif arrival["minutes_away"] <= 10:
                            time_str = f"{Colors.YELLOW}{arrival['minutes_away']} minutes{Colors.RESET}"
                        else:
                            time_str = f"{Colors.GREEN}{arrival['minutes_away']} minutes{Colors.RESET}"
                        
                        stops = arrival["stops_away"] or "Unknown"
                        stops_colored = f"{Colors.MAGENTA}{stops}{Colors.RESET}"
                        
                        print(f"{route:<19} {current_location:<30} {time_str:<24} {stops_colored}")
                
                print(f"\nRefreshing in {refresh_interval} seconds... (Press Ctrl+C to exit)")
                time.sleep(refresh_interval)
                clear_screen()
                
                # Reprint header after clear
                print("\n" + Colors.CYAN + "="*75 + Colors.RESET)
                print(f"{Colors.BOLD}{Colors.BLUE}=== NYC MTA Bus Tracker - Live Monitoring ==={Colors.RESET}")
                print(Colors.CYAN + "="*75 + Colors.RESET)
                print(f"{Colors.GREEN}Monitoring stop: {Colors.BOLD}{stop_id}{Colors.RESET}")
                if line_ref:
                    print(f"{Colors.GREEN}Route filter: {Colors.BOLD}{line_ref.replace('MTA NYCT_', '')}{Colors.RESET}")
                print(Colors.CYAN + "="*75 + Colors.RESET)
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Monitoring stopped. Goodbye!{Colors.RESET}")
            sys.exit(0)


def main():
    """Main function to run the MTA Tracker."""
    
    print(f"{Colors.BOLD}{Colors.BLUE}=== NYC MTA Bus & Train Tracker ==={Colors.RESET}")
    
    # Setup Bus Tracker
    bus_tracker = None
    bus_stop_id = None
    bus_line_ref = None
    
    bus_api_key = os.environ.get("MTA_BUS_API_KEY") or os.environ.get("MTA_API_KEY")
    bus_stop_id = os.environ.get("MTA_STOP_ID")
    bus_stop_name = os.environ.get("MTA_STOP_NAME")
    bus_route = os.environ.get("MTA_ROUTE")
    
    if bus_api_key and bus_stop_id:
        bus_tracker = MTABusTracker(bus_api_key)
        bus_line_ref = f"MTA NYCT_{bus_route}" if bus_route else None
        stop_display = bus_stop_name if bus_stop_name else bus_stop_id
        print(f"{Colors.GREEN}✓ Bus tracking enabled: {stop_display}" + (f", Route {bus_route}" if bus_route else "") + f"{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠ Bus tracking disabled (set MTA_BUS_API_KEY and MTA_STOP_ID in .env to enable){Colors.RESET}")
    
    # Setup Train Tracker
    train_tracker = None
    train_station_id = None
    train_route = None
    
    train_api_key = os.environ.get("MTA_TRAIN_API_KEY") or os.environ.get("MTA_API_KEY")
    train_station_id = os.environ.get("MTA_TRAIN_STATION_ID")
    train_station_name = os.environ.get("MTA_TRAIN_STATION_NAME")
    train_route = os.environ.get("MTA_TRAIN_ROUTE")
    
    if train_api_key and train_station_id:
        train_tracker = MTATrainTracker(train_api_key)
        train_route = train_route.upper() if train_route else None
        station_display = train_station_name if train_station_name else train_station_id
        print(f"{Colors.GREEN}✓ Train tracking enabled: {station_display}" + (f", Route {train_route}" if train_route else "") + f"{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠ Train tracking disabled (set MTA_TRAIN_API_KEY and MTA_TRAIN_STATION_ID in .env to enable){Colors.RESET}")
    
    # Check if at least one tracker is configured
    if not bus_tracker and not train_tracker:
        print(f"\n{Colors.RED}Error: No trackers configured!{Colors.RESET}")
        print("Please set the required environment variables in your .env file:")
        print("  - For buses: MTA_BUS_API_KEY (or MTA_API_KEY) and MTA_STOP_ID")
        print("  - For trains: MTA_TRAIN_API_KEY (or MTA_API_KEY) and MTA_TRAIN_STATION_ID")
        return
    
    # Get refresh interval
    refresh_env = os.environ.get("MTA_REFRESH_INTERVAL")
    if refresh_env:
        try:
            refresh_interval = int(refresh_env)
            if refresh_interval < 5:
                print("Minimum refresh interval is 5 seconds. Using 5 seconds.")
                refresh_interval = 5
        except ValueError:
            print(f"Invalid MTA_REFRESH_INTERVAL value: {refresh_env}. Using default 30 seconds.")
            refresh_interval = 30
    else:
        refresh_interval = 30
    
    # Get max trains to display
    max_trains = 10  # default
    max_trains_env = os.environ.get("MTA_MAX_TRAINS")
    if max_trains_env:
        try:
            max_trains = int(max_trains_env)
            if max_trains < 1:
                max_trains = 10
        except ValueError:
            print(f"{Colors.YELLOW}Invalid MTA_MAX_TRAINS value: {max_trains_env}. Using default 10.{Colors.RESET}")
            max_trains = 10
    
    # Get max buses to display
    max_buses = 10  # default
    max_buses_env = os.environ.get("MTA_MAX_BUSES")
    if max_buses_env:
        try:
            max_buses = int(max_buses_env)
            if max_buses < 1:
                max_buses = 10
        except ValueError:
            print(f"{Colors.YELLOW}Invalid MTA_MAX_BUSES value: {max_buses_env}. Using default 10.{Colors.RESET}")
            max_buses = 10
    
    print(f"{Colors.GREEN}Refresh interval: {refresh_interval} seconds{Colors.RESET}")
    print(f"\n{Colors.RED}Press Ctrl+C to exit{Colors.RESET}")
    
    # Start continuous monitoring of both
    def clear_screen():
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    try:
        while True:
            time.sleep(0.5)  # Small delay before first display
            clear_screen()
            
            # Header
            print("\n" + Colors.CYAN + "="*75 + Colors.RESET)
            print(f"{Colors.BOLD}{Colors.BLUE}=== NYC MTA Bus & Train Tracker - Live Monitoring ==={Colors.RESET}")
            print(Colors.CYAN + "="*75 + Colors.RESET)
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{Colors.CYAN}[Last updated: {Colors.BOLD}{current_time}{Colors.RESET}{Colors.CYAN}]{Colors.RESET}")
            
            # Display Bus Info
            if bus_tracker:
                stop_display = bus_stop_name if bus_stop_name else bus_stop_id
                print(f"\n{Colors.BOLD}{Colors.MAGENTA}🚌 BUS ARRIVALS - {stop_display}" + (f" - Route {bus_route}" if bus_route else "") + f"{Colors.RESET}")
                print(Colors.CYAN + "-" * 75 + Colors.RESET)
                
                bus_data = bus_tracker.get_bus_arrivals(bus_stop_id, bus_line_ref)
                bus_arrivals = bus_tracker.parse_arrivals(bus_data)
                
                if not bus_arrivals:
                    print(f"{Colors.YELLOW}No upcoming buses found.{Colors.RESET}")
                else:
                    print(f"{Colors.BOLD}{Colors.CYAN}{'Route':<10} {'Bus Location':<30} {'Arriving In':<15} {'Stops Away'}{Colors.RESET}")
                    print(Colors.CYAN + "-" * 68 + Colors.RESET)
                    
                    count = 0
                    for arrival in bus_arrivals:
                        if arrival["minutes_away"] is None:
                            continue
                        
                        if count >= max_buses:
                            break
                            
                        route_colored = f"{Colors.YELLOW}{arrival['route']}{Colors.RESET}"
                        current_location = arrival["current_location"][:28]
                        
                        if arrival["minutes_away"] <= 0:
                            time_str = f"{Colors.RED}{Colors.BOLD}Arriving now{Colors.RESET}"
                        elif arrival["minutes_away"] <= 5:
                            time_str = f"{Colors.RED}{arrival['minutes_away']} minute{'s' if arrival['minutes_away'] != 1 else ''}{Colors.RESET}"
                        elif arrival["minutes_away"] <= 10:
                            time_str = f"{Colors.YELLOW}{arrival['minutes_away']} minutes{Colors.RESET}"
                        else:
                            time_str = f"{Colors.GREEN}{arrival['minutes_away']} minutes{Colors.RESET}"
                        
                        stops = arrival["stops_away"] or "Unknown"
                        stops_colored = f"{Colors.MAGENTA}{stops}{Colors.RESET}"
                        
                        print(f"{route_colored:<19} {current_location:<30} {time_str:<24} {stops_colored}")
                        count += 1
            
            # Display Train Info
            if train_tracker:
                station_display = train_station_name if train_station_name else train_station_id
                print(f"\n{Colors.BOLD}{Colors.MAGENTA}🚇 TRAIN ARRIVALS - {station_display}" + (f" - Route {train_route}" if train_route else "") + f"{Colors.RESET}")
                print(Colors.CYAN + "-" * 75 + Colors.RESET)
                
                train_arrivals = train_tracker.get_train_arrivals(train_station_id, train_route)
                
                if not train_arrivals:
                    print(f"{Colors.YELLOW}No upcoming trains found.{Colors.RESET}")
                else:
                    print(f"{Colors.BOLD}{Colors.CYAN}{'Route':<10} {'Direction':<15} {'Arriving In':<15}{Colors.RESET}")
                    print(Colors.CYAN + "-" * 40 + Colors.RESET)
                    
                    for arrival in train_arrivals[:max_trains]:
                        route_colored = f"{Colors.YELLOW}{arrival['route']}{Colors.RESET}"
                        direction = arrival["direction"]
                        
                        if arrival["minutes_away"] <= 0:
                            time_str = f"{Colors.RED}{Colors.BOLD}Arriving now{Colors.RESET}"
                        elif arrival["minutes_away"] <= 5:
                            time_str = f"{Colors.RED}{arrival['minutes_away']} minute{'s' if arrival['minutes_away'] != 1 else ''}{Colors.RESET}"
                        elif arrival["minutes_away"] <= 10:
                            time_str = f"{Colors.YELLOW}{arrival['minutes_away']} minutes{Colors.RESET}"
                        else:
                            time_str = f"{Colors.GREEN}{arrival['minutes_away']} minutes{Colors.RESET}"
                        
                        print(f"{route_colored:<19} {direction:<15} {time_str:<24}")
            
            print(f"\n{Colors.CYAN}Refreshing in {refresh_interval} seconds... (Press Ctrl+C to exit){Colors.RESET}")
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Monitoring stopped. Goodbye!{Colors.RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
