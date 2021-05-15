import discord
import time
import io
import os

from O365 import Account, MSGraphProtocol
from datetime import date, datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands

def task_in_img(final):
	image = Image.new(mode="RGB", size=(20+410*len(final), 509), color=(47,47,47))
	draw = ImageDraw.Draw(image)

	def to_place(x,y,width,height):
		return (x,y,x+width,y+height)

	def is_duplicate(event, events, duplicate = False, point = 0):
		for ev in events:
			if ev != event and int(ev[2][0:2])+int(ev[4].seconds/60/60) <= start+duration and start <= int(ev[2][0:2]):
				duplicate = True
				memory.append(ev)
		return duplicate

	for j, events in enumerate(final):
		memory = []
		for i, event in enumerate(events):
			clas, start, duration = event[0], int(event[2][0:2]), int(event[4].seconds/60/60)
			duration += int(event[3][3:5])/60
			if not is_duplicate(event, events):
				if len(clas) <= 45: text = clas
				else: text = clas[0:45]
				draw.rectangle(to_place(x=20+410*j,y=50+(start-9)*50+start-9,width=400,height=50*duration+duration), fill=(255,255,255))
				draw.text((20+410*j,50+(start-9)*50+(start-9)+duration*50/2-25/2), text, font=ImageFont.truetype("arial.ttf", 20), fill=(0,0,0))
			else:
				if len(clas) <= 25: text = clas
				else: text = clas[0:25]
				if event in memory:
					draw.rectangle(to_place(x=20+410*j,y=50+(start-9)*50+start-9,width=(400-20)/2,height=50*duration+duration), fill=(255,255,255))
					draw.text((20+410*j,50+(start-9)*50+(start-9)+duration*50/2-25/2), text, font=ImageFont.truetype("arial.ttf", 20), fill=(0,0,0))
				else:
					draw.rectangle(to_place(x=(400-20)/2+40+410*j,y=50+(start-9)*50+start-9,width=(400-20)/2,height=50*duration+duration), fill=(255,255,255))
					draw.text(((400-20)/2+40+410*j,50+(start-9)*50+(start-9)+duration*50/2-25/2), text, font=ImageFont.truetype("arial.ttf", 20), fill=(0,0,0))

	draw.rectangle((0, 0, 20+410*len(final), 50), fill="#1a1a1a")
	draw.rectangle((0, 0, 20, 509), fill="#1a1a1a")
	for i in range(10):
		if i+9 < 10: t = "0"+str(i+9)+"h"
		else : t = str(i+9)+"h"
		draw.text((0,50+50*i+i), t, font=ImageFont.truetype("arial.ttf", 11), fill=(255,255,255))
		draw.line(to_place(20, 50+50*i+i, 410*len(final), 0), fill=(127,127,127))
	draw.text(((20+410*len(final))/2-150/2,10), "PLANNING", font=ImageFont.truetype("arial.ttf", 30), fill=(255,255,255,127))
	
	image_binary = io.BytesIO()
	image.save(image_binary, "PNG")
	image_binary.seek(0)
	return image_binary

class Schedule(commands.Cog, name="schedule"):
	def __init__(self, bot):
		self.bot = bot
		source_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		CLIENT_ID = open(os.path.join(source_directory, "auth", "client.dat"), "r").read()
		SECRET_ID = open(os.path.join(source_directory, "auth", "secret.dat"), "r").read()
		TENANT_ID = open(os.path.join(source_directory, "auth", "tenant_id.dat"), "r").read()
		account = Account((CLIENT_ID, SECRET_ID), protocol=MSGraphProtocol(default_resource='planning@algosup.com'), auth_flow_type='credentials', tenant_id=TENANT_ID)
		if account.authenticate(scope=['Calendars.Read.Shared', 'Calendars.Read']): pass#print('Authenticated!')
		schedule = account.schedule()
		self.calendar = schedule.get_default_calendar()

	async def extract_calendar(self, start, end):
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

	@commands.command(name='currentcalendar', aliases=['cc', 'ac'])
	async def actual_calendar(self, ctx):
		today, events = datetime.now().date(), []
		start = today
		end = start + timedelta(1)
		for event in await self.extract_calendar(start, end):
			if not "start" in str(event):
				events.append(self.extract_infos(str(event)))
		image = task_in_img([events])

		embed = discord.Embed(colour=0x474747)
		embed.set_image(url='attachment://schedule.png')
		embed.set_footer(text="Requested by : "+str(ctx.message.author.name)+" à "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(file=discord.File(fp=image, filename='schedule.png'), embed=embed)
		image.close()

	@commands.command(name='nextcalendar', aliases=['nc'])
	async def next_calendar(self, ctx, more = 1):
		today, events = datetime.now().date(), []
		start = today + timedelta(more)
		end = start + timedelta(1)
		for event in await self.extract_calendar(start, end):
			if not "start" in str(event):
				events.append(self.extract_infos(str(event)))
		image = task_in_img([events])

		embed = discord.Embed(colour=0x474747)
		embed.set_image(url='attachment://schedule.png')
		embed.set_footer(text="Requested by : "+str(ctx.message.author.name)+" à "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(file=discord.File(fp=image, filename='schedule.png'), embed=embed)
		image.close()

	@commands.command(name='weekcalendar', aliases=['wc'])
	async def week_calendar(self, ctx):
		today, events, stock, final = datetime.now().date(), [], [], []
		start = today - timedelta(days=today.weekday())
		end = start + timedelta(days=5)
		for event in await self.extract_calendar(start, end):
			if not "start" in str(event):
				events.append(self.extract_infos(str(event)))
		for i in range(0, len(events)):
			for j in range(0, len(events)-i-1):
				if events[j][1] > events[j+1][1]:
					events[j], events[j+1] = events[j+1], events[j]
		for i in range(0, len(events)):
			stock.append(events[i])
			if i == len(events)-1 or events[i][1] != events[i+1][1]:
				final.append(stock)
				stock = []
		
		image = task_in_img(final)

		embed = discord.Embed(colour=0x474747)
		embed.set_image(url='attachment://schedule.png')
		embed.set_footer(text="Requested by : "+str(ctx.message.author.name)+" à "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(file=discord.File(fp=image, filename='schedule.png'), embed=embed)
		image.close()

	@commands.command(name='nextweekcalendar', aliases=['nwc'])
	async def next_week_calendar(self, ctx, more = 1):
		today, events, stock, final = datetime.now().date(), [], [], []
		start = today - timedelta(days=today.weekday()+(more*7))
		end = start + timedelta(days=5)
		for event in await self.extract_calendar(start, end):
			if not "start" in str(event):
				events.append(self.extract_infos(str(event)))
		for i in range(0, len(events)):
			for j in range(0, len(events)-i-1):
				if events[j][1] > events[j+1][1]:
					events[j], events[j+1] = events[j+1], events[j]
		for i in range(0, len(events)):
			stock.append(events[i])
			if i == len(events)-1 or events[i][1] != events[i+1][1]:
				final.append(stock)
				stock = []
		image = task_in_img(final)

		embed = discord.Embed(colour=0x474747)
		embed.set_image(url='attachment://schedule.png')
		embed.set_footer(text="Requested by : "+str(ctx.message.author.name)+" à "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(file=discord.File(fp=image, filename='schedule.png'), embed=embed)
		image.close()

def setup(bot):
	bot.add_cog(Schedule(bot))
