import discord
import time

from datetime import date, datetime, timedelta
from discord.ext import commands
from classes.processimage import ProcessImage
from classes.microsofto365 import MicrosoftO365

startat, endat = 9, 17

class Schedule(commands.Cog, name="schedule", command_attrs=dict(hidden=False)):
	"""Show your scolar schedule"""
	def __init__(self, bot):
		self.bot = bot
		self.microsoft = MicrosoftO365('planning@algosup.com')
		self.microsoft.readToken()
		self.microsoft.login()

	def help_custom(self):
		emoji = '📅'
		label = "Schedule"
		description = "Algosup's planning in two commands."
		return emoji, label, description

	def getElements(self, start, end):
		events = self.microsoft.extractCalendar(start, end)
		self.microsoft.extractEvents(events)

		if len(self.microsoft.events) > 0:
			self.microsoft.sortByDay(self.microsoft.events)
			self.microsoft.sortByHour(self.microsoft.events)

			self.microsoft.findDuplicate(self.microsoft.events)

		return self.microsoft.events

	def processSchedule(self, events, startat = 9, endat = 17):
		nday = len(events)
		if nday < 1: nday = 1

		nhours = endat+1 - startat
		width = 20+400*nday+10*(nday-1)
		height = 50+50*nhours+nhours

		image = ProcessImage(width, height)

		for j in range(0, nday):
			for i in range(1,nhours+1):
				image.rectangle(image.place(20+400*j+10*j, i*51, 400, 50), (255,255,255))
				image.text(image.place(0, i*51 - 5, 20, 20), (255,255,255), "0"+str(i+(startat-1))+"h" if i+(startat-1) < 10 else str(i+(startat-1))+"h", 11)
		image.textCentered(width, 50, (255,255,255), "PLANNING", 30)

		for nday, day in enumerate(events):
			for event in day:
				title, start, end, n, duplicate = event[0], float(event[2][0:2])+float(event[2][3:5])/60-startat, float(event[3][0:2])+float(event[3][3:5])/60-startat, event[4], event[5]
				duration = end - start

				if not round(start) == start:
					y = 50+50*start+1*int(start+1)+1
					height = 50*duration+1*int(duration)-1
				elif not round(end) == end:
					y = 50+50*start+1*int(start+1)
					height = 50*duration+1*int(duration)
				else:
					y = 50+50*start+1*int(start+1)
					height = 50*duration+1*int(duration)-1

				if duplicate > 1 and n != duplicate:
					x = 20+400*nday+10*nday + 400/duplicate*(n-1)
					width = 400/duplicate - (duplicate-1)+1
				elif duplicate > 1:
					x = 20+400*nday+10*nday + 400/duplicate*(n-1)+1
					width = 400/duplicate - (duplicate-1)
				else : 
					x = 20+400*nday+10*nday
					width = 400

				fontsize = 14
				s = image.getTextsize(title, fontsize)

				image.rectangle(image.place(x = x, y = y, width = width, height = height), (0, 100, 200))
				image.text((x+width/2-s[0]/2, y+height/2-s[1]/2), color = (255, 255, 255), text = title, fontsize = fontsize)

		return image.saveBinary()

	@commands.command(name='daycalendar', aliases=['dc'])
	async def day_calendar(self, ctx, more = 0):
		"""Get the schedule of the scolar day."""
		today = datetime.now().date()
		start = today + timedelta(days=more)
		end = start + timedelta(days=1)

		events = self.getElements(start, end)
		image = self.processSchedule(events, startat, endat)

		embed = discord.Embed(description='📅 __Planning__ : of `'+str(start)+'`', colour=0x474747)
		embed.set_image(url='attachment://schedule.png')
		embed.set_footer(text="Requested by : "+str(ctx.message.author.name)+" at "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(file=discord.File(fp=image, filename='schedule.png'), embed=embed)
		image.close()

	@commands.command(name='weekcalendar', aliases=['wc'])
	async def week_calendar(self, ctx, more = 0):
		"""Get the schedule of the scolar week."""
		today = datetime.now().date()
		start = today + timedelta(days=today.weekday()+1+((more-1)*7))
		end = start + timedelta(weeks=1)

		events = self.getElements(start, end)
		image = self.processSchedule(events, startat, endat)

		embed = discord.Embed(description='📅 __Planning__ : from `'+str(start)+'` to `'+str(end)+'`', colour=0x474747)
		embed.set_image(url='attachment://schedule.png')
		embed.set_footer(text="Requested by : "+str(ctx.message.author.name)+" at "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(file=discord.File(fp=image, filename='schedule.png'), embed=embed)
		image.close()

def setup(bot):
	bot.add_cog(Schedule(bot))
