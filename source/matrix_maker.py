# script to create the special matrices
import numpy as np
from scipy.sparse import block_diag 

def build_start_to_schedule_matrix(number_captains = 1):
	# 72 possible tours per day
	# 6 2-hour blocks of 12 tours
	# 7 days in a week
	tours_per_block = 12
	blocks_per_day = 6
	days = 7
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

def build_phi_matrix(number_captains = 1):
	# 72 possible tours per day
	# 6 2-hour blocks of 12 tours
	# 7 days in a week
	tours_per_block = 12
	blocks_per_day = 6
	days = 7
	one_temp = np.ones(tours_per_block * blocks_per_day)
	phi_tilde = block_diag([one_temp] * days)
	return (block_diag([phi_tilde] * number_captains)).tocsr()

# try some test cases
number_captains = 40
#test = np.random.randint(low = 0, high = 1, size = 7 * 72 * number_captains)
sts_mat = build_start_to_schedule_matrix(number_captains)
phi_mat = build_phi_matrix(number_captains)
print phi_mat.shape
print sts_mat.shape

