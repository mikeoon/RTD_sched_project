import numpy as np
from datetime import timedelta
import dictionary_maker as dm

number_captains = 38
tours_per_block = 12
blocks_per_day = 6
days = 7
max_days_worked = 3

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
# keys are days, values are (tours_per_block * blocks_per_day) indicies, each value giving how many captains per slot
t_per_slot = dm.tours_per_slot()

names, tours_unavailable, max_days_per_captain = dm.individual_constraints('CaptainConstraints.csv')

required_tours = dm.required_tours(number_captains)

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


# Used to check work days in a row
# passed in is a single captain
# not used right now, just alternating groups.
def days_worked_per_captain_constraint(capt_dict, captain, max_days_worked=4):
	day_count = 0
	for day in range(7): # for each day of the week
		# False = DON'T add timeslot on that day to current cap
		#if day_count > max_days_worked:
		#	return False
		if len(capt_dict[captain][day]) > 0:
			day_count += 1
	# if return True, POP
	return day_count > max_days_worked

	
# mike - not sure what this is for for now
def tours_per_day_constraint(capt_dict, captain, day, max_tours_day=5):
	# Pop if returns true
	return (len(capt_dict[captain][day]) > max_tours_day)

# Used to check tours per time 
def tours_per_time_slot_constraint(capt_dict, t_per_slot, day, timeslot):
	tour_count = 0
	for captain in range(len(capt_dict)):
		if timeslot in capt_dict[captain][day]:
			tour_count += 1

	return tour_count > t_per_slot[day][timeslot]	# True = pop


# Check number of captains per day
def capts_per_day_constraint(capt_dict, capt_lim_per_day, day):
	capt_count = 0
	for captain in range(len(capt_dict.keys())):
		if len(capt_dict[captain][day]) != 0:
			capt_count += 1

	# True = POP
	return capt_count > capt_lim_per_day[day]

# Used to check if captain is working in a timeslot already
def capt_block_constraint(captain_slot, tours_per_block, timeslot):
	if len(captain_slot) <= 1:
		# to catch index out of bounds, first check
		return False

	else:
		# True = pop the most recent time slot
		slot = captain_slot[0] % tours_per_block
		check_slot = timeslot % tours_per_block
		return slot != check_slot

def tours_unavailable_constraint(tours_unavailable, captain, day, timeslot):
	# POP if returns True
	return timeslot in tours_unavailable[captain][day]

def required_tour_constraint(required_tours, captain, day, timeslot):
	# Return True if the timeslot is a required tour
	return timeslot in required_tours[captain][day]

# Used to alternate groups:
def alternate_captains(capt_last_day):
	return  len(capt_last_day) == 0

def dict_to_matrix(cap_dict, number_captains = 1, tours_per_block = 12, blocks_per_day = 6, days = 7):
	# Puts the dictionary in matrix format.
	result = []
	for captain in range(number_captains):
		capt_temp = []
		for day in range(days):
			day_temp = [0] * (tours_per_block * blocks_per_day) #72
			for t in capt_dict[captain][day]:
				day_temp[t] = 1
			capt_temp.append(day_temp)
		capt_temp = np.hstack(capt_temp)
		result.append(capt_temp)
	return np.vstack(result)

def dict_to_schedule(capt_dict, names_dict, filename = 'test.csv', number_captains = 1, ours_per_block = 12, blocks_per_day = 6, days = 7):
	# Method to take in the captain dictionary and print out a csv file of a 
	# schedule in the same format as RTD currently does. 
	#
	#First, create a list with the timeslots for easy lookup.
	time_to_slot = []
	t = timedelta(minutes = 9*60)
	t_add = timedelta(minutes = 10)
	for i in range(tours_per_block * blocks_per_day):
		temp = ':'.join(str(t + i * t_add).split(':')[:2])
		time_to_slot.append(temp)
	# Now, put everythong together in a result list.
	result = []
	for captain in range(number_captains):
		capt_temp = []
		for day in range(days):
			day_temp = []
			for t in capt_dict[captain][day]:
				day_temp.append(time_to_slot[t])
			capt_temp.append(' '.join(day_temp))
		result.append(','.join(capt_temp))
	# Now, write the result list to a csv file
	with open(filename, 'w') as f:
		f.write('Captain, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday \n')
		counter = 0
		for line in result:
			f.write(names[counter] + ',' + line + '\n')
			counter += 1


# Main loops/iteration for creating schedule
for day in range(days):
	for captain in range(number_captains):
		for timeslot in range(tours_per_block * blocks_per_day):
			#if days_worked_per_captain_constraint(capt_dict[captain], max_days_worked):
			if day == 0 or alternate_captains(capt_dict[captain][day - 1]): # try to ge this to work without if statement
				# 1. give captain first timeslot in
				capt_dict[captain][day].append(timeslot)

				# for testing
				#if timeslot + (day * tours_per_block * blocks_per_day) >= 72:
					#print str(timeslot + (day * tours_per_block * blocks_per_day))

				# These are the constraints, if any constraint fails, booleans return TRUE to mean YES POP
				if capt_block_constraint(capt_dict[captain][day], tours_per_block, timeslot):
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
				break
				# this is where you're going to check for the individual. not yet implemented


#for i in range(len(capt_dict.keys())):
#for i in range(20):
#	print capt_dict[i]

#''np.savetxt('test.csv', dict_to_schedule(capt_dict, 40), delimiter = ',')
#np.savetxt('test_03082015.csv',  dict_to_matrix(capt_dict, 40), delimiter = ',')

dict_to_schedule(capt_dict, names_dict = names, filename = 'test.csv', number_captains = number_captains)
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