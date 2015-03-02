import numpy as np
import math
import Queue as Q
import matrix_maker as mm


def days_worked_per_captain_constraint(capt_dict, captain, max_days_worked):
	# return true of comstraint is violated
	return len(capt_dict[captain]) > max_days_worked

def start_times_per_day_constraint(capt_dict, captain, Psi_matrix):
	# get the start times for the captain and check that they are not working
	# more than once per day
	# return true if constraint is violated
	captain_start_times = mm.convert_to_vector(capt_dict, captain = captain)
	one_vec = np.ones(len(captain_start_times))
	return sum((Psi_matrix * captain_start_times > np.ones(7))) != 0

def individual_constraints_satisfied(capt_dict, captain, max_days_worked, Psi_matrix):
	# returns true if all constraints are satisfied
	l = []
	l.append(days_worked_per_captain_constraint(capt_dict, captain, max_days_worked))
	l.append(start_times_per_day_constraint(capt_dict, captain, Psi_matrix))
	# if all constraints satisfied, the sum of the list will be 0
	return sum(l) == 0

def tours_per_time_slot_constraint(capt_dict, time_slot_constraints, total_tours_mat):
	# return true if constraint is satisfied
	sched_vec = mm.convert_to_vector(capt_dict, number_captains = len(cap_dict))
	tours_per_time_slot =  total_tours_mat * sched_vec # ttm is equality matrix
	return tours_per_time_slot == time_slot_constraints

def number_daily_captains_constraint(capt_dict, number_daily_captains_constraint, M_matrix):
	# return true if constraint is satisfied
	sched_vec = mm.convert_to_vector(capt_dict, number_captains = len(cap_dict))
	return (M_matrix * sched_vec) == np.matrix(number_daily_captains_constraint).T

def equality_constraints_satisfied(capt_dict, time_slot_constraints, 
	number_daily_captains_constraint, total_tours_mat, M_matrix, day):
	tptsc = tours_per_time_slot_constraint(capt_dict, tours_timeslot_vec, tours_timeslot_mat)
	# however, we only want this day's constraints
	tptsc = tptsc[(day * tours_per_block * blocks_per_day):((day + 1) * tours_per_block * blocks_per_day)]
	# second, how captains are working this day
	ndcc = number_daily_captains_constraint(capt_dict, daily_captains_constraint, M_matrix)
	# however, we only want this day's constriants
	ndcc = ndcc[day]
	return (sum(tptsc) == len(tptsc)) and (ndcc == True)

# REMEBER: zero indexed, captain 1 = x_0

# set variables, change if needed
number_captains = 40
tours_per_block = 12
blocks_per_day = 6
days = 7
max_days_worked = 4


# creates list for ALL time slots, 7k
slots = range(tours_per_block * blocks_per_day * days)
#for i in range(tours_per_block * blocks_per_day * days):
	#slots.append(i)

# keeps track of which captain has which slots (to start?)
cap_dict = []
for i in range(number_captains):
	cap_dict.append((i, []))
cap_dict = dict(cap_dict)

Psi_matrix = mm.build_psi_matrix()
total_tours_mat = mm.build_equality_matrix(number_captains)
eq_vec = mm.build_equality_constraint_vect(number_captains)
M_matrix = mm.build_M_matrix(number_captains)

#print days_worked_per_captain_constraint(cap_dict, 1, 4)
#print start_times_per_day_constraint(cap_dict, 1, Psi_matrix)
#print tours_per_time_slot_constraint(cap_dict, eq_vec, total_tours_mat)[:72].sum()
#print individual_constraints_satisfied(cap_dict, 1, 4, Psi_matrix)
#print
#print number_daily_captains_constraint(cap_dict, (np.ones(days) * 20), M_matrix)

def build_feasible_schedule(number_captains = 1, tours_per_block = 12, 
										blocks_per_day = 6, days = 7, max_days_worked = 4, 
										daily_captains_constraint = None):
	# build some of the important matrices
	Psi_matrix = mm.build_psi_matrix()
	tours_timeslot_mat = mm.build_equality_matrix(number_captains)
	tours_timeslot_vec = mm.build_equality_constraint_vect(number_captains)
	M_matrix = mm.build_M_matrix(number_captains)
	if daily_captains_constraint == None:
		daily_captains_constraint = np.ones(7) * 20

	# build a dictionary of captain's start times (initialize as empty dict of empty lists)
	capt_dict = dict()
	for i in range(number_captains):
		capt_dict[i] = []

	for day in range(days):
		for captain in range(number_captains):
			for timeslot in range(tours_per_block * blocks_per_day):
				prev = cap_dict[captain] # save the previous schedule
				# add in the new timeslot
				capt_dict[captain].append(timeslot + (day * tours_per_block * blocks_per_day))
				# if this new addition does not violate the captain's constraint, 
				# keep it and exit this for loop
				if individual_constraints_satisfied(capt_dict, captain, max_days_worked, Psi_matrix):
					break
				else: # otherwise, run the loop again
					capt_dict[captain] = prev
			# check to see if this day's constraints are satisfied
			# first, tours per time slot
			tptsc = tours_per_time_slot_constraint(capt_dict, tours_timeslot_vec, tours_timeslot_mat)
			# however, we only want this day's constraints
			tptsc = tptsc[(day * tours_per_block * blocks_per_day):((day + 1) * tours_per_block * blocks_per_day)]
			# second, how captains are working this day
			ndcc = number_daily_captains_constraint(capt_dict, daily_captains_constraint, M_matrix)
			# however, we only want this day's constriants
			ndcc = ndcc[day]
			if (sum(tptsc) == len(tptsc) and ndcc == True):
				break
	return capt_dict


result = build_feasible_schedule(number_captains, tours_per_block, blocks_per_day, days, max_days_worked, (np.ones(days) * 20))
for i in result.keys():
	print result[i]

x_feasible = mm.convert_to_vector(result, number_captains)
#print x_feasible

ineq_matrix = mm.build_inequality_matrix(number_captains)
ineq_constraint_matrix = mm.build_inequality_constraint_vect(number_captains)
#print ((ineq_matrix * x_feasible) <= ineq_constraint_matrix)
# tours per time slot equality constraint
equal_matrix = mm.build_equality_matrix(number_captains)
equal_constraint_matrix = mm.build_equality_constraint_vect(number_captains)
#print (equal_matrix * x_feasible) == equal_constraint_matrix
################################################################################

# captain queue, allows for captains to get an even share of shifts
cap_q = Q.Queue()
for i in range(number_captains):
	cap_q.put(i)


constraint = True # for testing... need to implement this

while len(slots) != 0:
	# captain currently on
	cap = cap_q.get()
	cap_q.put(cap)
	#constraint = True # for testing
	if constraint:
		if slots[0] not in cap_dict.values():
			cap_dict[cap].append(slots[0])
			#constraint = False # for testing
		# Here, check to see if new values are valid with constraints SO FAR
		# If fails, just throw next captain in
		if not constraint:
			temp = cap_dict[cap][-1]
			del cap_dict[cap][-1]
			cap = cap_q.get()
			print cap # TESTING
			cap_q.put(cap)
			cap_dict[cap].append(slots[0])
	del slots[0]

# For testing
#for i in range(number_captains):
#	print cap_dict[i]


#test1 = mm.convert_to_vector(cap_dict, number_captains)
#np.savetxt('test1.csv', test1, delimiter=',')


###################################################################################################################

# FAILED RECURSION ATTEMPT DOES NOT WORK. -- just kept it incase we wanted to use recursion
def bnb_test(slots, cap_dict, back_track, cap_q):
	if len(slots) == 0:
		return slots
	# First step left
	if slots[0] not in cap_dict.values():
		temp = cap_q.get()
		cap_q.put(temp)
		cap_dict[temp].append(slots[0])
		del slots[0]
		slots = bnb_test(slots, cap_dict, back_track, cap_q)
	# for stepping right
	if back_track:
		cap_dict[0]
		slots = bnb_test(slots, cap_dict, back_track, cap_q)
	# this is for stepping left in the tree
