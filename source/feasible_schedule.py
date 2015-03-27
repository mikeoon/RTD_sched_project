import numpy as np
from datetime import timedelta
import dictionary_maker as dm

number_captains = 39
tours_per_block = 12
blocks_per_day = 6
days = 7

################################### TO DO ######################################
## Implement Constraints
## 	- Unable to work (certain times or shifts)
## 	- Has to work specific shift
## Implement Interface
##		- Input 
##  	- Output to csv/excel format (Done)


# initialize a dictionary of start times
# keys are captain, values are list of 7 lists, each of the 7 lists are days of the week. Those values are time slots on that day
capt_dict = dm.captain_dictionary(number_captains)

# need to set which days need x amount of tours
# keys are days, values are (tours_pser_block * blocks_per_day) indicies, each value giving how many captains per slot
t_per_slot = dm.tours_per_slot()

names, tours_unavailable, max_days_per_captain = dm.individual_constraints('CaptainConstraints.csv')

required_tours = dm.required_tours_from_file(names, 'RequiredTours.csv', number_captains, tours_per_block, blocks_per_day)

#required_tours = dm.required_tours(number_captains)

# sets the number of captains per day: default 20
# each index is a different day: index 0 = monday, index 1 = tuesday, etc.
capt_lim_per_day = [18] * 7


########################## INDIVIDUAL CONSTRAINTS ##############################
## INEQUALITY CONSTRAINTS --
## 1) Days worked per captian constraint. (No more than 4 perweek)
## 2) Start times per day constraint. (No more than once per day)
## 3) Unable to work constraint. (Can't work specific days)
## 4) Has to work specific shift constraint. (Some shifts are requested)
## EQUALITY CONSTRAINTS --
## 5) Tours per timeslot constraint. (Specified by the user, usually 1-3)
## 6) Captains per day constraint. (Specified by the user, usually 20)


def days_worked_per_captain_constraint(capt_dict, captain, max_days_worked=4):
	# Checks to see if a captain is working more than four days in a week.
	#
	# Params:
	# 		capt_dict: Dictionary of captains. Each value is a list of 7 lists. 
	#                Each of the sublists consists of the tour times a captain 
	# 					  runs. 
	#		captain: The number of the captain. This is the key to capt_dict.
	#     max_days_worked: The maximum number of days worked a captain can 
	# 							  work in a week.
	# Returns:
	# 		True if the constraint is violated.
	day_count = 0
	for day in range(7): # for each day of the week
		if len(capt_dict[captain][day]) > 0:
			day_count += 1 # count number of days with a shift
	return day_count > max_days_worked

def tours_per_day_constraint(capt_dict, captain, day, max_tours_day=5):
	# Checks to see if a Captain has been scheduled for too many tours in a day.
	#
	# Params:
	# 		capt_dict: Dictionary of captains. Each value is a list of 7 lists. 
	#                Each of the sublists consists of the tour times a captain 
	# 					  runs.
	# 		captain: The number of the captain. This is the first key to the 
	#					captain dictionary.
	#     day: The day number (0-6). This is the second key to the captain
	# 			  dictionary. Monday is 0.
	#		max_tours_day: Maximum number of tours in a day (usually 5).
	# Returns:
	#		True if the constraint is violated.
	return (len(capt_dict[captain][day]) > max_tours_day)

def tours_per_time_slot_constraint(capt_dict, t_per_slot, day, timeslot):
	# Checks to see if the number of tours RTD wants to run in a particular 
	# timeslot is violated. Currently, it only checks if we've overscheduled
	# a particular timeslot. 
	#
	# Params:
	# 		capt_dict: Dictionary of captains. Each value is a list of 7 lists. 
	#                Each of the sublists consists of the tour times a captain 
	# 					  runs.
	#		t_per_slot: Dictionary of the number of tours we want to run at a 
	# 						particular timeslot on a cetrain day. Each value is 
	# 						a list of lists. Each sublist is of length 72 because of 
	#                 the number of timeslots in a single day.
	#		day: The day of the week (0-6). Monday is 0.
	#		timeslot: The timeslot on any given day (0-71).
	# Returns:
	#		True if the constraint is violated.
	tour_count = 0
	for captain in range(len(capt_dict)):
		if timeslot in capt_dict[captain][day]:
			tour_count += 1
	return tour_count > t_per_slot[day][timeslot]

def capts_per_day_constraint(capt_dict, capt_lim_per_day, day):
	# Checks to see if we've scheduled too many captains in a given day. 
	#
	# Params: 
	# 		capt_dict: Dictionary of captains. Each value is a list of 7 lists. 
	#                Each of the sublists consists of the tour times a captain 
	# 					  runs.
	#		capt_lim_per_day: Dictionary of the maximum number of captains we can
	# 								schedule in any given day. Key is the day and value 
	#								value is the max captains for that day. 
	#		day: The day of the week (0-6). Monday is 0.
	# Returns:
	#		True if constraint is violated.
	capt_count = 0
	for captain in range(len(capt_dict.keys())):
		if len(capt_dict[captain][day]) != 0:
			capt_count += 1
	return capt_count > capt_lim_per_day[day]

def capt_block_constraint(capt_dict, captain, day, tours_per_block=12):
	# Checks to make sure that a Captain doesn't run multiple tours in 
	# a given day.
	#
	# Params:
	# 		capt_dict: Dictionary of captains. Each value is a list of 7 lists. 
	#                Each of the sublists consists of the tour times a captain 
	# 					  runs.
	# 		captain: The number of the captain. This is the first key to the 
	#					captain dictionary.
	#     day: The day number (0-6). This is the second key to the captain
	# 			  dictionary. Monday is 0.
	#		tours_per_block: Number of potential tour time slots in a 2-hour block. 
	#							  Default is 12 since we run every 10 minutes. 
	# Returns:
	# 		True if the constraint is violated.
	l = sorted(capt_dict[captain][day])
	for i in range(len(l)):
		for j in range(i + 1, len(l)):
			if abs(l[i] - l[j]) < tours_per_block:
				return True
	return False

def tours_unavailable_constraint(tours_unavailable, captain, day, timeslot):
	# Checks to see if a Captain is unavailable to run a tour. Currently, this
	# is begin used to make sure a Captain is not scheduled on their day off. 
	#
	# Params: 
	# 		tours_unavailable: Dictionary of the form X[captain][day] that says
	#								 which tours a captain cannot work. 
	# 		captain: The number of the captain. This is the first key to the 
	#					tours unavailable dictionary.
	#     day: The day number (0-6). This is the second key to the tours 
	#			  unavailable dictionary. Monday is 0.
	#		timeslot: The timeslot in the day (0-71).
	# Returns:
	#		True if the constraint is violated. 
	return timeslot in tours_unavailable[captain][day]

def main_constraints(capt_dict, captain, day, timeslot, tours_per_block, 
							t_per_slot, capt_lim_per_day, tours_unavailable):
	if capt_block_constraint(capt_dict, captain, day, tours_per_block):
		return True
	elif tours_per_time_slot_constraint(capt_dict, t_per_slot, day, timeslot):
		return True
	elif capts_per_day_constraint(capt_dict, capt_lim_per_day, day):
		return True
	elif days_worked_per_captain_constraint(capt_dict, captain, max_days_per_captain[captain]):
		return True
	elif tours_per_day_constraint(capt_dict, captain, day, 5):
		return True
	elif tours_unavailable_constraint(tours_unavailable, captain, day, timeslot):
		return True
	return False

def required_tour_constraint(required_tours, captain, day, timeslot):
	# Return True if the timeslot is a required tour
	return timeslot in required_tours[captain][day]


################################ MAIN LOOPS ####################################


# First, put the required tours in the schedule and fill out from there.
for captain in range(number_captains):
	capt_dict[captain] = required_tours[captain]
	# check each day to see when the captain's have required tours
	for day in range(days):
		if len(capt_dict[captain][day]) != 0:
			# get first tour and add new tours based on the first time slot's
			# block position.
			l = sorted(capt_dict[captain][day])
			time1 = l[0] % tours_per_block # gets block posiiton
			potentials = [time1 + tours_per_block*i for i in range(5)] # get potential tours that the captain can run 
			# 'potentials' is a list of potential time slots that are 2 hours apart
			for timeslot in potentials:
				if timeslot > tours_per_block * blocks_per_day:
					break # out of bounds timeslot (> 72)
				elif len(capt_dict[captain][day]) < 5: # captain does not have a full day
					capt_dict[captain][day].append(timeslot)
					if capt_block_constraint(capt_dict, captain, day, tours_per_block):
						capt_dict[captain][day].pop()
					elif tours_per_time_slot_constraint(capt_dict, t_per_slot, day, timeslot):
						capt_dict[captain][day].pop()
					elif capts_per_day_constraint(capt_dict, capt_lim_per_day, day):
						capt_dict[captain][day].pop()
					elif tours_per_day_constraint(capt_dict, captain, day, 5):
						capt_dict[captain][day].pop()
					elif tours_unavailable_constraint(tours_unavailable, captain, day, timeslot):
						capt_dict[captain][day].pop()

#dm.dict_to_schedule(capt_dict, names_dict = names, filename = 'test.csv', number_captains = number_captains)

# Main loops/iteration for creating schedule
for day in range(days):
	for captain in range(number_captains):
		for timeslot in range(tours_per_block * blocks_per_day):
			#if days_worked_per_captain_constraint(capt_dict[captain], max_days_worked):
			if day == 0 or len(capt_dict[captain][day - 1]) == 0: # try to ge this to work without if statement
			#if len(required_tours[captain][day]) != 0:
				# 1. give captain first timeslot in
				capt_dict[captain][day].append(timeslot)

				if capt_block_constraint(capt_dict, captain, day, tours_per_block):
					capt_dict[captain][day].pop()
				elif tours_per_time_slot_constraint(capt_dict, t_per_slot, day, timeslot):
					capt_dict[captain][day].pop()
				elif capts_per_day_constraint(capt_dict, capt_lim_per_day, day):
					capt_dict[captain][day].pop()
				elif tours_per_day_constraint(capt_dict, captain, day, 5):
					capt_dict[captain][day].pop()
				elif days_worked_per_captain_constraint(capt_dict, captain, max_days_per_captain[captain]):
					capt_dict[captain][day].pop()
				elif tours_unavailable_constraint(tours_unavailable, captain, day, timeslot):
					capt_dict[captain][day].pop()
			else:
				break # go on to the next day

# Main loops/iteration for creating schedule
for day in range(days):
	for captain in range(number_captains):
		for timeslot in range(tours_per_block * blocks_per_day):
			capt_dict[captain][day].append(timeslot)

			if capt_block_constraint(capt_dict, captain, day, tours_per_block):
				capt_dict[captain][day].pop()
			elif tours_per_time_slot_constraint(capt_dict, t_per_slot, day, timeslot):
				capt_dict[captain][day].pop()
			elif capts_per_day_constraint(capt_dict, capt_lim_per_day, day):
				capt_dict[captain][day].pop()
			elif tours_per_day_constraint(capt_dict, captain, day, 5):
				capt_dict[captain][day].pop()
			elif days_worked_per_captain_constraint(capt_dict, captain, max_days_per_captain[captain]):
				capt_dict[captain][day].pop()
			elif tours_unavailable_constraint(tours_unavailable, captain, day, timeslot):
				capt_dict[captain][day].pop()
		else:
			break # go on to the next day

#for i in range(len(capt_dict.keys())):
#for i in range(20):
#	print capt_dict[i]
dm.dict_to_schedule(capt_dict, names_dict = names, filename = 'test.csv', number_captains = number_captains)
#test = convert_to_matrix(capt_dict, 40)
#np.savetxt('test1.csv', test, delimiter=',')

######################## FEASIBLE SOLUTION ALGORITHM ###########################
## 1) Initialize captain dictionary.
## 1)* Initialize captains who have to work specific tours first before 
##    initializing everyone else. (Implement this last).
## 2) First, look at day 1.
##    (a) Choose the first 20 captains from the list (or however many are needed
##        that day) and plug them into spots so that all of the tours per time
##			 slot constraints are solved. (Thus, equality constraints are satisfied
## 		 for that day).
##    (b) For every captain whose individual constraints are violated, swap them
##        around with a captain who hasn't been assigned to that day. Do this 
##        until all individual constraints are satisfed. Note that the constriant
##        requiring certain captains to work on specific time slots will have to
##        be solved by initializing them first. 
## 3) Repeat (2) for every day 1,...,7. 

## Scheme:
## Run with ideal constraints (switching every day, etc)
## Then run without switiching to fill in gaps
## Then run with relaxed constraints to completely fill in gaps
## Assign on call shifts last since they have separate constraints 
## (i.e. don't count as a work day and some peole don't want them)