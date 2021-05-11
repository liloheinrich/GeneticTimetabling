import csv
import itertools
import random
import copy
from operator import itemgetter

# using 24-hour convention
DAY_START = 8
DAY_END = 17
LUNCH_START = 11.5
LUNCH_END = 12
NIGHT_END = 21

time_list = []
for i in range(DAY_START,DAY_END): # time window for classes
	for j in range(0,4): # 15-minute increments
		time_list.append(i+0.25*j) # timecode as (hour).(minutes as fraction of hour)

evening_time_list = []
for i in range(DAY_END,NIGHT_END): # time window for classes
	for j in range(0,4): # 15-minute increments
		evening_time_list.append(i+0.25*j) # timecode as (hour).(minutes as fraction of hour)

day_list = [i for i in range(0,5)] # weekdays mon-fri as 0-4
day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


class Course:
	def __init__(self, course_info):
		self.name = course_info[0]
		self.profs = course_info[1].split(sep = ' & ')
		self.num_classes = int(course_info[2])
		self.length = float(course_info[3])

		temp_days_possible = list(itertools.combinations(day_list, self.num_classes))
		self.days_possible = []
		for i in range(len(temp_days_possible)):
			if "SCOPE" in self.name: # SCOPE should be only wednesdays and or fridays
				if 2 in temp_days_possible[i] or 4 in temp_days_possible[i]:
					self.days_possible.append(temp_days_possible[i])
			else: # classes/lectures should never be back-to-back days, it's much less effective
				for d in temp_days_possible[i]: 
					if d+1 not in temp_days_possible[i] and d-1 not in temp_days_possible[i]:
						self.days_possible.append(temp_days_possible[i])

		self.times_possible = []
		if "Conductorless" in self.name: # OCO in evening is a special exception
			for t in evening_time_list:
				end_timecode = t + self.length
				if end_timecode <= NIGHT_END:
					self.times_possible.append(t)
		else:
			for t in time_list:
				end_timecode = t + self.length
				if end_timecode <= DAY_END:
					if "SCOPE" in self.name and t <= 9.0: # SCOPE is a special exception
						print("SCOPING!")
						self.times_possible.append(t)
					elif end_timecode <= LUNCH_START or t >= LUNCH_END:
						self.times_possible.append(t)

		self.loc = course_info[4]
		self.possibilities = [self.days_possible, self.times_possible] # days, times is the key
		self.max = [len(self.days_possible), len(self.times_possible)]

		# print("profs", self.profs)
		# print("days_possible:", self.days_possible)
		# print("times_possible:", self.times_possible)

	def __str__(self):
		return str(self.name)
			# +", taught by "+str(self.profs)
			# +" with "+str(self.num_classes)+" "+str(self.length)+"-hour classes per week"

def timecode_tostring(timecode):
	hour_str = str(int(timecode))
	minute_str = str(int((timecode % 1)*60))
	if minute_str == "0":
		minute_str += "0"
	return hour_str + ":" + minute_str

def get_courses(filename):
	courses = []
	with open(filename) as csv_file:
	    csv_reader = csv.reader(csv_file, delimiter=',')
	    for row in csv_reader:
	    	course_info = row[0:5]
	    	course = Course(course_info)
	    	courses.append(course)
	return courses

course_filename = "course_info.csv"
courses = get_courses(course_filename)
dna1 = []
dna2 = []
for c in courses:
	print(c)
	dna1.append([0,0])
	dna2.append([c.max[0]-1,c.max[1]-1])
print()

print("INITIAL POPULATION") # the "adam and eve" sort of
print("dna1:", dna1)
print("dna2:", dna2)
print()

def get_conflicts(filename):
	conflicts = dict()
	with open(filename) as csv_file:
	    csv_reader = csv.reader(csv_file, delimiter=',')
	    line_count = 0
	    for row in csv_reader:
	    	conflicts[row[0], row[1]] = int(row[2])
	return conflicts

conflict_filename = "conflicts.csv"
conflicts = get_conflicts(conflict_filename)
print("CONFLICTS")
print(conflicts)
print()

def prof_overlap(pair, courses, dna):
	eval = 0
	c1 = courses[pair[0]]
	c2 = courses[pair[1]]
	d1 = dna[pair[0]]
	d2 = dna[pair[1]]
	days1 = c1.possibilities[0][d1[0]]
	days2 = c2.possibilities[0][d2[0]]
	for td1 in days1:
		for td2 in days2:
			if td1 == td2:
				start_time1 = c1.possibilities[1][d1[1]]
				# print("c2.name", c2.name, "c2.possibilities", c2.possibilities)
				start_time2 = c2.possibilities[1][d2[1]]
				end_time1 = start_time1 + c1.length
				end_time2 = start_time2 + c2.length
				if start_time1 < end_time2 and start_time2 < end_time1:
					if any(prof in c1.profs for prof in c2.profs):
						# print("c1.profs", c1.profs)
						# print("c2.profs", c2.profs)
						eval -= 1
	return eval

def loc_overlap(pair, courses, dna):
	eval = 0
	c1 = courses[pair[0]]
	c2 = courses[pair[1]]
	d1 = dna[pair[0]]
	d2 = dna[pair[1]]
	days1 = c1.possibilities[0][d1[0]]
	days2 = c2.possibilities[0][d2[0]]
	for td1 in days1:
		for td2 in days2:
			if td1 == td2:
				start_time1 = c1.possibilities[1][d1[1]]
				start_time2 = c2.possibilities[1][d2[1]]
				end_time1 = start_time1 + c1.length
				end_time2 = start_time2 + c2.length
				if start_time1 < end_time2 and start_time2 < end_time1:
					if c1.loc == c2.loc:
						eval -= 1
	return eval

def get_conflicts(pair, courses, dna):
	eval = 0
	c1 = courses[pair[0]]
	c2 = courses[pair[1]]
	d1 = dna[pair[0]]
	d2 = dna[pair[1]]
	days1 = c1.possibilities[0][d1[0]]
	days2 = c2.possibilities[0][d2[0]]
	for td1 in days1:
		for td2 in days2:
			if td1 == td2:
				start_time1 = c1.possibilities[1][d1[1]]
				start_time2 = c2.possibilities[1][d2[1]]
				end_time1 = start_time1 + c1.length
				end_time2 = start_time2 + c2.length
				# if start_time1 < end_time2 and start_time2 < end_time1:
				if start_time1 <= end_time2 and start_time2 <= end_time1:
					if conflicts.get((c1.name, c2.name)) == None:
						if conflicts.get((c2.name, c1.name)) != None:
							eval -= conflicts[c2.name, c1.name]
					else:
						eval -= conflicts[c1.name, c2.name]
	return eval

def fitness(courses, dna):
	# # TODO think about this more
	eval = 0
	DOUBLEBOOK_PENALTY = 1000
	idx_list = [i for i in range(len(dna))]
	idx_pairs = list(itertools.combinations(idx_list, 2))
	# print("idx_pairs", idx_pairs)

	for p in idx_pairs:
		prof_eval = prof_overlap(p, courses, dna)
		if prof_eval < 0: # there's a professor who is double-booked
			eval += prof_eval* DOUBLEBOOK_PENALTY

		loc_eval = loc_overlap(p, courses, dna)
		if loc_eval < 0: # there's a location that is double-booked
			eval += loc_eval* DOUBLEBOOK_PENALTY

		eval += get_conflicts(p, courses, dna) # number of students who it conflicts for
	return eval

print("INITIAL FITNESS")
init_pop = [dna1, dna2]
fitnesses = []
for p in init_pop:
	# print("dna", p)
	eval = fitness(courses, p)
	# print("eval", eval)
	fitnesses.append(eval)
# selected = init_pop
# selected_fitnesses = fitnesses
population = list(zip(fitnesses, init_pop))
print("fitnesses:", fitnesses)
print()

NONIMPROVEMENTS = 0
MAX_NONIMPROVEMENTS = 10
FITNESS = float("-inf")
SCHEDULE = None
NEW_FITNESS = max(fitnesses)
NEW_SCHEDULE = init_pop[fitnesses.index(NEW_FITNESS)]
print("NEW_FITNESS", NEW_FITNESS)
# print("NEW_SCHEDULE", NEW_SCHEDULE)
print()

def crossover(dna1, dna2, num_children):
	children = []
	for i in range(num_children):
		rand = random.randint(0,len(dna1)-1)
		child = copy.deepcopy(dna1)
		for j in range(rand, len(dna1)):
			child[j] = dna2[j]
		children.append(child)
	return children

def mutate(courses, dna, probability):
	# print("dna", dna)
	for i in range(len(dna)):
		for j in range(len(dna[i])):
			if random.random() < probability:
				rand = random.randint(0,courses[i].max[j]-1)
				dna[i][j] = rand
				# print("dna", dna, "rand", rand)
	# print("dna", dna)

def make_roulette_wheel(fitnesses):
	percents = []
	for i in range(len(fitnesses)):
		percent = 1.0
		if fitnesses[i] != 0:
			# percent = (-1/fitnesses[i]) # inverse
			percent = (-1/fitnesses[i]/fitnesses[i]/fitnesses[i]) # cubed inverse
		percents.append(percent)
	sum_percents = sum(percents)
	for i in range(len(percents)):
		percents[i] *= 1/sum_percents
	return percents

def selection(courses, zipped_dna, size): # roulette wheel method #children, fitnesses
	# make sure to at least keep (one of) the best candidate(s)
	# zipped_dna = list(zip(fitnesses, children))
	# print("(zipped_dna)"., (zipped_dna))
	# max_val = max(list(zipped_dna))
	max_val = max(zipped_dna, key=itemgetter(0))
	print("max_val", max_val[0])
	max_idx = zipped_dna.index(max_val)
	# max_idx = fitnesses.index(max(fitnesses))
	# print("max val", zipped_dna[max_idx]) #, "dna =", pool[max_idx])
	# print("max val =", fitnesses[max_idx]) #, "dna =", pool[max_idx])

	selected = [zipped_dna[max_idx][1]]
	# print("selected", selected)
	print("fitness(zipped_dna[max_idx][1])", fitness(courses, zipped_dna[max_idx][1]))
	print("zipped_dna[max_idx][0]         ", zipped_dna[max_idx][0])
	selected_fitnesses = [zipped_dna[max_idx][0]]
	zipped_dna.pop(max_idx)
	# fitnesses.pop(max_idx)

	# save some others based on roulette wheel probability of inverse
	for i in range(size-1):
		unzip_fit = [element for element,_ in zipped_dna]
		# print("unzip_fit", unzip_fit)
		percents = make_roulette_wheel(unzip_fit)
		if len(percents) == 0:
			break
		rand = random.random()
		percent = 0
		idx = 0
		while idx < len(percents) and rand > (percent + percents[idx]):
			percent += percents[idx]
			idx += 1
		# print("idx", idx, "percents", percents)
		# print("zipped_dna[idx][1]", zipped_dna[idx][1])
		selected.append(zipped_dna[idx][1])
		print("fitness(zipped_dna[idx][1])", fitness(courses, zipped_dna[idx][1]))
		print("zipped_dna[idx][0]         ", zipped_dna[idx][0])
		selected_fitnesses.append(fitnesses[idx])
		zipped_dna.pop(idx)
	zipped_selected = zip(selected_fitnesses, selected)
	return zipped_selected #, selected_fitnesses

############################################################################################

# population = init_pop
# while (NONIMPROVEMENTS < MAX_NONIMPROVEMENTS):
while FITNESS <= -1000:
	print("SELECT")
	size = 8 # even numbers work well for pairing
	zipped_selected = selection(courses, population, size) #children, mutated_fitnesses
	print() 

	print("CROSSOVER")
	num_children = 20
	# zipped_dna = zip(selected_fitnesses, selected)
	sorted_zipped_dna = sorted(zipped_selected, reverse=True)
	sorted_dna = [element for _,element in sorted_zipped_dna]
	sorted_fit = [element for element,_ in sorted_zipped_dna]
	print("sorted_fit =", sorted_fit)

	children = []
	for i in range(int(len(sorted_dna) / 2)):
		children.extend(crossover(sorted_dna[2*i], sorted_dna[2*i+1], num_children))

	crossover_fitnesses = []
	for c in children:
		# print("dna", c)
		crossover_fitnesses.append(fitness(courses, c))
	print("crossover_fitnesses:", crossover_fitnesses)
	avg_fitness = sum(crossover_fitnesses)/len(crossover_fitnesses)
	print("avg_fitness", avg_fitness)
	print()
	# zipped_dna = zip(crossover_fitnesses, children)


	print("MUTATE")
	probability = 0.05
	mutated_fitnesses = []
	for c in children:
		mutate(courses, c, probability)
		mutated_fitnesses.append(fitness(courses, c))
	print("fitnesses:", mutated_fitnesses)
	avg_fitness = sum(mutated_fitnesses)/len(mutated_fitnesses)
	print("avg_fitness", avg_fitness)
	print()
	zipped_mutated = list(zip(mutated_fitnesses, children))
	unzip_dna = [element for _,element in zipped_mutated]
	unzip_fit = [element for element,_ in zipped_mutated]


	print("FITNESS")
	fitnesses = []
	for s in unzip_dna:
		# eval = fitness(courses, s)
		fitnesses.append(fitness(courses, s))
	print("fitnesses:", fitnesses)
	avg_fitness = sum(fitnesses)/len(fitnesses)
	print("avg_fitness", avg_fitness)
	print()

	population = zipped_mutated


	NEW_FITNESS = max(fitnesses)
	NEW_SCHEDULE = children[fitnesses.index(NEW_FITNESS)]
	# print("NEW_FITNESS", NEW_FITNESS)
	# print("FITNESS", FITNESS)
	# print("NEW_SCHEDULE", NEW_SCHEDULE)
	if NEW_FITNESS == 0:
		print("SUCCESS!!!")
		print()
		fitness(courses, NEW_SCHEDULE)
		break
	elif NEW_FITNESS > FITNESS:
		FITNESS = NEW_FITNESS
		SCHEDULE = NEW_SCHEDULE
		# print("Made an improvement!")
		NONIMPROVEMENTS = 0
	elif NEW_FITNESS <= FITNESS:
		NONIMPROVEMENTS += 1

	print("NEW_FITNESS", NEW_FITNESS)
	print("FITNESS", FITNESS)
	print("NONIMPROVEMENTS", NONIMPROVEMENTS)
	print("--------------------------------------------------------------------------------------------------------------------------------")


def print_schedule(courses, SCHEDULE):
	for i in range(len(SCHEDULE)):
		print(courses[i])
		# print(SCHEDULE[i])

		readable_profs = ""
		for p in courses[i].profs:
			readable_profs += ", " + p
		print("\tProfessor(s):", readable_profs[2:])
		days = courses[i].possibilities[0][SCHEDULE[i][0]]
		readable_days = ""
		for d in days:
			readable_days += ", " + day_names[d]
		print("\tDays:", readable_days[2:])
		start_timecode = courses[i].possibilities[1][SCHEDULE[i][1]]
		end_timecode = start_timecode + courses[i].length
		print("\tTime:", timecode_tostring(start_timecode), "-", timecode_tostring(end_timecode))
		print("\tLocation: ", courses[i].loc)


print_schedule(courses, NEW_SCHEDULE)