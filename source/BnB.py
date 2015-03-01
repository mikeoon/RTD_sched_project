import numpy as np
import math
import Queue as Q
import matrix_maker as mm

# REMEBER: zero indexed, captain 1 = x_0

# set variables, change if needed
number_captains = 40
tours_per_block = 12
blocks_per_day = 6
days = 7


# creates list for ALL time slots, k
slots = range(tours_per_block * blocks_per_day * days)
#for i in range(tours_per_block * blocks_per_day * days):
	#slots.append(i)

# keeps track of which captain has which slots
cap_dict = []
for i in range(number_captains):
	cap_dict.append((i, []))

cap_dict = dict(cap_dict)




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


test1 = mm.convert_to_matrix(cap_dict, number_captains)
print test1.shape
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

