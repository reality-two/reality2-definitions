# ****************************************************************************************************
# Roy C. Davies, 2023
# ****************************************************************************************************
from unihiker import GUI
import time
from pinpong.board import *
from pinpong.extension.unihiker import *
import subprocess
import threading
import ifaddr
import ssl
import time
import re
from requests import *

from reality2 import Reality2
from fsm import *

# ====================================================================================================
# Variables
# ====================================================================================================
reality2_dir = "/root/aarch64_GNU_Linux/reality2/" # Adjust this location as appropriate
reality2_cmd = reality2_dir + "run"
unihiker_config_file = "/opt/unihiker/pyboardUI/config.cfg"
unihiker_config = {}
ipaddr = ""
something_changed = False
running = True
messageGUI = ""
stateGUI = ""
qrcode = ""
qrcode_text = ""

r2 = None

display_wifi_qr = True

# WIFI Hotspot
wifi_ssid = ""
wifi_password = ""

# Set the GUI
gui = GUI()
stateGUI = gui.draw_text(x=120, y=0, text="", origin="n", font_size=10)

ssl_context = ssl.SSLContext()
ssl_context.verify_mode = ssl.CERT_NONE
# ====================================================================================================


# ====================================================================================================
# Create the FSM
# ====================================================================================================
Reality2FSM = Automation() 
# ====================================================================================================


# ====================================================================================================
# Service functions
# ====================================================================================================



# ----------------------------------------------------------------------------------------------------
# Generate a QR Code string for the hotspot
# ----------------------------------------------------------------------------------------------------
def generate_wifi_qr_code(ssid, password, authentication_type='WPA'):
    wifi_string = f'WIFI:T:{authentication_type};S:{ssid};P:{password};;'
    return wifi_string
# ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------
# Button clicks
# ----------------------------------------------------------------------------------------------------
def on_a_click():
    global Reality2FSM
    Reality2FSM.event("a_button")

def on_b_click():
    global Reality2FSM
    Reality2FSM.event("b_button")
# ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------
# Show the current state on the GUI
# ----------------------------------------------------------------------------------------------------
def print_state():
    global stateGUI, Reality2FSM, running
    
    while running:
        stateGUI.config(text="state = " + Reality2FSM._state)
        time.sleep(0.05)
# ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
def get_hotspot_ip():
    ipaddr = ""
    adapters = ifaddr.get_adapters()
    
    # First see if there is a wifi connection
    for adapter in adapters:
        if "wlan0" in adapter.nice_name:
            for ip in adapter.ips:
                if ip.is_IPv4:
                    ipaddr = ip.ip
                    
    # Otherwise see if there is a hotspot
    if (ipaddr == ""):
        for adapter in adapters:
            if "p2p0" in adapter.nice_name:
                for ip in adapter.ips:
                    if ip.is_IPv4:
                        ipaddr = ip.ip
                        
    return ipaddr
# ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------
# Switch between QR codes
# ----------------------------------------------------------------------------------------------------
def switch_qr():
    global display_wifi_qr, qrcode, qrcode_text, ipaddr, wifi_ssid, wifi_password
    
    display_wifi_qr = not display_wifi_qr
    
    if display_wifi_qr:
        qrcode.config(text=generate_wifi_qr_code(wifi_ssid, wifi_password))
        qrcode_text.config(text="ssid: " + wifi_ssid + " pass: " + wifi_password)
    else:
        qrcode.config(text="https://" + ipaddr + ":4005")
        qrcode_text.config(text="reality2 web")
# ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------
# Set things up
# ----------------------------------------------------------------------------------------------------
def initialise():
    global messageGUI, stateGUI, gui, qrcode, qrcode_text, display_wifi_qr, wifi_ssid, wifi_password, ipaddr
    
    # Get the Wifi hotspot details
    with open(unihiker_config_file) as user_file:
        unihiker_config = json.loads(user_file.read())
        wifi_ssid = unihiker_config["apName"]
        wifi_password = unihiker_config["apPassword"]
    
    # Get the IP Addr of this Reality2 Node
    ipaddr = get_hotspot_ip()

    # Set up the callbacks for the buttons
    gui.on_a_click(on_a_click)
    gui.on_b_click(on_b_click)

    # Draw the original message and keep the GUI object
    messageGUI = gui.draw_text(x=120, y=50, text="Initialising", origin="n", font_size=10)
    
    # Create a scannable QR code to the Wifi
    if (ipaddr == ""):
        gui.draw_text(x=120, y=170, text="No Network", origin="n", font_size=10)
    else:
        qrcode = gui.draw_qr_code(x=120, y=170, w=180, text=generate_wifi_qr_code(wifi_ssid, wifi_password), origin="center")
        qrcode_text = gui.draw_text(x=120, y=250, text="ssid: " + wifi_ssid + " pass: " + wifi_password, origin="n", font_size=10)
    
    # Interaction Button to toggle between wifi and webapp QR codes
    gui.add_button(x=120, y=290, w=100, h=30, text="Toggle", origin="center", onclick=switch_qr)

    # Show the state of the FSM in a parallel thread
    gui.start_thread(print_state)

    # Start the sensors board
    Board().begin()
# ----------------------------------------------------------------------------------------------------

# ====================================================================================================



# ====================================================================================================
# Actions
# ====================================================================================================

# ----------------------------------------------------------------------------------------------------
# Check if Reality2 Node is running
# ----------------------------------------------------------------------------------------------------
def check_r2_node(_):
    processes = subprocess.run(["ps", "-e"], capture_output=True)
    return ("beam.smp" in str(processes.stdout))
# ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------
# Take one input coming from the previous action (usually the function above and create an event.
# ----------------------------------------------------------------------------------------------------
def check_server(is_running):
    global Reality2FSM
    
    if (is_running):
        Reality2FSM.event("r2_node_ok")
    else:
        Reality2FSM.event("check_r2_node", 1)
        
    return (True)
# ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------
# Start Reality2 Node
# ----------------------------------------------------------------------------------------------------
def start_thread():
    subprocess.run([reality2_cmd, reality2_dir])

def start_r2_node(is_running):
    global Reality2FSM
    if (not is_running):
        the_thread = threading.Thread(target=start_thread)
        the_thread.start()
        
    Reality2FSM.event("check_r2_node", 1)

    return (True)
# ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------
# Stop Reality2 Node
# ----------------------------------------------------------------------------------------------------
def stop_thread():
    subprocess.run(["killall", "beam.smp"])

def stop_reality2(is_running):
    global Reality2FSM
    if (is_running):
        the_thread = threading.Thread(target=stop_thread)
        the_thread.start()

    return (True)
# ----------------------------------------------------------------------------------------------------

    
    
# ----------------------------------------------------------------------------------------------------
# Read a sensor, in this case, the light level sensor on the Unihiker
# ----------------------------------------------------------------------------------------------------
def read_sensor(_):
    global Reality2FSM, r2
    
    # Read ambient light via PinPong
    light_value = light.read()

    # Send the value to a Sentant
    if (r2 != None):
        r2.sentantSendByName (name = "__node", event = "sensor", parameters = {"data": light_value}, passthrough = {})

    # Set up the next read sensor in 5 seconds time
    Reality2FSM.event("read_sensor", 5)

    # Return a message to be printed to screen
    return "Sensor value :" + str(light_value)
# ----------------------------------------------------------------------------------------------------
                
                

# ----------------------------------------------------------------------------------------------------
# Connect to Reality2 node
# ----------------------------------------------------------------------------------------------------
def connect_to_r2(_):
    global r2
    
    r2 = Reality2("localhost", 4005)

    Reality2FSM.event("connected")
    Reality2FSM.event("read_sensor", 5)
# ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------
# Change the message on the screen
# ----------------------------------------------------------------------------------------------------
def printout(something):
    global messageGUI, Reality2FSM

    messageGUI.config(text=something)
    Reality2FSM.event("clear", 2)
    print (something)
    return True
# ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------
# Clear the message on the screen
# ----------------------------------------------------------------------------------------------------
def clear(_):
    global messageGUI
    messageGUI.config(text="")
    return True
# ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------
# Quit the Python script
# ----------------------------------------------------------------------------------------------------
def quit(_):
    global running

    running = False
# ----------------------------------------------------------------------------------------------------

# ====================================================================================================


# ====================================================================================================
# Main Code
# ====================================================================================================

# ----------------------------------------------------------------------------------------------------
# Set the transitions
# ----------------------------------------------------------------------------------------------------
#                           state               event               newstate            actions
# Kick the whole process off by starting the R2 node by running the 'run' script
Reality2FSM.add(Transition("start",            "init",             "starting",          ["Starting Reality2 Node", printout, check_r2_node, start_r2_node]))

# Keep checking until the R2 node is up and running
Reality2FSM.add(Transition("starting",         "check_r2_node",    "starting",          [check_r2_node, check_server]))
Reality2FSM.add(Transition("starting",         "r2_node_ok",       "ready",             ["Reality2 Node ready", printout, connect_to_r2]))

# Read the sensor
Reality2FSM.add(Transition("ready",            "read_sensor",      "ready",             [read_sensor, printout]))

# Used to clear the GUI message so it doesn't linger
Reality2FSM.add(Transition("*",                "clear",            "*",                 [clear]))

# Button action
Reality2FSM.add(Transition("*",                "b_button",         "quitting",          ["Quitting...", printout, check_r2_node, stop_reality2, quit]))
# ----------------------------------------------------------------------------------------------------

# Initialise various things
initialise()

# Set the FSM
Reality2FSM.go()

# Keep going until the end
while running:            
    time.sleep(0.1)

# Close down the FSM
Reality2FSM.stop()
# ====================================================================================================