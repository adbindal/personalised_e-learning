import sys, random

## This fie does no work in main code, it is mainly used for generating the
## arbitary students in the database 

# Files for paths and personal information
studs = lambda: open("Students.paths", "r")
noOfLevels = 0

def normalize(array):
	sumOfElements = sum(array)
	return [Element / sumOfElements for Element in array]

def genScore():
	numberOfQuestions = random.randint(10, 20)
	marks = [random.random() * 10 / 10.0 for i in range(numberOfQuestions)]
	template = normalize([random.random() for i in range(numberOfQuestions)])
	score = sum([marks[i] * template[i] for i in range(numberOfQuestions)])
	return score

def lvlId(vertex):
	lvl, _, _ = vertex.split(',')
	lvl = lvl.strip()
	print lvl
	return int(lvl[1])

def getLevels(path):
	global noOfLevels
	if not noOfLevels:
		noOfLevels = len(set([lvlId(i) for i in path.split("->")]))
	return noOfLevels 

def getStudId():
	for stud in studs():
		idx, path = stud.split(": ")
		yield idx, path
	return

def createInfo(file):
	for idx, p in getStudId():
		lvl = getLevels(p)
		scores = [random.randint(0,2), random.random()]
		for _ in range(lvl):
			scores.append(genScore())
		file.write(str(idx) + ' '.join(map(str,scores)) + "\n")
	return

def main():
	infos = open("Students.data", "w+")
	createInfo(infos)
	infos.close()
	return

if __name__=="__main__":
	main()
