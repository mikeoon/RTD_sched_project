import matrix_maker as mm
import numpy as np
from scipy.sparse import vstack
from openopt import MINLP
from openopt import NLP

number_captains = 40
tours_per_block = 12
blocks_per_day = 6
days = 7
np.random.seed(33)

l = []
for i in range(number_captains):
	temp = np.zeros(tours_per_block * blocks_per_day) # number per captain
	temp[np.random.randint(tours_per_block * blocks_per_day)] = 1
	l.append(np.hstack([temp] * days))
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


new_ineq_mat = vstack((ineq_matrix, -1 * equal_matrix)).tocsr()
new_ineq_vec = vstack((ineq_constraint_matrix, -1 * equal_constraint_matrix)).tocsr()


objective = lambda x : objective_helper(phi_mat * x, number_captains = number_captains)
ineq_constraint = lambda x : ineq_matrix * x - ineq_constraint_matrix
equal_constraint = lambda x : equal_matrix * (sts_mat * x) - equal_constraint_matrix
new_ineq_constraint = lambda x : new_ineq_mat * x - new_ineq_vec

#print (new_ineq_mat * x)[-72:]
#print new_ineq_vec.shape

#t1 = equal_matrix * np.matrix(np.zeros(len(x))).T - equal_constraint_matrix

#equal_constraint(np.matrix(np.zeros(len(x))).T)


# test the equality constraint...something fishy is going on


#p = MINLP(f = objective, x0 = np.matrix(np.zeros(len(x))).T, c = ineq_constraint, h = equal_constraint)
p = MINLP(f = objective, x0 = x, c = ineq_constraint, h = equal_constraint)
#p = MINLP(f = objective, x0 = x, c = new_ineq_constraint)
#p = MINLP(f = objective, x0 = x,  A = ineq_matrix, b = ineq_constraint_matrix)

p.discreteVars = mm.build_dictionary(number_captains)
nlpSolver = 'ipopt'
p.lb = [0]*len(x)
p.ub = [1]*len(x)

#r = p.solve('branb', nlpSolver = nlpSolver, plot = False)
