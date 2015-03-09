import numpy as np
import csv

def captain_dictionary(number_captains=1):
	d = dict()
	for i in range(number_captains):
		d[i] = [[], [], [], [], [], [], [], []]
	return d

def tours_per_slot(tours_per_block=12, blocks_per_day=6, days=7, filename=None):
	if filename is not None:
		# then read in the file and build the constraint
		1
	# Otherwise, use the schedule goven to us as an example.
	t_per_slot = dict()
	for day in range(days):
		temp = np.zeros(blocks_per_day * tours_per_block)
		# MAIN LOCATION SCHEDULE
		for i in range(2, 61, 2): temp[i] = 2
		# WESTAKE SCHEDULE (Use += rather than simply =)
		# 1 person starts at 9:30 and runs 5 tours
		for i in range(3, 52, 12): temp[i] += 1
		# 1 person starts at 10:30 and runs 5 tours
		for i in range(9, 58, 12): temp[i] += 1
		# 2 people start at 10 and 11, each and all 4 people run 5 tours each
		for i in range(6, 62, 6): temp[i] += 2
		# ON CALL (do this at a different time)
		# 1 on all at 10 and another at 11
		#temp[6] += 1
		#temp[12] += 1
		# Done with this day. 
		t_per_slot[day] = temp
	return t_per_slot

def max_days_per_captain(number_captains=1):
	max_days_per_captain = dict()
	# Otherwise, simply assume that the max is 4
	for i in range(number_captains):
		max_days_per_captain[i] = 4 # can be other than 4
	return max_days_per_captain

def required_tours(number_captains = 1, days = 7, filename=None):
	required_tours = dict()
	for i in range(number_captains):
		l = []
		for d in range(days):
			l.append([]) # non-empty for tours that are required 
		required_tours[i] = l # non-empty for tours that are required 
	if filename is not None:
		1 # Read in the constraints
	return required_tours

def tours_unavailable(number_captains=1, days=7):
	tours_unavailable = dict()
	for i in range(number_captains):
		l = []
		for d in range(days):
			l.append([]) # non-empty for unavailable tours/days
			# tours_unavailable[i][d] = range(72) if can't work all day
		tours_unavailable[i] = l
	return tours_unavailable

def individual_constraints(filename):
	names = dict()
	days_unavailable = dict()
	max_days_per_week = dict()
	# tear throuth the file, line by line
	with open(filename, 'rU') as f:
		f.readline() # first line is the header
		csv_reader = csv.reader(f)
		counter = 0
		for line in csv_reader:
			# Captain Name
			names[counter] = line[0]
			# Unavailability
			unavailable = line[1].lower().split(' ')
			# check each day to see if any are unavailable
			day_in_week = ['mon', 'tues', 'wed', 'thur', 'fri', 'sat', 'sun']
			temp = []
			for d in range(len(day_in_week)):
				if day_in_week[d] in unavailable:
					temp.append(range(72)) # can't work that day
				else:
					temp.append([])
			days_unavailable[counter] = temp
			# Max days in a single week
			max_days_per_week[counter] = int(line[2])
			counter += 1
	return names, days_unavailable, max_days_per_week