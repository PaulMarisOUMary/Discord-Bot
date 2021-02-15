from pystray import Icon as icon, Menu as menu, MenuItem as item #pip install pystray
from pypresence import Presence #pip install pypresence
from PIL import Image #pip install pillow
import asyncio, time, threading, pystray, os

Running, State, Stop = False, True, False

checked = True
def on_clicked(icon, item):
	global checked, State
	checked = not item.checked
	State = checked

def quit_all():
	global Stop
	icon.stop()
	Stop = True

class Checker(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	
	def isRunning(self):
		output = os.popen('wmic process get description, processid').read()
		return "discord.exe" in output.lower()

	def run(self):
		global Running, Stop
		while not Stop:
			Running = self.isRunning()
			time.sleep(10)

class Discord(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		try:
			asyncio.set_event_loop(asyncio.new_event_loop())
			global Running, Stop, State
			while not Stop:
				if Running:
					if State:
						RPC.connect()
						RPC.update(large_image="algosup_base_dark", large_text="Algosup",
							details="Working",
							buttons=[{"label": "Website", "url": "https://www.algosup.com/"}])
					else: RPC.close()
				time.sleep(15)
		except: pass

RPC = Presence(client_id='809116041892462612', pipe=0)

Checker().start()
Discord().start()

image = Image.open("algosup_taskbar.png")
menu = menu(item('Presence', on_clicked, checked=lambda item: checked), item('Quit', quit_all))
icon = pystray.Icon("name", image, "Algosup", menu)
icon.run()
