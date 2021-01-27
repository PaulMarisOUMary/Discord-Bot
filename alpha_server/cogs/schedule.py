import discord
import time
import os

from O365 import Account, Connection, MSGraphProtocol
from datetime import date, datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands

def new_img():
	image = Image.new(mode="RGB", size=(420,509), color=(47, 47, 47))
	draw = ImageDraw.Draw(image)
	draw.rectangle((0, 0, 420, 50), fill="#1a1a1a")
	draw.rectangle((0, 0, 20, 560), fill="#1a1a1a")
	draw.text((10,10), "Planning : ", font=ImageFont.truetype("arial.ttf", 30), fill=(255,255,255,128))
	for i in range(10):
		draw.line((20, 50+50*i+i, 420, 50+50*i+i), fill="#616161")
	for i in range(9):
		if i+9 < 10: t = "0"+str(i+9)+"h"
		else : t = str(i+9)+"h"
		draw.text((0,50+50*i+i), t, font=ImageFont.truetype("arial.ttf", 11), fill=(255,255,255,128))
	image.save("calendar.png")

def add_task_img(events):
    image = Image.open("calendar.png")
    draw = ImageDraw.Draw(image)
    duplicate = bool
    for i, event in enumerate(events):
        clas, date, start, duration = event[0], event[1], int(event[2][0:2]), int(event[4].seconds/60/60)
        for ev in events: 
            if ev != event:
                if int(ev[2][0:2])+int(ev[4].seconds/60/60) <= start+duration and start <= int(ev[2][0:2]):
                    duplicate = True
                    draw.rectangle((20+420/2*(i-1), 50+(start-9)*50+start-9, 420/2*i, 50+(duration+start-9)*50+duration), fill="#4a4a4a")
                    draw.text((20+420/2*(i-1), 50+(start-9)*50+start-9), clas, font=ImageFont.truetype("arial.ttf", 20), fill=(255,255,255,128))

                else: duplicate = False
        if not duplicate:
            draw.rectangle((20, 50+(start-9)*50+start-9, 420, 50+(duration+start-9)*50+start), fill="#4a4a4a")
            draw.text((25, 50+(start-9)*50+start-9), clas, font=ImageFont.truetype("arial.ttf", 20), fill=(255,255,255,128))

    image.save("calendar.png")

class Schedule(commands.Cog, name="schedule"):
	def __init__(self, bot):
		self.bot = bot
		if os.name == 'nt':
			end = os.getcwd()+'\\auth\\'
		elif os.name == 'posix':
			end = os.getcwd()+'/auth/'
		CLIENT_ID = open(end+"client.dat", "r").read()
		SECRET_ID = open(end+"secret.dat", "r").read()
		TENANT_ID = open(end+"tenant_id.dat", "r").read()
		account = Account((CLIENT_ID, SECRET_ID), protocol=MSGraphProtocol(default_resource='planning@algosup.com'), auth_flow_type='credentials', tenant_id=TENANT_ID)
		if account.authenticate(scope=['Calendars.Read.Shared', 'Calendars.Read']): print('Authenticated!')
		schedule = account.schedule()
		self.calendar = schedule.get_default_calendar()

	def extract_calendar(self, start, end):
		query = self.calendar.new_query('start').greater_equal(start)
		query.chain('and').on_attribute('end').less_equal(end)
		events = self.calendar.get_events(query=query, include_recurring=True)
		return events

	def extract_infos(self, info):
		info = str(info)
		heading = info[info.find('Subject:')+9:info.find('on:')-2]
		date = info[info.find('on:')+4:info.find('from:')-1]
		start_timetable = info[info.find('from:')+6:info.find('to:')-1]
		end_timetable = info[info.find('to:')+4:-1]
		duration = datetime.strptime(end_timetable, '%H:%M:%S')-datetime.strptime(start_timetable, '%H:%M:%S')
	
		return heading, date, start_timetable, end_timetable, duration

	@commands.command(name='actualcalendar', aliases=['ac'])
	async def actual_calendar(self, ctx):
		today, events, final = datetime.today(), [], []
		start = datetime(today.year, today.month, today.day)
		end = start + timedelta(1)
		new_img()
		for event in self.extract_calendar(start, end):
			events.append(str(event))
		for str_event in events:
			final.append(self.extract_infos(str_event))
		
		add_task_img(final)

		embed = discord.Embed(colour=0x474747)
		embed.set_image(url='attachment://stat.png')
		embed.set_footer(text="Requête de : "+str(ctx.message.author)+" à "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(file=discord.File("calendar.png", 'stat.png'), embed=embed)

	@commands.command(name='weekcalendar', aliases=['wc'])
	async def week_calendar(self, ctx):
		await ctx.send("week")

	@commands.command(name='nextcalendar', aliases=['nc'])
	async def next_calendar(self, ctx):
		await ctx.send("next")

def setup(bot):
	bot.add_cog(Schedule(bot))