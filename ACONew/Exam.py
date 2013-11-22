import RandomUtils, MiscUtils

def getScore(numberOfQuestions, marks, Qvalue):
	"""
	(int, float[], float[]) ---> float

	@params numberOfQuestions: @Type integer provide the total questions in exam
	@params marks: @Type float array stores the marks scored by the user
	@params Qvalue: @Type float array stores the relevance value of each question to the user
	@return score: @Type float @range 0-1 provides the score of the user according to user's ability

	Function computes the ability of the user based on his performance in the exam
	"""

	return sum([marks[i]*Qvalue[i] for i in range(numberOfQuestions)]) #/ numberOfQuestions

def getTemplate(numberOfQuestions):
	"""
	(int) ---> float[]

	@params numberOfQuestions: @Type integer provide the number of questions in the exam
	@return examTemplate: @Type float array provide the relevance array for the exam

	Function return the array containing the value of relevance of each question in the exam
	"""

	relevanceArray = [RandomUtils.getDouble() for i in range(numberOfQuestions)] 
	Template = [int(i * 100) / 100.0 for i in MiscUtils.normalize(relevanceArray)]
	return Template

def getMarks(numberOfQuestions):
	"""
	(int) ---> float[]

	@params numberOfQuestions: @Type integer provide the total number of questions in exam
	@return marks: @Type float array shows the array of the marks obtained by the user for each question

	Function returns the marks of the student he obtained for each question in the exam
	"""

	marks = [int(RandomUtils.getDouble() * 100) / 100.0 for i in range(numberOfQuestions)]
	return marks
