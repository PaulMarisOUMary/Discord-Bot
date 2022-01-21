#################################################
#						#
#  This Cog is made for Algosup Discord Bot	#
#   						#
#	By LavaL, creator of LavaL Bot		#
#						#
#################################################

from os import name
import time
import discord
import datetime
from datetime import date
from discord import user
from pytz import timezone
from discord.ext import commands, tasks
from discord import Member

class Student:
	def __init__(self, name, surname, user_id, dateofbirth, promo):
		self.name = name
		self.surname = surname
		self.user_id = user_id
		self.dateofbirth= dateofbirth
		self.promo = promo
	def __repr__(self):
		return repr((self.name, self.surname, self.user_id, self.dateofbirth, self.promo))

students = [
	# Class(Name, Surnane, discord_id, date of birth(year-month-day), Promo)
	Student("Nicolaon", "Romain", 405414058775412746, '2002-12-20', "Alpha"),
	Student("Diancourt", "Théo", 202041154231861248, '2004-04-21', "Beta"),
	Student("Chartier", "Léo", 283358054827819008, '2001-10-27', "Beta"),
	Student("Debry", "Robin", 692669442131492936, '2000-11-17', "Beta"),
	Student("Bobis", "Alexandre", 890238206103134238, '2003-08-18', "Beta"),
	Student("Gorin", "Pierre", 289689300574928897, '2004-03-21', "Beta"),
	Student("Mida", "Nicolas", 209765697188790272, '2001-11-09', "Beta"),
	Student("Archimbaud", "Malo", 231447375254781962, '2002-06-06', "Beta"),
	Student("Bernard", "Max", 627775366601113601, '2002-04-21', "Alpha"),
	Student("Le Brun", "Gaël", 217727048632762369, '2002-01-08', "Beta"),
	Student("Curel", "Clémentine", 755449654912614441, '1999-02-27', "Alpha"),
	Student("Caton", "Clément", 219156294974570497, '1999-04-02', "Alpha"),
	Student("Priol", "Eloi", 456516058984087583, '2003-05-11', "Alpha"),
	Student("De Lavenne", "Louis", 501471077709381643, '2002-07-27', "Alpha"),
	Student("Molnar", "Ivan", 267377288989900810, '1999-07-27', "Alpha"),
	Student("Bouquin", "Laurent", 248910730122756108, '2002-09-26', "Alpha"),
	Student("Fernandez", "Aurélien", 354321839234744320, '2002-10-23', "Alpha"),
	Student("Vinette", "Karine", 759045368591155221, '1985-11-13', "Alpha"),
	Student("Maris", "Paul", 265148938091233293, '2000-11-14', "Alpha"),
	Student("Namir", "Salaheddine", 436469556257619978, '1997-12-03', "Alpha"),
	Student("Trouvé", "Théo", 293476472767905792, '2001-12-18', "Alpha"),
	Student("Clément", "Quentin", 477507595402477568, "2003-11-26", "Beta"),
	Student("Chaput", "Mathieu", 274284070261882880, "2002-04-20", "Beta"),
	Student("Leroy", "Victor", 332519404308791297, "2004-07-08", "Beta"),
	Student("Gautier", "Elise", 890234516587839498, "2003-03-28", "Beta"),
	Student("Planchard", "Thomas", 300305011554910209, "2003-07-11", "Beta"),
	Student("Pages", "Maxime", 200894937330483201, "2002-04-20", "Beta"),
	Student("Riviere", "Guillaume", 157840464559472640, "1997-08-22", "Beta"),
	Student("Lorut-Gauriat", "Martin", 615932803439394817, "2000-07-05", "Alpha"),
	Student("Cuahonte", "David", 222030501005885461, "2002-12-20", "Beta"),
	Student("Lemoine", "Arthur", 294083746439626752, "2001-09-10", "Beta"),
	Student("Pillet", "Antonin", 303832553482092545, "2003-11-13", "Beta"),
	Student("Hureaux", "Florent", 267613920343228417, "1996-11-26", "Alpha")
]

def Timer():
	fmt = "%H:%M:%S"
	# Current time in UTC
	now_utc = datetime.datetime.now(timezone('UTC'))
	now_berlin = now_utc.astimezone(timezone('Europe/berlin'))
	actual_time = now_berlin.strftime(fmt)
	return actual_time


def Calcul_Age(birthDate):
	today = date.today() 
	age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
	return age
 

class Birthday(commands.Cog, name="birthday"):
	"""Birthday description"""
	def __init__(self, bot):
		self.bot = bot
		self.daily_birthday.start()

	def cog_unload(self):
		self.daily_birthday.cancel()


	@tasks.loop(hours=1)
	async def daily_birthday(self):
		guild = self.bot.get_guild(551753752781127680)
		channel = guild.get_channel(840003378062557202)
		is_nothing = True
		if datetime.datetime.now().hour == 9:
			for student in students:
				new_date = date.fromisoformat(student.dateofbirth)
				diff = Calcul_Age(new_date)
				if (new_date.month == date.today().month) and (new_date.day == date.today().day):
					message = ("Bon anniversaire **<@!" + str(student.user_id) + ">**, tu es né(e) le `" + str(new_date) + "` et tu as désormais " + str(diff) + " ans ! 🎉")

					embed = discord.Embed(title="Bon anniversaire !", colour=discord.Colour.dark_gold())
					embed.add_field(name="Wow c'est ton anniversaire aujourd'hui !", value=message, inline=False)
					embed.set_thumbnail(url="https://acegif.com/wp-content/gif/joyeux-anniversaire-chat-31.gif")
					await channel.send(embed=embed)
					is_nothing = False
     
			if is_nothing:
				await channel.send("Il n'y a pas d'anniversaire aujourd'hui :(")


	@daily_birthday.before_loop
	async def before_daily_birthday(self):
		await self.bot.wait_until_ready()

	@commands.command(name='birthdayall', aliases=['bda'])
	async def birthdayall(self, ctx):
		listofstudents = sorted(students, key=lambda student: student.dateofbirth)
		embed=discord.Embed(title="All birthdays", colour=discord.Colour.dark_gold())
		embed.set_thumbnail(url="https://stickeramoi.com/8365-large_default/sticker-mural-couronne-jaune.jpg")
		i = 0
		while i < len(students):
			embed.add_field(name=listofstudents[i].name + " " + listofstudents[i].surname, value=listofstudents[i].dateofbirth, inline=True)
			embed.set_footer(text="Demandé par : "+str(ctx.message.author.name)+" à " +
					Timer(), icon_url=ctx.message.author.display_avatar.url)
			i = i + 1
		await ctx.send(embed=embed)

	@commands.command(name='birthday', aliases=['birth'])
	async def birthday(self, ctx, member: Member = None):
		if not member:
			ID_discord = ctx.message.author.id
		else:
			ID_discord = member.id
		# ID_discord = ctx.message.author.id
		for student in students:
			if ID_discord == student.user_id:
				new_date = date.fromisoformat(student.dateofbirth)
				diff = Calcul_Age(new_date)
				message = "<@!" + str(student.user_id) + "> tu es agé(e) de " + str(diff) + " ans ! 🎉"
				embed = discord.Embed(title=f"Age de {student.surname}", description=message, color=0x12F932)
	
				embed.set_thumbnail(url="https://acegif.com/wp-content/gif/joyeux-anniversaire-chat-31.gif")
	
				embed.set_footer(text="Demandé par : "+str(ctx.message.author.name)+" à " +
						 Timer(), icon_url=ctx.message.author.display_avatar.url)
	
				await ctx.send(embed=embed)

	@commands.command(name='lenstudent', aliases=['lens'])
	@commands.is_owner()
	async def lenstudent(self, ctx):
		listofstudent = len(students)
		print(listofstudent)

def setup(bot):
	bot.add_cog(Birthday(bot))
