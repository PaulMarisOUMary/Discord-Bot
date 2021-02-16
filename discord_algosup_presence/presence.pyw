from pystray import Icon as icon, Menu as menu, MenuItem as item #pip install pystray
from pypresence import Presence #pip install pypresence
from PIL import Image, ImageDraw, ImageFont #pip install pillow
import asyncio, time, threading, pystray, os

State, Stop, sett = True, False, False

checked = True
def on_clicked(icon, item):
	global checked, State, sett
	checked = not item.checked
	State = checked
	if not State:
		sett = False

def quit_all():
	global Stop
	icon.stop()
	Stop = True
	asyncio.close()

def create_image():
	image = Image.new('RGB', (512, 512), (15, 17, 20))
	draw = ImageDraw.Draw(image)
	for i, color in enumerate([(195,195,195), (127,127,127), (169,16,28)]):
		draw.text((50+150*i, 10), "}", font=ImageFont.truetype("arial.ttf", 375), fill=color)
		draw.ellipse((40+150*i, 160, 90+150*i, 210), fill=color)

	return image

class SetPresence(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def isRunning(self):
		output = os.popen('wmic process get description, processid').read()
		return "discord.exe" in output.lower()

	def run(self):
		asyncio.set_event_loop(asyncio.new_event_loop())
		global Stop, State, sett
		while not Stop:
			if self.isRunning():
				RPC.connect()
				if State and not sett:
					RPC.update(large_image="algosup_base_dark", large_text="Algosup",
						details="Working",
						buttons=[{"label": "Website", "url": "https://www.algosup.com/"}])
					sett = True
				if not State and sett:
					RPC.clear()
			print("0")

if __name__ == "__main__":
	RPC = Presence(client_id='809116041892462612', pipe=0)
	SetPresence().start()

	menu = menu(item('Presence', on_clicked, checked=lambda item: checked), item('Quit', quit_all))
	icon = pystray.Icon("name", create_image(), "Algosup", menu)
	icon.run()
