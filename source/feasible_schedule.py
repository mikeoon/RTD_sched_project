number_captains = 40
tours_per_block = 12
blocks_per_day = 6
days = 7
max_days_worked = 4

# initialize a dictionary of start times
capt_dict = dict()
for captain in range(number_captains):
	# empty schedule for each day
	capt_dict[captain] = [] # could be a list of 7 lists, 1 per day

capt_dict[1] = [373, 72, 90, 1]

########################## INDIVIDUAL CONSTRAINTS ##############################
## INEQUALITY CONSTRAINTS --
## 1) Days worked per captian constraint. (No more than 4 perweek)
## 2) Start times per day constrain. (No more than once per day)
## 3) Unable to work constraint. (Can't work specific days)
## 4) Has to work specific shift constraint. (Some shifts are rquested)
## EQUALITY CONSTRAINTS --
## 5) Tours per timeslot constraint. (Specified by the user, usually 1-3)
## 6) Captains per day constraint. (Specified by the user, usually 20)

def days_worked_per_captain_constraint(capt_dict, captain, max_days_worked):
	# return true if constraint is satisfied
	return len(capt_dict[captain]) <= max_days_worked

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

def unable_to_work_constraint(capt_dict, captain, shifts_unable_to_work):
	return 1

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
