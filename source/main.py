import matrix_maker as mm
import numpy as np
from openopt import MINLP

number_captains = 10
np.random.seed(33)

l = []
for i in range(number_captains):
	temp = np.zeros(72) # number per captain
	temp[np.random.randint(72)] = 1
	l.append(np.hstack([temp] * 7))
x = np.matrix(np.hstack(l)).T


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


ineq_matrix = mm.build_inequality_matrix(number_captains)
ineq_constraint_matrix = mm.build_inequality_constraint_vect(number_captains)
equal_matrix = mm.build_equality_matrix(number_captains)
equal_constraint_matrix = mm.build_equality_constraint_vect(number_captains)

#print type(equal_matrix)
#print (equal_matrix * x).shape
#print equal_constraint_matrix.shape
#print type(x)
#print type(equal_constraint_matrix)
#print type(ineq_matrix)


objective = lambda x : objective_helper(phi_mat * x, number_captains = number_captains)
ineq_constraint = lambda x : ineq_matrix * x - ineq_constraint_matrix
equal_constraint = lambda x : equal_matrix * x - equal_constraint_matrix

#t1 = equal_matrix * np.matrix(np.zeros(len(x))).T - equal_constraint_matrix

#equal_constraint(np.matrix(np.zeros(len(x))).T)


#p = MINLP(f = objective, x0 = np.matrix(np.zeros(len(x))).T, c = ineq_constraint, h = equal_constraint)
p = MINLP(f = objective, x0 = x, c = ineq_constraint, h = equal_constraint)

p.discreteVars = mm.build_dictionary(number_captains)
nlpSolver = 'ipopt'

#p.lb = [0]*len(x)
#p.ub = [1]*len(x)

r = p.solve('branb', nlpSolver=nlpSolver, plot = False)



print r.xf
print r.ff