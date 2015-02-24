import matrix_maker as mm

# try some test cases
number_captains = 40
#test = np.random.randint(low = 0, high = 1, size = 7 * 72 * number_captains)
sts_mat = mm.build_start_to_schedule_matrix(number_captains)
phi_mat = mm.build_phi_matrix(number_captains)
print phi_mat.shape
print sts_mat.shape