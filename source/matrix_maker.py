# script to create the special matrices
import numpy as np
from scipy.sparse import block_diag, hstack, vstack, csr_matrix

def build_start_to_schedule_matrix(number_captains = 1, tours_per_block = 12, blocks_per_day = 6, days = 7):
	# create basic matrices and then build via blocks
	I_temp = np.identity(tours_per_block)
	zero_temp = np.zeros((tours_per_block, tours_per_block))
	# build the parts to the lower triangular matrix. There are 6 blocks in one
	# day, so there are 6 rows of the lower triangular matrix
	L_1 = np.hstack((I_temp, np.hstack([zero_temp] * 5)))
	L_2 = np.hstack((np.hstack([I_temp] * 2), np.hstack([zero_temp] * 4)))
	L_3 = np.hstack((np.hstack([I_temp] * 3), np.hstack([zero_temp] * 3)))
	L_4 = np.hstack((np.hstack([I_temp] * 4), np.hstack([zero_temp] * 2)))
	L_5 = np.hstack((np.hstack([I_temp] * 5), zero_temp))
	L_6 = np.hstack((zero_temp, np.hstack([I_temp] * 5)))
	# put them together to get the L matrix
	L = np.vstack((L_1, L_2, L_3, L_4, L_5, L_6))
	# make L' block diagonal matrix from L 7 times (# days in the week)
	L_prime = block_diag([L] * days)
	# now, block diagonal stack L_prime for the number of captains 
	return (block_diag([L_prime] * number_captains)).tocsr()

def build_phi_matrix(number_captains = 1, tours_per_block = 12, blocks_per_day = 6, days = 7):
	one_temp = np.ones(tours_per_block * blocks_per_day)
	phi_tilde = block_diag([one_temp] * days)
	return (block_diag([phi_tilde] * number_captains)).tocsr()

def build_psi_matrix(number_captains = 1, tours_per_block = 12, blocks_per_day = 6, days = 7):
	one_temp = np.ones(tours_per_block * blocks_per_day)
	psi_tilde = block_diag([one_temp] * days)
	return block_diag([psi_tilde] * number_captains).tocsr()

def build_M_matrix(number_captains = 1, tours_per_block = 12, blocks_per_day = 6, days = 7):
	one_temp = np.ones(tours_per_block * blocks_per_day)
	M_tilde = block_diag([one_temp] * days)
	return hstack([M_tilde] * number_captains).tocsr()

def build_inequality_matrix(number_captains = 1, tours_per_block = 12, blocks_per_day = 6, days = 7):
	# first, build Psi
	Psi = build_psi_matrix(number_captains, tours_per_block, blocks_per_day, days)
	# next, build S
	one_temp = np.ones(tours_per_block * blocks_per_day * days)
	S = block_diag([one_temp] * number_captains).tocsr()
	# build M Matrix to keep # of captains per day low, SHOULD BE EQUALITY
	#M = build_M_matrix(number_captains, tours_per_block, blocks_per_day, days)
	return vstack((Psi, S)).tocsr()

def build_equality_matrix(number_captains = 1, tours_per_block = 12, blocks_per_day = 6, days = 7):
	# finally, build E
	E = csr_matrix(np.hstack([np.identity(tours_per_block * blocks_per_day * days)] * number_captains))
	STS = build_start_to_schedule_matrix(number_captains, tours_per_block, blocks_per_day, days)
	return (E * STS).tocsr()

# builds 
def build_inequality_constraint_vect(number_captains = 1, tours_per_block = 12, blocks_per_day = 6, days = 7):
	phi_const_vect = np.matrix(np.ones(days * number_captains))
	phi_const_vect = phi_const_vect.T
	# the 4 coefficient is hard coded, should be an input 
	S_const_vect = np.matrix(np.ones(number_captains) * 4)
	S_const_vect = S_const_vect.T
	#M_const_vect = np.matrix(np.ones(days) * 20) # shouls be equality
	#M_const_vect = M_const_vect.T
	return np.vstack((phi_const_vect, S_const_vect))


def build_equality_constraint_vect(number_captains = 1, tours_per_block = 12, blocks_per_day = 6, days = 7):
	temp_vect = np.matrix([0,0,3]).T
	# hard coded for 3rd time slot, should be an input
	temp_zero_vect = np.matrix(np.zeros(9)).T
	temp = np.vstack([temp_vect] * 21)
	temp = np.vstack([temp, temp_zero_vect])
	return np.vstack([temp] * days)


def build_dictionary(number_captains = 1, tours_per_block = 12, blocks_per_day = 6, days = 7):
	d = []
	for i in range(number_captains * tours_per_block * blocks_per_day * days):
		d.append((i, [0,1]))
	return dict(d)

# Creates a matrix of what schedule the bnb creates. can also be used to see current schedule, just have to update
# the parameters to how far you have gone in the bnb
def convert_to_matrix(cap_dict, number_captains = 1, tours_per_block = 12, blocks_per_day = 6, days = 7):
	# create first matrix to stack on
	sched_matrix = np.zeros(tours_per_block * blocks_per_day * days)
	sched_matrix[cap_dict[0]] = 1
	sched_matrix = np.matrix(sched_matrix)

	for i in range(number_captains - 1):
		temp_row = np.zeros(tours_per_block * blocks_per_day * days)
		temp_row[cap_dict[i+1]] = 1
		temp_row = np.matrix(temp_row)
		sched_matrix = np.vstack((sched_matrix, temp_row))

	return sched_matrix

def convert_to_vector(cap_dict, number_captains = 1, tours_per_block = 12, blocks_per_day = 6, days = 7, captain = None):
	# if we wish to look at a specific captain's start schedule, override
	if captain is not None:
		capt_start_times = cap_dict[captain]
		temp_vec = np.zeros(tours_per_block * blocks_per_day * days)
		for time in capt_start_times:
			temp_vec[time] = 1
		return temp_vec

	# else, provide the schedule for the whole crew
	sched_vec = []
	for i in range(number_captains):
		capt_start_times = cap_dict[i]
		temp_vec = np.zeros(tours_per_block * blocks_per_day * days)
		for time in capt_start_times:
			temp_vec[time] = 1
		sched_vec.append(temp_vec)
	return np.matrix(np.hstack(sched_vec)).T







