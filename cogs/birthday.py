#################################################
#												#
#  This Cog is made for Algosup Discord Bot		#
#   											#
#	By LavaL, creator of LavaL Bot				#
#												#
#################################################

import os
import time
import discord
import datetime
from pytz import timezone
from discord.ext import commands, tasks
from discord import Member
import aiomysql
import json
from views import birthday as vbirthday

with open('auth/database.json', 'r') as json_file:
	data = json.load(json_file)

#database connection
async def database_connection():
	connection = await aiomysql.connect(host=data['dbhost'], user=data['dbuser'], password=data['dbpassword'], db=data['dbname'])
	cursor = await connection.cursor()
	await cursor.execute("SELECT * FROM `algobot_birthday` ORDER BY `name` ASC")
	students = await cursor.fetchall()
	listofstudents = []
	for student in students:
		name = student[0]
		surname = student[1]
		discord_id = student[2]
		date_of_birth = student[3]
		promo = student[4]
		listofstudents.append(Student(name, surname, discord_id, date_of_birth, promo))
	await cursor.close()
	connection.close()
	return listofstudents

async def orderby_date_database_connection():
	connection = await aiomysql.connect(host=data['dbhost'], user=data['dbuser'], password=data['dbpassword'], db=data['dbname'])
	cursor = await connection.cursor()
	await cursor.execute("SELECT * FROM `algobot_birthday` ORDER BY `date_of_birth` ASC")
	students = await cursor.fetchall()
	listofstudents = []
	for student in students:
		name = student[0]
		surname = student[1]
		discord_id = student[2]
		date_of_birth = student[3]
		promo = student[4]
		listofstudents.append(Student(name, surname, discord_id, date_of_birth, promo))
	await cursor.close()
	connection.close()
	return listofstudents

class Student:
	def __init__(self, name, surname, discord_id, date_of_birth, promo):
		self.name = name
		self.surname = surname
		self.discord_id = discord_id
		self.date_of_birth= date_of_birth
		self.promo = promo
  
	def __str__(self):
		return "{} {} {} {} {}".format(self.name, self.surname, self.discord_id, self.date_of_birth, self.promo)
  

def Timer():
	fmt = "%H:%M:%S"
	# Current time in UTC
	now_utc = datetime.datetime.now(timezone('UTC'))
	now_berlin = now_utc.astimezone(timezone('Europe/berlin'))
	actual_time = now_berlin.strftime(fmt)
	return actual_time
 

class Algobot_Birthday(commands.Cog, name="algobot_birthday"):
	"""Birthday description"""
	def __init__(self, bot):
		self.bot = bot
		self.daily_birthday.start()

	def cog_unload(self):
		self.daily_birthday.cancel()

	@tasks.loop(hours=1)
	async def daily_birthday(self):
		a = await database_connection()
		guild = self.bot.get_guild(551753752781127680)
		channel = guild.get_channel(840003378062557202)
		is_nothing = True
		if datetime.datetime.now().hour == 9:
			for item in a:
				today = datetime.datetime.today().date()
				birthday = item.date_of_birth
				diff = abs(today - birthday)
				diff = diff.days
				age = diff // 365
				if (birthday.month == datetime.datetime.today().month) and (birthday.day == datetime.datetime.today().day):
					message = ("Bon anniversaire **<@!" + str(item.discord_id) + ">**, tu es né(e) le `" + str(birthday) + "` et tu as désormais " + str(age) + " ans ! 🎉")

					embed = discord.Embed(title="Bon anniversaire !", colour=discord.Colour.dark_gold())
					embed.add_field(name="Wow c'est ton anniversaire aujourd'hui !", value=message, inline=False)
					embed.set_thumbnail(url="https://acegif.com/wp-content/gif/joyeux-anniversaire-chat-31.gif")
					await channel.send(embed=embed)
					is_nothing = False
		
			if is_nothing:
				await channel.send("Il n'y a pas d'anniversaire aujourd'hui :sob:")


	@daily_birthday.before_loop
	async def before_daily_birthday(self):
		await self.bot.wait_until_ready()

	@commands.command(name='abirthdayall', aliases=['abda'])
	async def birthdayall(self, ctx):
		b = await orderby_date_database_connection()
		embed=discord.Embed(title="All birthdays", colour=discord.Colour.dark_gold())
		embed.set_thumbnail(url="https://stickeramoi.com/8365-large_default/sticker-mural-couronne-jaune.jpg")
		embed2=discord.Embed(title="All birthdays", colour=discord.Colour.dark_gold())
		embed2.set_thumbnail(url="https://stickeramoi.com/8365-large_default/sticker-mural-couronne-jaune.jpg")
		for item in b[0:24]:
			embed.add_field(name=item.name + " " + item.surname, value=item.date_of_birth, inline=True)
			embed.set_footer(text="Demandé par : "+str(ctx.message.author.name)+" à " + Timer(), icon_url=ctx.message.author.display_avatar.url)
		for item in b[25::]:
			embed2.add_field(name=item.name + " " + item.surname, value=item.date_of_birth, inline=True)
			embed2.set_footer(text="Demandé par : "+str(ctx.message.author.name)+" à " + Timer(), icon_url=ctx.message.author.display_avatar.url)

		await ctx.send(embed=embed)
		await ctx.send(embed=embed2)

	@commands.command(name='abirthdaya', aliases=['abirth'])
	async def birthday(self, ctx, member: Member = None):
		if not member:
			ID_discord = ctx.message.author.id
		else:
			ID_discord = member.id
		a = await database_connection()
		for item in a:
			if ID_discord == item.discord_id:
				today = datetime.datetime.today().date()
				birthday = item.date_of_birth
				diff = abs(today - birthday)
				diff = diff.days
				age = diff // 365
				message = "<@!" + str(item.discord_id) + "> tu es agé(e) de " + str(age) + " ans ! 🎉"
				embed = discord.Embed(title=f"Age de {item.surname}", description=message, color=0x12F932)

				embed.set_thumbnail(url="https://acegif.com/wp-content/gif/joyeux-anniversaire-chat-31.gif")

				embed.set_footer(text="Demandé par : "+str(ctx.message.author.name)+" à " +
							Timer(), icon_url=ctx.message.author.display_avatar.url)

				await ctx.send(embed=embed)

	@commands.command(name='alenstudent', aliases=['alens'])
	async def lenstudent(self, ctx):
		a = await database_connection()
		await ctx.send(len(a))

	@commands.command(name='addbirth', aliases=['ab'])
	@commands.cooldown(1, 30, commands.BucketType.user)
	async def aa(self, ctx, name, surname, discord_id, date_of_birth, promo):
		connection = await aiomysql.connect(host=data['dbhost'], user=data['dbuser'], password=data['dbpassword'], db=data['dbname'])
		cursor = await connection.cursor()
		lang_list = [name, surname,discord_id,date_of_birth,promo]
		try:
			await cursor.execute("INSERT INTO `algobot_birthday`(`name`, `surname`, `discord_id`, `date_of_birth`, `promo`) VALUES (%s, %s, %s, %s, %s)", lang_list)
			await connection.commit()
			await ctx.send("Tu t'es bien enregistré !")
		except:
			raise commands.CommandError('La commande est mal écrite, ex : Nicolaon, Romain, 405414058775412746, 2002-02-22, Alpha')
  
	@commands.command(name='deletebirth', aliases=['db'])
	@commands.is_owner()
	async def bb(self, ctx, text_do_delete):
		connection = await aiomysql.connect(host=data['dbhost'], user=data['dbuser'], password=data['dbpassword'], db=data['dbname'])
		cursor = await connection.cursor()
		await cursor.execute("DELETE FROM `algobot_birthday` WHERE `name` = %s", text_do_delete)
		await connection.commit()
		await ctx.send("Tu as bien delete !")


def setup(bot):
	bot.add_cog(Algobot_Birthday(bot))
