### Uses a simple rule-based approach to parse user-provided locations (e.g. from Twitter)

import string
import csv
import re

class location():

	aliases = {}
	countries = []
	states_and_abbrevs = {}
	state_nicknames = {}
	states_biggest_cities = {}
	USA_major_cities = {}
	USA_places = {}
	world_cities = {}

	# Countries that should be in all CAPS:
	specials = ['usa', 'uk']

	def __init__(self, input_str):

		self.input = input_str
		self.parsed = []
		self.final = dict.fromkeys(['city', 'state', 'country'])

	def preprocess(self):
		self.input = self.input.lower()

		url = re.compile('(www)\..+\.[\w]{2,}')
		email = re.compile('^\w+@\w+\.\w{2,}')
		threepeat = re.compile('([a-zA-Z])\\1{2,}')

		if url.search(self.input): self.input = 'GENERICURL'
		if email.search(self.input): self.input = 'GENERICEMAIL'
		self.input = re.sub('([a-zA-Z])\\1{2,}', r'\1', self.input)

		# convert all punctuation to white space (not ideal):
		self.input = [' ' if c in list(string.punctuation) else c for c in self.input]
		# remove all numbers:
		self.input = ''.join([i for i in self.input if not i.isdigit()])
		# remove trailing and duplicate whitespace:
		self.input = ' '.join(self.input.split())

		# add whitespace around string so functions below can find it:
		self.input = ' '+self.input+' '
		# St and Ft?

	def parse(self):

		if self.input is None:
			return -1

		# split string into a list of strings:
		self.parsed = self.input.split()

		self.is_alias()
		self.is_country()
		# check for state_abbrev first, so that oklahoma city, ok
		# isn't thrown out as just oklahoma:
		self.is_state_abbrev()
		self.is_state()
		self.is_state_nickname()
		self.is_major_city()
		self.is_world_city()
		self.is_place()


	def update(self, substr):
		self.parsed = [s for s in self.parsed if s not in substr.split()]
		self.input = ' '.join(self.parsed)
		self.input=' '+self.input+' '

	def is_alias(self):
		for a in location.aliases.keys():
			if self.input.find(' '+a+ ' ')!=-1:
				#split_a = a.split()
				#self.parsed=[l for l in self.parsed if l not in split_a]
				# Throw the 'proper' name to which the alias refers back onto
				# the place name, and send it back to be processed as normal.
				# Since these placenames are being treated as a 'bag of words'
				# and are thus orderless, the new place word can just be appended
				# to the end:
				self.update(a)
				self.parsed.append(location.aliases[a])
				self.input = ' ' + ' '.join(self.parsed) + ' '

	# if it detects foreign country, one option is to have it return whatever
	# occurs prior as place name.
	def is_country(self):
		for c in location.countries:
			if self.input.find(' '+c+' ')!=-1:
				self.final['country'] = c.title() if c not in location.specials else c.upper()
				self.update(c)
				return

	def is_state_abbrev(self):
		for a in location.states_and_abbrevs.values():
			if self.input.find(' '+a+' ')!=-1:
				self.final['state'] = a.upper()
				self.update(a)
				return

	def is_state(self):
		if self.final['state'] is not None: return

		for s in location.states_and_abbrevs.keys():
			if self.input.find(' '+s+' ')!=-1:
				# Convert state to abbreviation:
				self.final['state']=location.states_and_abbrevs[s].upper()
				self.update(s)
				return

	def is_state_nickname(self):

		if self.final['state'] is not None: return

		for n in location.state_nicknames.keys():
			if self.input.find(' '+n+' ')!=-1:
				self.final['state'] = location.state_nicknames[n].upper()
				self.update(n)
				return

	def is_major_city(self):
		for m in location.USA_major_cities.keys():
			if self.input.find(' '+m+' ')!=-1:
				print "HERE 2"
				self.final['city'] = m.title()
				if self.final['state'] is None:
					self.final['state'] = location.USA_major_cities[m].upper()
				self.update(m)
				return

	def is_world_city(self):

		# look up returning no value
		if self.final['country'] == 'usa':
			return

		for w in location.world_cities.keys():
			if self.input.find(' '+w+' ') != -1:
				self.final['city']=w.title()
				if self.final['country'] is None:
					self.final['country'] = location.world_cities[w].title()
				self.update(w)
				return			

	def is_place(self):

		if self.final['city'] is not None:
			return
		for (p, s) in location.USA_places:
			# look up find:  ##
			if self.input.find(' '+p+' ')!=-1:
				self.final['city'] = p.title()
				if self.final['state'] is None:
					self.final['state'] = location.states_and_abbrevs[s].upper()
					#self.final['state'] = location.states_and_abbrevs[location.USA_places[p]].upper()  # see if there's ever possibility of a conflict here
				self.update(p)
				return

def prep(line):

		line=line.lower()

		punct = list(string.punctuation)  # might not need it to be list
		# convert all punctuation to white space (not ideal):
		line = [' ' if c in punct else c for c in line]
		# remove all numbers:
		line = ''.join([i for i in line if not i.isdigit()])
		# remove trailing and duplicate whitespace:
		line = ' '.join(line.split())

		return line

def main():
	

	with open('aliases.csv') as f:
 		csv_r = csv.reader(f)
		location.aliases = {prep(line[0]): prep(line[1]) for line in csv_r}

	with open('countries.csv') as f:
		for line in iter(f.readline, ''):
			location.countries.append(prep(line))

	with open('states.csv') as f:
		states_temp = []
		for line in iter(f.readline, ''):
			states_temp.append(prep(line))

	with open('state_abbrevs.csv') as f:
		abbrevs_temp = []
		for line in iter(f.readline, ''):
			abbrevs_temp.append(prep(line))

	location.states_and_abbrevs = {s: a for s,a in zip(states_temp, abbrevs_temp)}

 	with open('state_nicknames.csv') as f:
 		csv_r = csv.reader(f)
 		location.state_nicknames = {prep(line[0]):prep(line[1]) for line in csv_r}

 	with open('state_biggest_cities.csv') as f:
 		csv_r = csv.reader(f)
 		location.states_biggest_cities = {prep(line[0]):prep(line[1]) for line in csv_r}

 	with open('USA_major_cities.csv') as f:
 		csv_r = csv.reader(f)
 		location.USA_major_cities = {prep(line[0]):prep(line[1]) for line in csv_r}

 	print location.USA_major_cities
 	with open('USA_places.csv') as f:
 		csv_r = csv.reader(f)
 		temp_places = {prep(line[0]):prep(line[1]) for line in csv_r}
 	location.USA_places = [(place,temp_places[place]) for place in sorted(temp_places.keys(), key=len, reverse=True)]

 	with open('world_cities.csv') as f:
 		csv_r = csv.reader(f)
 		location.world_cities = {prep(line[0]):prep(line[1]) for line in csv_r}
  
  list_of_dirty_locs = []

 	# Read in locations to be regularized. This is assuming that each
 	# location occupies its own line of a text file. The following line
 	# can be tweaked to allow for whatever input method you want.

 	with open('my_unclean_file.txt') as f:
 		for line in iter(f):
 			list_of_dirty_locs.append(line)

 	cleaned_locs = []
 	junk_locs = []

 	# Here's where the processing begins:
 	for line in list_of_dirty_locs:

 		loc = location(line)
 		loc.preprocess()
 		loc.parse()

 		# concatenate final string together
 		if loc.final['country'] == 'usa' and loc.final['state'] == None and loc.final['city'] == None:
 			loc.final['city'] = '[UNKNOWN]'

 		if all(v is None for v in loc.final.values()):
 			# The location parser didn't find anything that looked like a location
 			# Stick the original string into a file to see why it fell through:
 			junk_locs.append(loc.input)
 		
 		if loc.final['state'] is not None and loc.final['city'] is None:
 			state = loc.final['state']
			loc.final['city'] = location.states_biggest_cities[prep(state)].title()

 		output_string = ', '.join([l for l in loc.final.values() if l is not None])

 		if len(output_string) > 0:
 			cleaned_locs.append(output_string)

 		print "Cleaned:"
 		print cleaned_locs, '\n'
 		print "Junk:"
 		print junk_locs


if __name__ == '__main__':
	try:
		main()
	except Exception, ec:
		print ec
