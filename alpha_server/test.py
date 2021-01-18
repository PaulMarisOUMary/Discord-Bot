from datetime import datetime
from googletrans import Translator

def whoisnext():
	now = datetime.now()
	data = [datetime(2020, 10, 16), datetime(2020, 10, 23), datetime(2020, 11, 6), datetime(2020, 11, 13), datetime(2020, 11, 20), datetime(2020, 11, 27), datetime(2020, 12, 4)]
	guys = ["Théo Jules", "Paul Steevy", "Salah Karine", "Laura-lee Clément", "Louis Florent", "Martin Laurent", "Aurélien Eric"]
	daysresult = []

	for i in data:
		difference = i-now
		if not difference.days < 0:
			daysresult.append(difference.days)
	return guys[len(data)-len(daysresult)]

def getMissingChannel():
	actual, missing, normal = [], [], []
	for ch in channels:
		num = ch['name'].partition(' ')
		if num[-1].isdigit():
			actual.append(int(num[-1]))
	actual = sorted(actual)
	if len(actual) < 1: missing.append(1)
	else : [normal.append(x) for x in range(1, actual[-1]+1)]

	for i, no in enumerate(normal):
		if i < len(actual):
			if no != actual[i] and no not in actual:
				missing.append(no)
		elif no not in actual:
			missing.append(no)

	if len(missing) < 1: missing.append(actual[-1]+1)

	return missing[0]

translator = Translator()
tt = translator.detect("hello")
out = translator.translate('bonsoir', dest='en', src='fr').text
print(out, tt)