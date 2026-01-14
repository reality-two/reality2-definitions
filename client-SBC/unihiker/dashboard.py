# ****************************************************************************************************
# Reality2 Dashboard for Unihiker
# Roy C. Davies, 2024
#
# A visual dashboard that:
# - Starts and manages the Reality2 server
# - Displays network visualization with connected nodes
# - Lists sentants with their locations
# - Supports touch interaction to view and send events
# - Integrates sensor readings
# ****************************************************************************************************
from unihiker import GUI
import time
import math
import os
from pinpong.board import *
from pinpong.extension.unihiker import *
import subprocess
import threading
import ifaddr
import ssl
import json
import requests
import urllib3

from reality2 import Reality2
from fsm import *

# ====================================================================================================
# Configuration
# ====================================================================================================

def find_reality2_installation():
    """
    Dynamically find the Reality2 installation directory.
    Searches common locations and returns (reality2_dir, reality2_cmd) tuple.
    """
    # Check environment variable first
    env_path = os.environ.get('REALITY2_HOME')
    if env_path and os.path.isfile(os.path.join(env_path, 'run')):
        return env_path.rstrip('/') + '/', os.path.join(env_path, 'run')

    # Common installation paths to search
    search_paths = [
        # Unihiker paths
        "/root/aarch64_GNU_Linux_dev/reality2",
        "/root/aarch64_GNU_Linux/reality2",
        "/root/reality2/aarch64_GNU_Linux_dev/reality2",
        "/root/reality2/aarch64_GNU_Linux/reality2",
        # Arduino UNO-Q paths
        "/home/arduino/reality2/aarch64_GNU_Linux_dev/reality2",
        "/home/arduino/reality2/aarch64_GNU_Linux/reality2",
        # Raspberry Pi paths
        "/home/pi/reality2/aarch64_GNU_Linux_dev/reality2",
        "/home/pi/reality2/aarch64_GNU_Linux/reality2",
        # Generic paths
        "/opt/reality2",
        os.path.expanduser("~/reality2/aarch64_GNU_Linux_dev/reality2"),
        os.path.expanduser("~/reality2/aarch64_GNU_Linux/reality2"),
    ]

    for path in search_paths:
        run_script = os.path.join(path, 'run')
        if os.path.isfile(run_script):
            print(f"Found Reality2 at: {path}")
            return path.rstrip('/') + '/', run_script

    # If not found, try to find it dynamically
    try:
        result = subprocess.run(
            ['find', '/root', '/home', '-name', 'run', '-path', '*/reality2/*', '-type', 'f'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            run_path = result.stdout.strip().split('\n')[0]
            dir_path = os.path.dirname(run_path)
            print(f"Found Reality2 at: {dir_path}")
            return dir_path.rstrip('/') + '/', run_path
    except Exception as e:
        print(f"Search failed: {e}")

    # Fallback to default (will fail if not found, but gives clear error)
    print("Warning: Reality2 installation not found, using default path")
    return "/root/aarch64_GNU_Linux_dev/reality2/", "/root/aarch64_GNU_Linux_dev/reality2/run"

# Find Reality2 installation
reality2_dir, reality2_cmd = find_reality2_installation()
REFRESH_INTERVAL = 2  # seconds
SENSOR_INTERVAL = 5   # seconds

# ====================================================================================================
# Global State
# ====================================================================================================
running = True
r2 = None
gui = GUI()

# Data stores
nodes_data = []       # List of connected nodes
sentants_data = []    # List of all sentants
mesh_info = {}        # Mesh network status
selected_sentant = None
selected_sentant_events = []

# GUI element references
status_text = None
node_count_text = None
sentant_count_text = None
sentant_list_elements = []
sentant_buttons = []  # Persistent button pool for sentant list
sentant_header = None
event_buttons = []
sensor_value_text = None
network_elements = []
events_status_text = None
elements_initialized = False

# Display mode: "main", "events", "sensors"
display_mode = "main"

# Scroll position for sentant list
scroll_offset = 0
MAX_VISIBLE_SENTANTS = 8  # 2 columns x 4 rows

# ====================================================================================================
# FSM Setup
# ====================================================================================================
DashboardFSM = Automation()

# ====================================================================================================
# Utility Functions
# ====================================================================================================

def get_ip_address():
    """Get the IP address of this device."""
    ipaddr = ""
    adapters = ifaddr.get_adapters()

    for adapter in adapters:
        if "wlan0" in adapter.nice_name:
            for ip in adapter.ips:
                if ip.is_IPv4:
                    ipaddr = ip.ip

    if ipaddr == "":
        for adapter in adapters:
            if "p2p0" in adapter.nice_name:
                for ip in adapter.ips:
                    if ip.is_IPv4:
                        ipaddr = ip.ip

    return ipaddr if ipaddr else "No Network"

def check_r2_running(_):
    """Check if Reality2 Node is running."""
    processes = subprocess.run(["ps", "-e"], capture_output=True)
    return "beam.smp" in str(processes.stdout)

def get_mesh_info():
    """Query mesh network status from /mesh/info endpoint."""
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        response = requests.get(
            "https://localhost:4005/mesh/info",
            verify=False,
            timeout=2
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {}

# ====================================================================================================
# Drawing Functions
# ====================================================================================================

def draw_header():
    """Draw the dashboard header."""
    global status_text, node_count_text, sentant_count_text

    # Header background
    gui.fill_rect(x=0, y=0, w=240, h=35, color="#1a1a2e")

    # Title
    gui.draw_text(x=120, y=4, text="Reality2 Dashboard", origin="n",
                  font_size=10, color="white")

    # Status indicator
    status_text = gui.draw_text(x=120, y=18, text="Starting...", origin="n",
                                font_size=8, color="white")

# Persistent network viz elements
net_center_node = None
net_center_label = None
net_ble_indicator = None
net_wifi_indicator = None
net_hotspot_indicator = None
net_nodes_count = None
net_state_label = None
net_initialized = False

def init_network_viz():
    """Initialize the network visualization elements once."""
    global net_center_node, net_center_label, net_ble_indicator, net_wifi_indicator
    global net_hotspot_indicator, net_nodes_count, net_state_label, net_initialized

    center_x = 120
    center_y = 72

    # Center node
    net_center_node = gui.fill_circle(x=center_x, y=center_y, r=16, color="#4CAF50")
    net_center_label = gui.draw_text(x=center_x, y=center_y, text="R2", origin="center",
                                     font_size=6, color="white")

    # Status indicators
    net_ble_indicator = gui.fill_circle(x=12, y=42, r=4, color="#666666")
    gui.draw_text(x=20, y=42, text="BLE", origin="w", font_size=6, color="white")

    net_wifi_indicator = gui.fill_circle(x=12, y=54, r=4, color="#666666")
    gui.draw_text(x=20, y=54, text="WiFi", origin="w", font_size=6, color="white")

    net_hotspot_indicator = gui.fill_circle(x=12, y=66, r=4, color="#666666")
    gui.draw_text(x=20, y=66, text="AP", origin="w", font_size=6, color="white")

    # Node count box
    gui.fill_rect(x=185, y=40, w=50, h=30, color="#333333")
    gui.draw_text(x=210, y=46, text="Nodes", origin="center", font_size=6, color="white")
    net_nodes_count = gui.draw_text(x=210, y=60, text="0", origin="center", font_size=12, color="white")

    # Mesh state
    net_state_label = gui.draw_text(x=120, y=112, text="Unknown", origin="center", font_size=7, color="white")

    net_initialized = True

def update_network_viz():
    """Update the network visualization without recreating elements."""
    global net_center_node, net_center_label, net_ble_indicator, net_wifi_indicator
    global net_hotspot_indicator, net_nodes_count, net_state_label, mesh_info, nodes_data

    # Get mesh status
    mesh_state = mesh_info.get("mesh_info", {}).get("state", "unknown")
    is_hosting = mesh_info.get("mesh_info", {}).get("hosting", False)
    ble_available = mesh_info.get("capabilities", {}).get("bluetooth", False)
    wifi_available = mesh_info.get("capabilities", {}).get("wifi_mesh", False)

    # Update center node color and label
    if is_hosting:
        node_color = "#FF9800"
        node_label = "HOST"
    elif mesh_state == "connected_as_client":
        node_color = "#2196F3"
        node_label = "CLIENT"
    else:
        node_color = "#4CAF50"
        node_label = "R2"

    if net_center_node:
        net_center_node.config(color=node_color)
    if net_center_label:
        net_center_label.config(text=node_label)

    # Update status indicators
    if net_ble_indicator:
        net_ble_indicator.config(color="#4CAF50" if ble_available else "#666666")
    if net_wifi_indicator:
        net_wifi_indicator.config(color="#4CAF50" if wifi_available else "#666666")
    if net_hotspot_indicator:
        net_hotspot_indicator.config(color="#FF9800" if is_hosting else "#666666")

    # Update node count
    num_nodes = len(nodes_data)
    if net_nodes_count:
        net_nodes_count.config(text=str(num_nodes))

    # Update mesh state
    state_text = mesh_state.replace("_", " ").title() if mesh_state else "Unknown"
    if net_state_label:
        net_state_label.config(text=state_text)

def draw_network_viz():
    """Draw or update the network visualization."""
    global net_initialized

    if not net_initialized:
        init_network_viz()

    update_network_viz()

def init_sentant_list():
    """Initialize the sentant list elements once."""
    global sentant_buttons, sentant_header, sentant_list_elements

    list_start_y = 120
    col_width = 115
    row_height = 30
    cols = 2
    rows = 4
    max_visible = cols * rows

    # Section header background
    header_bg = gui.fill_rect(x=0, y=list_start_y, w=240, h=16, color="#2d2d44")
    sentant_list_elements.append(header_bg)

    # Section header text
    sentant_header = gui.draw_text(x=10, y=list_start_y + 8,
                                   text="Sentants (0)",
                                   origin="w", font_size=8, color="white")
    sentant_list_elements.append(sentant_header)

    # Create button pool for sentants (8 buttons, initially hidden)
    sentant_buttons = []
    for i in range(max_visible):
        row = i // cols
        col = i % cols
        x_pos = 60 + (col * col_width)
        y_pos = list_start_y + 20 + (row * row_height) + row_height // 2

        btn = gui.add_button(x=-100, y=-100, w=col_width - 5, h=row_height - 2,
                             text="", origin="center",
                             onclick=lambda idx=i: select_sentant_by_button(idx))
        sentant_buttons.append(btn)

def select_sentant_by_button(button_index):
    """Handle sentant selection via button pool."""
    global scroll_offset
    actual_index = scroll_offset + button_index
    select_sentant(actual_index)

def update_sentant_list():
    """Update the sentant list without recreating elements."""
    global sentant_buttons, sentant_header, sentants_data, scroll_offset

    list_start_y = 120
    col_width = 115
    row_height = 30
    cols = 2

    # Update header text
    if sentant_header:
        sentant_header.config(text=f"Sentants ({len(sentants_data)})")

    # Update visible sentant buttons
    max_visible = len(sentant_buttons)
    visible_sentants = sentants_data[scroll_offset:scroll_offset + max_visible]

    for i, btn in enumerate(sentant_buttons):
        if i < len(visible_sentants):
            sentant = visible_sentants[i]
            name = sentant.get("name", "Unknown")[:12]
            row = i // cols
            col = i % cols
            x_pos = 60 + (col * col_width)
            y_pos = list_start_y + 20 + (row * row_height) + row_height // 2
            btn.config(x=x_pos, y=y_pos, text=name)
        else:
            # Hide unused buttons
            btn.config(x=-100, y=-100)

def draw_sentant_list():
    """Draw or update the sentant list."""
    global elements_initialized, sentant_buttons

    if not sentant_buttons:
        init_sentant_list()

    update_sentant_list()

def draw_sensor_panel():
    """Draw the sensor readings panel."""
    global sensor_value_text

    # Sensor area: y=250 to y=280 (moved down for more viz space)
    panel_y = 250

    gui.fill_rect(x=0, y=panel_y, w=240, h=30, color="#1a1a2e")
    gui.draw_text(x=10, y=panel_y + 15, text="Light:", origin="w",
                  font_size=8, color="white")

    sensor_value_text = gui.draw_text(x=48, y=panel_y + 15, text="--",
                                       origin="w", font_size=8, color="#4CAF50")

    # Sensor toggle button - taller for proper text centering
    gui.add_button(x=205, y=panel_y + 15, w=50, h=28, text="Read",
                   origin="center", onclick=trigger_sensor_read)

def draw_control_buttons():
    """Draw control buttons at bottom."""
    # Bottom bar: y=280 to y=320 (40px)
    btn_y = 280
    btn_h = 28

    # Background for button area
    gui.fill_rect(x=0, y=btn_y, w=240, h=40, color="#1a1a2e")

    # Position buttons near bottom of screen (2 buttons, evenly spaced)
    gui.add_button(x=70, y=300, w=80, h=btn_h, text="Refresh",
                   origin="center", onclick=trigger_refresh)

    gui.add_button(x=170, y=300, w=80, h=btn_h, text="Stop",
                   origin="center", onclick=trigger_stop)

def draw_events_panel():
    """Draw the events panel for selected sentant."""
    global event_buttons, selected_sentant, selected_sentant_events
    global net_initialized, sentant_buttons, sentant_header

    # Clear previous event buttons
    for elem in event_buttons:
        try:
            elem.config(x=-100, y=-100)
        except:
            pass
    event_buttons = []

    if selected_sentant is None:
        return

    # Clear the entire screen - this destroys all elements
    gui.clear()

    # Reset persistent element flags so they get recreated on return
    net_initialized = False
    sentant_buttons = []
    sentant_header = None

    # Full screen background
    bg = gui.fill_rect(x=0, y=0, w=240, h=320, color="#1a1a2e")
    event_buttons.append(bg)

    # Header background
    header_bg = gui.fill_rect(x=0, y=0, w=240, h=50, color="#2d2d44")
    event_buttons.append(header_bg)

    # Header with sentant name
    sentant_name = selected_sentant.get("name", "Unknown")
    title = gui.draw_text(x=120, y=15, text=f"Events: {sentant_name[:15]}",
                          origin="n", font_size=9, color="white")
    event_buttons.append(title)

    # Back button
    back_btn = gui.add_button(x=35, y=35, w=55, h=28, text="Back",
                              origin="center", onclick=show_main_mode)
    event_buttons.append(back_btn)

    # Draw event buttons in 2-column grid
    if selected_sentant_events:
        for i, event in enumerate(selected_sentant_events[:8]):
            row = i // 2
            col = i % 2
            x_pos = 65 + (col * 110)  # Center x position
            y_pos = 90 + (row * 45)   # Center y position
            btn_h = 35

            event_name = event.get("event", event) if isinstance(event, dict) else str(event)
            event_name = event_name[:12]  # Truncate

            btn = gui.add_button(x=x_pos, y=y_pos, w=100, h=btn_h,
                                 text=event_name, origin="center",
                                 onclick=lambda e=event: send_event(e))
            event_buttons.append(btn)
    else:
        no_events = gui.draw_text(x=120, y=150, text="no events",
                                  origin="center", font_size=9, color="white")
        event_buttons.append(no_events)

    # Status text for event feedback (at bottom) - always shown
    global events_status_text
    events_status_text = gui.draw_text(x=120, y=300, text="Tap an event to send",
                                       origin="center", font_size=8, color="white")
    event_buttons.append(events_status_text)

# ====================================================================================================
# Event Handlers
# ====================================================================================================

def scroll_up():
    global scroll_offset
    if scroll_offset > 0:
        scroll_offset -= 1
        draw_sentant_list()

def scroll_down():
    global scroll_offset, sentants_data
    if scroll_offset + MAX_VISIBLE_SENTANTS < len(sentants_data):
        scroll_offset += 1
        draw_sentant_list()

def select_sentant(index):
    """Handle sentant selection."""
    global selected_sentant, selected_sentant_events, sentants_data, display_mode

    if 0 <= index < len(sentants_data):
        selected_sentant = sentants_data[index]
        # Try to get events from sentant definition
        selected_sentant_events = extract_events_from_sentant(selected_sentant)
        display_mode = "events"
        draw_events_panel()

def extract_events_from_sentant(sentant):
    """Extract sendable events from a sentant's events list (from GraphQL)."""
    events = []

    # Get events directly from the sentant data (fetched via GraphQL)
    sentant_events = sentant.get("events", [])

    for event_data in sentant_events:
        if isinstance(event_data, dict):
            event_name = event_data.get("event", "")
            if event_name and not event_name.startswith("_"):
                events.append(event_data)
        elif isinstance(event_data, str):
            if not event_data.startswith("_"):
                events.append({"event": event_data, "parameters": {}})

    # If no events found, return empty list (no defaults)
    return events

def send_event(event):
    """Send an event to the selected sentant."""
    global r2, selected_sentant, events_status_text

    print(f"[send_event] Called with event: {event}")

    if r2 is None:
        print("[send_event] r2 is None")
        if events_status_text:
            events_status_text.config(text="Not connected")
        return

    if selected_sentant is None:
        print("[send_event] selected_sentant is None")
        if events_status_text:
            events_status_text.config(text="No sentant selected")
        return

    try:
        event_name = event.get("event", event) if isinstance(event, dict) else str(event)
        sentant_name = selected_sentant.get("name", "")
        sentant_id = selected_sentant.get("id", "")

        # Use name if available, otherwise ID
        sentant_path = sentant_name if sentant_name else sentant_id

        print(f"[send_event] Sending '{event_name}' to path '{sentant_path}'")

        if sentant_path:
            result = r2.sentantSend(path=sentant_path, event=event_name, parameters={})
            print(f"[send_event] Result: {result}")
            if events_status_text:
                events_status_text.config(text=f"Sent: {event_name}")
        else:
            print("[send_event] No sentant path")
            if events_status_text:
                events_status_text.config(text="No sentant path")
    except Exception as e:
        print(f"[send_event] Exception: {e}")
        print(f"[send_event] Full error: {repr(e)}")
        if events_status_text:
            # Show more of the error message
            error_msg = str(e)
            if len(error_msg) > 30:
                error_msg = error_msg[:27] + "..."
            events_status_text.config(text=f"Error: {error_msg}")

def show_main_mode():
    """Switch back to main view."""
    global display_mode
    display_mode = "main"
    draw_main_screen()

def show_events_mode():
    """Switch to events mode."""
    global display_mode, selected_sentant, sentants_data

    if sentants_data and selected_sentant is None:
        selected_sentant = sentants_data[0]
        selected_sentant_events = extract_events_from_sentant(selected_sentant)

    if selected_sentant:
        display_mode = "events"
        draw_events_panel()

def trigger_refresh():
    """Trigger a data refresh."""
    global DashboardFSM
    DashboardFSM.event("refresh")

def trigger_sensor_read():
    """Trigger a sensor reading."""
    global DashboardFSM
    DashboardFSM.event("read_sensor")

def trigger_stop():
    """Trigger shutdown."""
    global DashboardFSM
    DashboardFSM.event("stop")

def draw_main_screen():
    """Draw the complete main screen."""
    gui.clear()
    draw_header()
    draw_network_viz()
    draw_sentant_list()
    draw_sensor_panel()
    draw_control_buttons()

# ====================================================================================================
# FSM Actions
# ====================================================================================================

def action_init(_):
    """Initialize the dashboard (called from FSM thread)."""
    global status_text

    # Draw initial UI (Board is already initialized in main thread)
    draw_main_screen()
    status_text.config(text="Initializing...")

    return True

def action_check_server(is_running):
    """
    Check if server process is ready and trigger appropriate event.
    Receives: is_running (bool) from check_r2_running
    """
    global DashboardFSM

    if is_running:
        DashboardFSM.event("server_ready")
    else:
        DashboardFSM.event("check_server", 1)

    return is_running

def action_start_server(is_running):
    """
    Start the Reality2 server if not already running.
    Receives: is_running (bool) from check_r2_running
    """
    global status_text, DashboardFSM

    def start_thread():
        subprocess.run([reality2_cmd, reality2_dir])

    if not is_running:
        thread = threading.Thread(target=start_thread)
        thread.start()
        if status_text:
            status_text.config(text="Starting server...")

    # Schedule check for server ready
    DashboardFSM.event("check_server", 2)
    return True

def action_connect(_):
    """
    Connect to the Reality2 server.
    Retries until HTTP server is actually responding.
    """
    global r2, status_text, DashboardFSM

    try:
        # Use verify_ssl=False for self-signed certificates on localhost
        r2 = Reality2("localhost", 4005, verify_ssl=False)

        # Test the connection by making a simple query
        # This ensures the server is actually ready
        test_result = r2.sentantAll(details="id")

        if status_text:
            status_text.config(text="Connected")
        DashboardFSM.event("connected")
    except Exception as e:
        if status_text:
            status_text.config(text=f"Waiting...")
        # Server not ready yet, retry in 2 seconds
        DashboardFSM.event("retry_connect", 2)

    return True

def action_refresh_data(_):
    """Refresh data from the server."""
    global r2, nodes_data, sentants_data, mesh_info, status_text, display_mode

    if r2 is None:
        return True

    try:
        # Get mesh network status
        mesh_info = get_mesh_info()

        # Get all sentants with events included
        result = r2.sentantAll(details="id name description events { event parameters }")
        sentants_data = result.get("sentantAll", [])

        # Extract peer/node information from mesh_info if available
        # The mesh_info contains capabilities which shows connected peers
        nodes_data = []  # Will be populated when peers connect

        if status_text:
            status_text.config(text=f"Updated: {len(sentants_data)} sentants")

        # Redraw if in main mode
        if display_mode == "main":
            draw_network_viz()
            draw_sentant_list()

    except Exception as e:
        if status_text:
            status_text.config(text=f"Refresh error: {str(e)[:15]}")

    # Schedule next refresh
    DashboardFSM.event("refresh", REFRESH_INTERVAL)
    return True

def action_read_sensor(_):
    """Read sensor values and optionally send to sentants."""
    global r2, sensor_value_text

    try:
        # Read light sensor
        light_value = light.read()

        if sensor_value_text:
            sensor_value_text.config(text=str(light_value))

        # Send to __node sentant if connected
        if r2:
            try:
                r2.sentantSend(
                    path="__node",
                    event="sensor",
                    parameters={"light": light_value}
                )
            except:
                pass  # __node might not exist

    except Exception as e:
        if sensor_value_text:
            sensor_value_text.config(text="Error")

    return True

def action_stop(_):
    """Stop the server and exit."""
    global running, r2

    # Close Reality2 connection
    if r2:
        try:
            r2.close()
        except:
            pass

    # Stop Reality2 server
    subprocess.run(["killall", "beam.smp"], capture_output=True)

    running = False
    return True

def action_update_status(message):
    """Update status text."""
    global status_text
    if status_text:
        status_text.config(text=message)
    return message

# ====================================================================================================
# Button Callbacks for A/B buttons
# ====================================================================================================

def on_a_click():
    global DashboardFSM
    DashboardFSM.event("a_button")

def on_b_click():
    global DashboardFSM
    DashboardFSM.event("b_button")

# ====================================================================================================
# Main Program
# ====================================================================================================

# FSM Transitions
#                           state               event               newstate            actions
Reality2FSM = DashboardFSM

# Initialization: init UI, check if running, start server if needed
Reality2FSM.add(Transition("start",            "init",             "starting",          [action_init, check_r2_running, action_start_server]))

# Server startup: keep checking until beam.smp is running
Reality2FSM.add(Transition("starting",         "check_server",     "starting",          [check_r2_running, action_check_server]))
Reality2FSM.add(Transition("starting",         "server_ready",     "connecting",        ["Connecting...", action_update_status, action_connect]))

# Connection: retry until HTTP server responds
Reality2FSM.add(Transition("connecting",       "retry_connect",    "connecting",        [action_connect]))
Reality2FSM.add(Transition("connecting",       "connected",        "running",           [action_refresh_data]))

# Running state
Reality2FSM.add(Transition("running",          "refresh",          "running",           [action_refresh_data]))
Reality2FSM.add(Transition("running",          "read_sensor",      "running",           [action_read_sensor]))

# Button events
Reality2FSM.add(Transition("running",          "a_button",         "running",           [trigger_refresh]))
Reality2FSM.add(Transition("*",                "b_button",         "stopping",          [action_stop]))

# Stop
Reality2FSM.add(Transition("*",                "stop",             "stopping",          [action_stop]))

# Register button callbacks
gui.on_a_click(on_a_click)
gui.on_b_click(on_b_click)

# Initialize sensor board in main thread (required for signal handlers)
print("Initializing sensor board...")
Board().begin()

# Start the FSM
Reality2FSM.go()

# Main loop
while running:
    time.sleep(0.1)

# Cleanup
Reality2FSM.stop()
print("Dashboard stopped")
