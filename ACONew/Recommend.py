import sys, random, IOUtils, RandomUtils
import ObjectiveFunction, StaticACO

#global lists and maps
timeAssigned = {}
totalLevels = 0
PastPaths = "Students.paths"
PastData = "Students.data"
defaultMatrix = []

class Data:
        """

        The class is for the storing the meta data for the recommendation.
    
        @variables
        course -> @Type class Course an object for the course in contention
        user -> @Type class User an object of the User class, mainly the target student
        maximumTime -> @Type Float stores the time available for the student to complete the course
        
        """

        def __init__(self, course, user):
                self.course = course
                self.user = user
                self.maximumTime = float('inf')
                return
        
class Student:
        """

        The class is for the storing the current progress data for the user.
    
        @variables
        studentId -> @Type integer stores the unique id of the user
        objective -> @Type integer stores the learning aim of the student to take up the course
        learningAbility -> @Type Float stores the initial learning ability of the target user
        scores -> @Type array stores the past scores of the target user, used to calculate the cumulative ability.
        
        """

        def __init__(self, studentId=0, path=[], learningAbility=0.0, objective=-1, scores=[]):
                self.studentId = studentId
                self.path = path
                self.objective = objective
                self.learningAbility = learningAbility
                self.scores = scores
                return

        # Setter functions for the class
        def setId(self, studentIndex):
                self.studentId = studentIndex
                return

        def setPath(self, path):
                self.path = path
                return

        def setObjective(self, objective):
                self.objective = objective
                return

        def setScores(self, scores):
                self.scores = scores
                return
        
        # Getter functions for the class #

        def peerImportance(self, currentAbility, levelIndex):
                " The function tries to find the similarity value between the given user's ability {current ability} and the past student given by self. "
                
                toleranceLimit = 0.1                            ## This gives the threshlod value for tolerance function
                scope = 0.8                                     ## This decides the percent weightage for next and final value similarities
                nextLevelAbility, finalLevelAbility = expectedAbilities(currentAbility, totalLevels - levelIndex)
                T_next  = tolerance(nextLevelAbility, self.ability(levelIndex+1), toleranceLimit) if self.ability(levelIndex+1) > 0.33 else 0.0
                T_final = tolerance(finalLevelAbility, self.ability(totalLevels), toleranceLimit) if self.ability(totalLevels) > 0.33 else 0.0
                return T_next * scope + T_final * (1.0 - scope)

        def expertImportance(self, currentAbility, levelIndex):
                " The function tries to find the expertise value between the given user's ability {current ability} and the past student given by self. "
                
                expertTolerance = 0.70                                                  ## Refers the minimum value after which level of expertise can be considered 
                scope = 0.2                                                             ## This decides the weightage to be given to final and next level expertise values
                userAbility = currentAbility + (1 - currentAbility) * expertTolerance   ## Compute the Minimum Ability user must possess to be an expert for the current learner
                delta = lambda x,y: 1/(1 + 1/(((y-x)*100)**2)) if y > x else 0.0        ## Function: computes value of expertise based on the imporvement in marks
                #if not self.isSimilar(currentAbility, levelIndex):                     ## Checking for similarity of the current user with the past learner

                ## The userAbility variable is considered in both the cases because if the person in consideration is an expert (s)he should not be improving alongwith the modules
                ## However, (s)he must have a more or less stagnant graph of the ability from the start, since (s)he already is an expert of the subject.
                D_next  = delta(userAbility, self.ability(levelIndex+1))
                D_final = delta(userAbility, self.ability(totalLevels))
                return D_next * scope + D_final * (1.0 - scope)
                #return 0.0                                                              ## Value to be returned in case the current student is similar to this student

        def timeTaken(self, levelIndex, course):
                " The function has been used to compute the time spent by the Stuent till level { levelIndex } in the { course } "
                
                timeSpent = 0.0
                for vertex in self.path:
                        levelId, vertexId, chosenLOs = getVals(vertex)
                        if levelId <= levelIndex:
                                for i in range(course.numberOfLOsAtLevel[levelId]):
                                        if ((1<<i) & chosenLOs) != 0:
                                                timeSpent += timeAssigned[vertexId] * course.LALOPT[levelId][self.objective][i]
                        else:
                                break
                return timeSpent

        def pathValue(self, levelIndex, course, logfile):
                " The function has been used to compute the path value of the path taken by the Stuent till level { levelIndex } in the { course } "
                
                road = StaticACO.Path()

                # This is the dummy vertex for a start of the path 
                dv = StaticACO.Vertex(-1,-1,0,0)

                # Make an edge between the dummy vertex and first vertex in the course
                dv.edgeList.append(StaticACO.Edge(course.levels[0].vertexes[0], 0.0))

                # Add that dummuy vertex to the path of the Student
                road.add(dv, 0)

                # This loop tries to formulate a string to an object of class Path
                for element in self.path:
                        l, v, m = getVals(element)
                        #print l,v,m
                        if l <= levelIndex:
                                road.add(course.levels[l].vertexes[v], m)
                        else:
                                break

                pathVal = ObjectiveFunction.pathValue(self.objective, road, defaultMatrix, Data(course, self), logfile, 0)
                #if pathVal:    print pathVal
                return pathVal

        def ability(self, levelIndex):
                " Compute the learning ability of the Student at level { levelIndex } "
                
                learningAbility = self.learningAbility
                k = 0.8
                for i in range(levelIndex):
                        learningAbility = k * learningAbility + (1-k) * self.scores[i]
                return learningAbility

def expectedAbilities(_presentAbility, levelsLeft):
        " The function predicts the value of final score of the student, depending on his current score and the levels he is yet to study "
        levelOfExpertise = [0, 0.4, 0.6, 0.75, 0.85, 0.9, 0.95, 1.0]
        scaleScores = lambda x: 0.0 if x == len(levelOfExpertise)-1 else (((_presentAbility - levelOfExpertise[x]) * (levelOfExpertise[i+2] - levelOfExpertise[i+1])) / (levelOfExpertise[i+1] - levelOfExpertise[i]))
        for i in range(len(levelOfExpertise)-1):
                if levelOfExpertise[i] < _presentAbility <= levelOfExpertise[i+1]:
                        _finalAbility = levelOfExpertise[i+1] + scaleScores(i)
                        #print "\nPresent ability = %f" %_presentAbility
                        #print "\nfinal ability = %f" %_finalAbility
        _nextAbility = _presentAbility + (_finalAbility - _presentAbility)/levelsLeft if levelsLeft else _finalAbility
        #print "\nnext ability = %f" %_nextAbility
        return _nextAbility, _finalAbility

def getVals(vertex):
        " Returns the various values from the vertex packet given by (level id, vertex id, LOs Taken) "
        
        #print vertex
        lId, vId, LO = vertex.split(',')
        lId, vId, LO = lId.strip(), vId.strip(), LO.strip()
        lId, vId, LO = int(lId[1]), int(vId[0]), int(LO)
        return lId, vId, LO

def tolerance(testValue, baseValue, toleranceLimit):
        " Returns the amount of tolerance between the two values given as argument depending on the { tolerance limit } "
        
        amountOftolerance = max((max(min(testValue, baseValue), 0.0) + toleranceLimit - max(testValue, baseValue))/toleranceLimit, 0.0)
        return amountOftolerance

def getSimilarStudents(aim, user, course, path, logfile ):

        # Let the user know about the current progress in the course
        print "Current Parameters --->  aim = %d fitF = %f time = %f  alpha = %f " % (aim, path.pathValue, path.timeTaken, user.learningAbility),
        currentLevel = path.last().levelIndex
        print "currentLevel = ", currentLevel
        
        # Local Variables used inside the function
        similarStudents = []                            ## Set of the similar students
        allStudents = []                                ## Set of All students with same aim
        dataFile = open(PastData, "r")                  ## File conataining the records of the past student 

        for paths in open(PastPaths, "r"):
                
                sid, pathTaken = paths.split(':')       # Get the path and student id bifercated from the line read from the file
                pathTaken = pathTaken.split("->")       # split the path up to find the list of vertices visited in it
                personal = dataFile.readline().split()  # read the corresponding line from the personal file to get the user class details
                sid, obj, ability, marks = int(personal[0]), int(personal[1]), float(personal[2]), map(float, personal[3:])     # Extraction of details
                temp = Student(studentId=sid, path=pathTaken, learningAbility=ability, objective=obj, scores=marks)             # Create a Student object
                
                # The parameters for tolerance relation
                toleranceValue = 0.1

                # Type 1 style, standard and self computed
                #diffpath = (abs(temp.pathValue(currentLevel, course) - path.pathValue) / path.pathValue) >= toleranceValue
                #difftime = (abs(temp.timeTaken(currentLevel, course) - path.timeTaken) / path.timeTaken) >= toleranceValue
                #diffable = (abs(temp.ability(currentLevel) - user.learningAbility)) >= toleranceValue

                # Type 2 style, referred tolerance relation on rough sets for this
                diffpath = tolerance(temp.pathValue(currentLevel, course, logfile), path.pathValue, toleranceValue)
                difftime = tolerance(temp.timeTaken(currentLevel, course), path.timeTaken, toleranceValue)
                diffable = tolerance(temp.ability(currentLevel), user.learningAbility, toleranceValue)

                if obj == aim:
                        allStudents.append(temp)
                        if ((diffpath and difftime) or diffable):
                                similarStudents.append(temp)

        dataFile.close()
        return allStudents, similarStudents

def nextPerspective(student, levelIndex):
        " Helps in finding the next perspective of the past students based on the path that they have followed "
        
        for vertex in student.path:
                levelId, vertexId, _ = getVals(vertex)
                if levelId > levelIndex:
                        return levelId, vertexId
        return None, None

def getRecommendations(aim, course, user, pathFollowed, logfile):
        """
        (Course, User, Path) ---> Vertex.perspectiveIndex

        @params course          : @Type class Course stores the template for the course in contention
        @params user            : @Type class User   stores the data for the user in contention
        @params pathFollowed    : @Type class Path   stores the current Path followed by the user
        @return vertexId        : @Type integer      Vertex.perspectiveIndex tells the perspective which is best till now

        """

        global totalLevels, defaultMatrix
        defaultMatrix = [[0.0 for j in range(course.numberOfPerspectivesAtLevel[i])] for i in range(course.numberOfLevels)]
        ratioWeight = 0.98              ## Currently useless
        fillTime(course)                ## fill in the maximum time assigned to the perspectives in the global variable { time assigned }
        currentLevel = pathFollowed.last().levelIndex   ## Put in the level we are currently at, means the user is on
        totalLevels = course.numberOfLevels             ## Stores the total levels available in the course
        numberOfChoices = course.numberOfPerspectivesAtLevel[currentLevel+1]    ## Stores number of perspectives available at next level

        rType = ["Expert Recommendation", "Peer Recommendation"]                          ## used for printing what kind of recommendation is given to the users.
        print "Total Number of vertexes: ", numberOfChoices
        totalSet, toleranceSet = getSimilarStudents(aim, user, course, pathFollowed, logfile)      ## Find the total and peer group of the current learner
        print "Total Students   :- ", len(totalSet)
        print "Similar Students :- ", len(toleranceSet)
        print "User's  are provided with ", rType[int(user.choiceOfReco)], " !!!"  

        Recommendation = [[0.0, 0.0] for _ in range(numberOfChoices)]           ## make an array for total [] and good [].
        #successfulSet = getSuccessfulStudents(toleranceSet)

        ## This loop helps determining the impact a particular student in the peer group has on the current student, and his choices
        if user.choiceOfReco > 0.10:
                for stud in toleranceSet:
                        levelId, vertexId = nextPerspective(stud, currentLevel)
                        Recommendation[vertexId][1] += stud.peerImportance(user.learningAbility, currentLevel) * user.choiceOfReco
                        Recommendation[vertexId][0] += 1.0

        if user.choiceOfReco < 0.90:
                for stud in totalSet:
                        levelId, vertexId = nextPerspective(stud, currentLevel)
                        expertIValue = stud.expertImportance(user.learningAbility, currentLevel) * (1.0 - user.choiceOfReco)
                        Recommendation[vertexId][1] += expertIValue
                        logfile.write("\nrecommendation value[%d][1] = %f\n" %(vertexId, expertIValue))
                        if expertIValue > 0.10:
                                Recommendation[vertexId][0] += 1.0
        ## Modified to include the number of students in support of the rule instead of just ratio
        successVal = lambda x, y: x/y if y != 0 else x
        successRate = [successVal(float(Recommendation[i][1]), float(Recommendation[i][0])) for i in range(numberOfChoices)]
        #successRate = [(float(Recommendation[i][1]) / float(Recommendation[i][0]))*ratioWeight + (float(Recommendation[i][1])/len(toleranceSet))*(1-ratioWeight) for i in range(numberOfChoices)]
        print "Importance Values : ", [Recommendation[i][1] for i in range(numberOfChoices)]
        print "Total Students    : ", [Recommendation[i][0] for i in range(numberOfChoices)]
        #print "Current Status    : ", successRate

        return successRate
        #maxRate = max(successRate)
        #return successRate.index(maxRate), maxRate

def fillTime(course):
        " Computes and stores the time assigned for the perspectives in the course, has been used to compute the time spent by the past learner in the course "
        
        global timeAssigned
        for level in course.levels:
                for vertex in level.vertexes:
                        timeAssigned[vertex.perspectiveIndex] = vertex.timeAssigned
        return


def addPath(path, ID,  out):
        " It is a helper function to the addStudent () and helps adding the path taken by the current learner to respective database "
        
        out.write("\n" + ID + " : ")
        if path.vertexes:
                for i in range(1, len(path.vertexes)):
                        out.write(str(path.vertexes[i].toString()) + "," + str(path.chosenLO[i]))
                        if i != len(path.vertexes) -1:
                                out.write(" -> ") 
        else:
                out.write("No Path Found.")

def addScore(aim, scores, ID, out):
        " It is a helper function that helps appending the personal details of the current learner to the respective database "
        
        out.write("\n" + ID + " " + str(aim))
        for marks in scores:
                out.write(" " + str(marks))
        
def addStudent(followedPath, scores, aim):
        " The function has been used to append the database with the data of the new student after he completes the course "
        
        ID = str(RandomUtils.getRange(1, 1000)) + str(RandomUtils.getRange(1, 10))

        pathFile = open(PastPaths, "a")
        addPath(followedPath, ID, pathFile)
        pathFile.close()

        dataFile = open(PastData, "a")
        addScore(aim, scores, ID, dataFile)
        dataFile.close()
        return
