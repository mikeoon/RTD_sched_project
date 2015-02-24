import matrix_maker as mm
import numpy as np

number_captains = 40
np.random.seed(33)

l = []
for i in range(number_captains):
	temp = np.zeros(72) # number per captain
	temp[np.random.randint(72)] = 1
	l.append(np.hstack([temp] * 7))
x = np.hstack(l)


#test = np.random.randint(low = 0, high = 1, size = 7 * 72 * number_captains)
sts_mat = mm.build_start_to_schedule_matrix(number_captains)
phi_mat = mm.build_phi_matrix(number_captains)
#print (phi_mat * x).shape
#print x[:72]

def objective_helper(phi_mat_x, number_captains = 1):
	result = 0
	for i in range(number_captains):
		temp = phi_mat_x[(i * 7):((i + 1) * 7)]
		t1 = temp[0]*temp[1]*temp[2]*temp[3]
		t2 = temp[1]*temp[2]*temp[3]*temp[4]
		t3 = temp[2]*temp[3]*temp[4]*temp[5]
		t4 = temp[3]*temp[4]*temp[5]*temp[6]
		t5 = temp[4]*temp[5]*temp[6]*temp[0]
		# wrap around more?
		result += t1 + t2 + t3 + t4 + t5
	return result

objective = lambda x : objective_helper(phi_mat * x, number_captains = number_captains)

#print objective_helper(phi_mat * x, number_captains = number_captains)
#print objective(x)
temp = mm.build_inequality_matrix(40)
print temp.shape
