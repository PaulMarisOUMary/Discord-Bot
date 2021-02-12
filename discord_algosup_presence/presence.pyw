from pystray import MenuItem as item #pip install pystray
from pypresence import Presence #pip install pypresence
from PIL import Image #pip install pillow
import pystray

def quit_all():
    RPC.clear()
    icon.stop()

def enable_presence():
    """RPC.update(large_image="algosup_base_dark", large_text="Algosup",
            small_image="dark_vscode", small_text="Visual Studio Code",
            details="Working in", state="Go workspace",
            buttons=[{"label": "Website", "url": "https://www.algosup.com/"}])"""
    RPC.update(large_image="algosup_base_dark", large_text="Algosup",
            details="Working",
            buttons=[{"label": "Website", "url": "https://www.algosup.com/"}])
    
    icon.notify(message='Presence Enabled !', title="Discord Algosup Presence")

def disable_presence():
    RPC.clear()
    icon.notify(message='Presence Disabled !', title="Discord Algosup Presence")

state = True
def switch_presence(icon, item):
    global state
    state = not item.checked
    if state : enable_presence()
    else : disable_presence()
    

RPC = Presence(client_id='809116041892462612', pipe=0)
RPC.connect()

image = Image.open("algosup_taskbar.png")
menu = (item('Discord presence', switch_presence, checked=lambda item: state),item('Quit', lambda : quit_all(), checked=lambda item: False))
icon = pystray.Icon("name", image, "Algosup", menu)
enable_presence()
icon.run()