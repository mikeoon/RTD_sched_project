import numpy as np

number_captains = 40
tours_per_block = 12
blocks_per_day = 6
days = 7
max_days_worked = 3

# initialize a dictionary of start times
# keys are captain, values are list of 7 lists, each of the 7 lists are days of the week. Those values are time slots on that day
capt_dict = dict()
for captain in range(number_captains):
	# empty schedule for each day
	capt_dict[captain] = [[], [], [], [], [], [], []] # could be a list of 7 lists, 1 per day

# need to set which days need x amount of tours
# keys are days, values are (tours_per_block * blocks_per_day) indicies, each value giving how many captains per slot
t_per_slot = dict()
for day in range(days):
	# these are ndarrays, may want to think about another structure
	# at least 1 captain per day
	t_per_slot[day] = np.ones(blocks_per_day * tours_per_block * days) * 2



# sets the number of captains per day: default 20
# each index is a different day: index 0 = monday, index 1 = tuesday, etc.
capt_lim_per_day = [20, 20, 20, 20, 20, 20, 20]


#capt_dict[1] = [373, 72, 90, 1]

########################## INDIVIDUAL CONSTRAINTS ##############################
## INEQUALITY CONSTRAINTS --
## 1) Days worked per captian constraint. (No more than 4 perweek)
## 2) Start times per day constrain. (No more than once per day)
## 3) Unable to work constraint. (Can't work specific days)
## 4) Has to work specific shift constraint. (Some shifts are rquested)
## EQUALITY CONSTRAINTS --
## 5) Tours per timeslot constraint. (Specified by the user, usually 1-3)
## 6) Captains per day constraint. (Specified by the user, usually 20)


# Used to check work days in a row
# passed in is a single captain
# not used right now, just alternating groups.
def days_worked_per_captain_constraint(captain, max_days_worked):
	day_count = 0
	for day in range(len(captain)):
		# False = DON'T add timeslot on that day to current cap
		#if day_count > max_days_worked:
		#	return False

		if len(captain[day]) > 0:
			day_count += 1
		else:
			day_count = 0

		if day_count > max_days_worked:
			return False

	return True	# True = add timeslots for that day
	
# mike - not sure what this is for for now
def start_times_per_day_constraint(capt_dict, captain):
	# check difference in ordered values
	# should be >= 72
	# returns True if satisfied
	vals = sorted(capt_dict[captain])
	diff = [x - vals[i - 1] for i, x in enumerate(vals)][1:]
	for elem in diff:
		if elem < 72:
			return False
	return True

# mike - not sure what this is for for now
def unable_to_work_constraint(capt_dict, captain, shifts_unable_to_work):
	return 1

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

# Used to alternate groups:
def alternate_captains(capt_last_day):
	return  len(capt_last_day) == 0

# not yet complete, doesn't get all values
def convert_to_matrix(cap_dict, number_captains = 1, tours_per_block = 12, blocks_per_day = 6, days = 7):
	# create first matrix to stack on
	sched_matrix = np.zeros(tours_per_block * blocks_per_day * days)
	for day in range(len(cap_dict[0])):
		#print type(cap_dict[0])
		sched_matrix[cap_dict[0][day]] = 1
	sched_matrix = np.matrix(sched_matrix)

	for captain in range(number_captains - 1):
		temp_row = np.zeros(tours_per_block * blocks_per_day * days)
		for day in range(days - 1):
			temp_row[cap_dict[captain+1][day]] = 1
		temp_row = np.matrix(temp_row)
		sched_matrix = np.vstack((sched_matrix, temp_row))
	return sched_matrix



# Main loops/iteration for creating schedule
for day in range(days):
	for captain in range(number_captains):
		for timeslot in range(tours_per_block * blocks_per_day):
			#if days_worked_per_captain_constraint(capt_dict[captain], max_days_worked):
			if day == 0 or alternate_captains(capt_dict[captain][day - 1]):
				# 1. give captain first timeslot in
				capt_dict[captain][day].append(timeslot + (day * tours_per_block * blocks_per_day))

				# for testing
				#if timeslot + (day * tours_per_block * blocks_per_day) >= 72:
					#print str(timeslot + (day * tours_per_block * blocks_per_day))

				# These are the constraints, if any constraint fails, booleans return TRUE to mean YES POP
				if capt_block_constraint(capt_dict[captain][day], tours_per_block, (timeslot + (day * tours_per_block * blocks_per_day))):
					capt_dict[captain][day].pop()

				elif tours_per_time_slot_constraint(capt_dict, t_per_slot, day, (timeslot + (day * tours_per_block * blocks_per_day))):
					capt_dict[captain][day].pop()

				elif capts_per_day_constraint(capt_dict, capt_lim_per_day, day):
					capt_dict[captain][day].pop()
			else:
				break
				# this is where you're going to check for the individual. not yet implemented


for i in range(len(capt_dict.keys())):
#for i in range(20):
	print capt_dict[i]

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
