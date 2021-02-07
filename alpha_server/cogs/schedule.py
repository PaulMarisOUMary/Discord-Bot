import discord
import time
import io
import os

from O365 import Account, MSGraphProtocol
from datetime import date, datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands

def add_task_img(final):
	image = Image.new(mode="RGBA", size=(20+400*len(final),509), color=(47, 47, 47))
	draw = ImageDraw.Draw(image)

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
			if event[3][3:5] == '30': duration += 0.5
			if not is_duplicate(event, events):
				draw.rectangle((20+400*j, 50+(start-9)*50+start-9, 420-1+400*j, 50+(start-9)*50+(start-9)+50*duration+duration), fill=(255,255,255,127))
				draw.text((20+400/2-len(clas)*11/2+400*j, 50+(start-9)*50+(start-9)+duration*50/2-25/2), clas, font=ImageFont.truetype("arial.ttf", 25), fill=(0,0,0,127))
			else :
				if len(clas) <= 20: text = clas
				else: text = clas[0:20]
				if event in memory:
					draw.rectangle((20+400*j, 50+(start-9)*50+start-9, (420-20-20)/2+10+400*j, 50+(start-9)*50+start-9+50*duration+duration), fill=(255,255,255,127))
					draw.text((5+20+400*j, 50+(start-9)*50+(start-9)+duration*50/2-25/2), text, font=ImageFont.truetype("arial.ttf", 20), fill=(0,0,0,127))
				else:
					draw.rectangle((30+(420-20-20)/2+20+400*j, 50+(start-9)*50+start-9, 20+(420-20-20)/2+20+(420-20-20)/2+400*j, 50+(start-9)*50+start-9+50*duration+duration), fill=(255,255,255,127))
					draw.text((15+20+(420-20-20)/2+20+400*j, 50+(start-9)*50+(start-9)+duration*50/2-25/2), text, font=ImageFont.truetype("arial.ttf", 20), fill=(0,0,0,127))
		draw.line((20+400*j, 50, 20+400*j, 509), fill=(127,127,127,127))

	draw.rectangle((0, 0, 20+400*len(final), 50), fill="#1a1a1a")
	draw.rectangle((0, 0, 20, 509), fill="#1a1a1a")
	for i in range(10):
		if i+9 < 10: t = "0"+str(i+9)+"h"
		else : t = str(i+9)+"h"
		draw.text((0,50+50*i+i), t, font=ImageFont.truetype("arial.ttf", 11), fill=(255,255,255,127))
		draw.line((20, 50+50*i+i, 20+400*len(final), 50+50*i+i), fill=(127,127,127,127))
	draw.text(((20+400*len(final))/2-150/2,10), "PLANNING", font=ImageFont.truetype("arial.ttf", 30), fill=(255,255,255,127))

	image_binary = io.BytesIO()
	image.save(image_binary, "PNG")
	image_binary.seek(0)
	return image_binary

class Schedule(commands.Cog, name="schedule"):
	def __init__(self, bot):
		self.bot = bot
		end = os.getcwd()
		CLIENT_ID = open(end+"/auth/client.dat", "r").read()
		SECRET_ID = open(end+"/auth/secret.dat", "r").read()
		TENANT_ID = open(end+"/auth/tenant_id.dat", "r").read()
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

	@commands.command(name='actualcalendar', aliases=['ac'])
	async def actual_calendar(self, ctx):
		today, events = datetime.now().date(), []
		start = today
		end = start + timedelta(1)
		for event in await self.extract_calendar(start, end):
			events.append(self.extract_infos(str(event)))
		image = add_task_img([events])

		embed = discord.Embed(colour=0x474747)
		embed.set_image(url='attachment://schedule.png')
		embed.set_footer(text="Requested by : "+str(ctx.message.author.name)+" à "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(file=discord.File(fp=image, filename='schedule.png'), embed=embed)
		image.close()

	@commands.command(name='nextcalendar', aliases=['nc'])
	async def next_calendar(self, ctx):
		today, events = datetime.now().date(), []
		start = today + timedelta(1)
		end = start + timedelta(1)
		for event in await self.extract_calendar(start, end):
			events.append(self.extract_infos(str(event)))
		image = add_task_img([events])

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
		
		image = add_task_img(final)

		embed = discord.Embed(colour=0x474747)
		embed.set_image(url='attachment://schedule.png')
		embed.set_footer(text="Requested by : "+str(ctx.message.author.name)+" à "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(file=discord.File(fp=image, filename='schedule.png'), embed=embed)
		image.close()

def setup(bot):
	bot.add_cog(Schedule(bot))
