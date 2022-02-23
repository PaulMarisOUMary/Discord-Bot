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

with open('auth/database.json', 'r') as json_file:
	data = json.load(json_file)

#database connection
async def database_connection():
	connection = await aiomysql.connect(host=data['dbhost'], user=data['dbuser'], password=data['dbpassword'], db=data['dbname'])
	cursor = await connection.cursor()
	await cursor.execute("SELECT * FROM `algobot_birthday` ORDER BY `date_of_birth` ASC")
	students = await cursor.fetchall()
	listofstudents = []
	for student in students:
		discord_id = student[0]
		date_of_birth = student[1]
		listofstudents.append(Student(discord_id, date_of_birth))
	await cursor.close()
	connection.close()
	return listofstudents

class Student:
	def __init__(self, discord_id, date_of_birth):
		self.discord_id = discord_id
		self.date_of_birth = date_of_birth
  
	def __str__(self):
		return "{} {} {} {} {}".format(self.discord_id, self.date_of_birth)
  

def Timer():
	fmt = "%H:%M:%S"
	# Current time in UTC
	now_utc = datetime.datetime.now(timezone('UTC'))
	now_berlin = now_utc.astimezone(timezone('Europe/berlin'))
	actual_time = now_berlin.strftime(fmt)
	return actual_time
 

class Birthday(commands.Cog, name="birthday"):
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

	@commands.command(name='birthdayall', aliases=['bda'])
	async def birthdayall(self, ctx):
		a = await database_connection()
		embed=discord.Embed(title="All birthdays", colour=discord.Colour.dark_gold())
		embed.set_thumbnail(url="https://stickeramoi.com/8365-large_default/sticker-mural-couronne-jaune.jpg")
		embed2=discord.Embed(title="All birthdays", colour=discord.Colour.dark_gold())
		embed2.set_thumbnail(url="https://stickeramoi.com/8365-large_default/sticker-mural-couronne-jaune.jpg")
		for item in a[0:24]:
			date = datetime.datetime.strftime(item.date_of_birth, "%d %b %Y")
			embed.add_field(name=date, value=f"<@!{item.discord_id}>", inline=True)
			embed.set_footer(text="Demandé par : "+str(ctx.message.author.name)+" à " + Timer(), icon_url=ctx.message.author.display_avatar.url)
		for item in a[25::]:
			date = datetime.datetime.strftime(item.date_of_birth, "%d %b %Y")
			embed2.add_field(name=date, value=f"<@!{item.discord_id}>", inline=True)
			embed2.set_footer(text="Demandé par : "+str(ctx.message.author.name)+" à " + Timer(), icon_url=ctx.message.author.display_avatar.url)

		await ctx.send(embed=embed)
		await ctx.send(embed=embed2)

	@commands.command(name='mybirthday', aliases=['mbirth'])
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
				embed = discord.Embed(title=f"Mon age", description=message, color=0x12F932)

				embed.set_thumbnail(url="https://acegif.com/wp-content/gif/joyeux-anniversaire-chat-31.gif")

				embed.set_footer(text="Demandé par : "+str(ctx.message.author.name)+" à " +
							Timer(), icon_url=ctx.message.author.display_avatar.url)

				await ctx.send(embed=embed)

	@commands.command(name='lenstudent', aliases=['lens'])
	async def lenstudent(self, ctx):
		a = await database_connection()
		await ctx.send("Il y a ", len(a), "élèves qui sont enregistrés")

	@commands.command(name='registerbirthday', aliases=['rbirth'])
	@commands.cooldown(1, 30, commands.BucketType.user)
	async def registerbirthday(self, ctx, date_of_birth):
		name = ctx.message.author.name
		discord_id = ctx.message.author.id
		connection = await aiomysql.connect(host=data['dbhost'], user=data['dbuser'], password=data['dbpassword'], db=data['dbname'])
		cursor = await connection.cursor()
		user_to_add = [discord_id, date_of_birth]
		try:
			await cursor.execute("INSERT INTO `algobot_birthday`(`discord_id`, `date_of_birth`) VALUES (%s, %s)", user_to_add)
			await connection.commit()
			await ctx.send("Tu t'es bien enregistré !")
		except:
			raise commands.CommandError('La commande est mal écrite, ex : `rbirth 2002-12-20`')
  
	@commands.command(name='deletebirthday', aliases=['dbirth'])
	@commands.is_owner()
	async def deletebirthday(self, ctx, discord_id):
		connection = await aiomysql.connect(host=data['dbhost'], user=data['dbuser'], password=data['dbpassword'], db=data['dbname'])
		cursor = await connection.cursor()
		user_to_delete = [discord_id]
		await cursor.execute("DELETE FROM `algobot_birthday` WHERE `discord_id` = %s", user_to_delete)
		await connection.commit()
		await ctx.send("Tu as bien delete !")

	@commands.command(name='modifbirthday', aliases=['modbirth'])
	@commands.is_owner()
	async def modifbirthday(self, ctx, var, discord_id):
		connection = await aiomysql.connect(host=data['dbhost'], user=data['dbuser'], password=data['dbpassword'], db=data['dbname'])
		cursor = await connection.cursor()
		modiflist = [var, discord_id]
		await cursor.execute("UPDATE `algobot_birthday` SET `date_of_birth` = %s WHERE `discord_id` = %s", modiflist)
		await connection.commit()
		await ctx.send("Tu as bien modif !")


def setup(bot):
	bot.add_cog(Birthday(bot))