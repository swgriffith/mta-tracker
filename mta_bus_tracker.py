#!/usr/bin/env python3
"""
NYC MTA Bus Arrival Time Tracker
Uses the MTA Bus Time API to get real-time bus arrival predictions.
"""

import requests
import json
from datetime import datetime
from typing import Optional, List, Dict
import os
import time
import sys

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
                # Try to get from ProgressStatus or OriginRef/ProgressRate
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
                    # Fallbaclocation": current_locationOriginRef or VehicleLocation
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
    """Main function to run the MTA Bus Tracker."""
    
    # Get API key from environment variable
    api_key = os.environ.get("MTA_API_KEY")
    
    if not api_key:
        print("Error: MTA_API_KEY environment variable not set.")
        print("Get your API key from: https://bustime.mta.info/wiki/Developers/Index")
        print("\nSet it with: export MTA_API_KEY='your-api-key-here'")
        return
    
    tracker = MTABusTracker(api_key)
    
    # Example usage
    print(f"{Colors.BOLD}{Colors.BLUE}=== NYC MTA Bus Tracker ==={Colors.RESET}")
    
    # Get stop ID from environment variable or prompt
    stop_id = os.environ.get("MTA_STOP_ID")
    if stop_id:
        print(f"\nUsing stop ID from environment: {stop_id}")
    else:
        stop_id = input("\nEnter bus stop ID (e.g., MTA_305423): ").strip()
        if not stop_id:
            print("No stop ID provided. Using example: MTA_305423")
            stop_id = "MTA_305423"
    
    # Get route from environment variable or prompt
    route = os.environ.get("MTA_ROUTE")
    if route:
        print(f"Using route filter from environment: {route}")
        line_ref = f"MTA NYCT_{route}"
    else:
        route = input("Enter route to filter (e.g., M15) or press Enter for all routes: ").strip()
        line_ref = f"MTA NYCT_{route}" if route else None
    
    # Get refresh interval from environment variable or prompt
    refresh_env = os.environ.get("MTA_REFRESH_INTERVAL")
    if refresh_env:
        try:
            refresh_interval = int(refresh_env)
            if refresh_interval < 5:
                print("Minimum refresh interval is 5 seconds. Using 5 seconds.")
                refresh_interval = 5
            else:
                print(f"Using refresh interval from environment: {refresh_interval} seconds")
        except ValueError:
            print(f"Invalid MTA_REFRESH_INTERVAL value: {refresh_env}. Using default 30 seconds.")
            refresh_interval = 30
    else:
        refresh_input = input("Enter refresh interval in seconds (default: 30): ").strip()
        try:
            refresh_interval = int(refresh_input) if refresh_input else 30
            if refresh_interval < 5:
                print("Minimum refresh interval is 5 seconds. Using 5 seconds.")
                refresh_interval = 5
        except ValueError:
            print("Invalid input. Using default 30 seconds.")
            refresh_interval = 30
    
    # Start continuous monitoring
    tracker.monitor_arrivals(stop_id, line_ref, refresh_interval)


if __name__ == "__main__":
    main()
