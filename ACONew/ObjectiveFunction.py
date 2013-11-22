import math

def pathValue(currentLearningAim, path, data):
     """
     (int, Path, ACO) ---> float

     @params currentLearningAim : @Type integer tells the Priority of the student
     @params path : @Type class Path stores the path taken by the User
     @params data : @Type class ACO stores the data for the user alongwith the one related to his progress
     @return f : @Type float the value of the fitness function for this particular user taking this path

     Function returns the fitness function value for a particular path in a particular ant Colony setup
     """

     #Local Variables
     timeSpent = 0.0                 # Total time spent on the course
     difficulty = 0.0                # Cumulative Difficulty Level
     CF, DF = 0.0, 0.0               # Coverage & Depth Factors
     timeSpentOnVertex = []          # time Spent on each perspective i.e. Vertices

     # Review the Path followed thus updating the spent time of the user
     for i in range(len(path.vertexes)):
         vertex = path.vertexes[i]
         timeSpentVertex = 0.0
         for j in range(len(vertex.SubVertexes)):
             if (path.chosenLO[i] & 1<<j) != 0:
                 timeSpentVertex += vertex.timeAssigned * data.course.LALOPT[vertex.levelIndex][currentLearningAim][j]
         timeSpent += timeSpentVertex
         timeSpentOnVertex.append(timeSpentVertex)
     path.timeTaken = timeSpent

     # Check for the fact that total time does not overflow the max time for the course !!!
     if timeSpent > data.maximumTime:
         return -1.0*float('inf')

     # Review the User's path again to store the values for the difficulty
     i, j = 0, 1
     #print len(path.vertexes)
     while j < len(path.vertexes):
         for edge in path.vertexes[i].edgeList:
             if edge.destination == path.vertexes[j]:
                 difficulty += edge.difficulty
         i, j = i+1, j+1

     # Review of the path again for the computation of the Coverage Factor
     seenLevels = [False]*data.course.numberOfLevels
     for i in range(1, len(path.vertexes)):
         vertex = path.vertexes[i]
         if not seenLevels[vertex.levelIndex]:
             seenLevels[vertex.levelIndex] = True
             CF += calculateLA(timeSpentOnVertex[i], data.course.maximumLAAtLevel[vertex.levelIndex], data.user.learningAbility)

     # Compute the value of the Depth factor for the student
     numerator = [0.0] * data.course.numberOfLevels
     denominator = [0.0] * data.course.numberOfLevels
     for i in range(1, len(path.vertexes)):
         vertex = path.vertexes[i]
         LA = calculateLA(timeSpentOnVertex[i], data.course.maximumLAAtLevel[vertex.levelIndex], data.user.learningAbility)
         numerator[vertex.levelIndex] += LA * data.course.PACT[vertex.levelIndex][currentLearningAim][vertex.perspectiveIndex]
         denominator[vertex.levelIndex] += LA
     for i in range(data.course.numberOfLevels):
         if denominator[i] != 0.0:
             DF += numerator[i] / denominator[i]

     return CF + DF - 0.5 * difficulty

def calculateLA(time, maximumLA, learningAbility):
     """ 
     (int, float, float) ---> float

     @params time : @Type integer  time taken to complete a Level / Topic
     @params maximumLA : @Type float the maximum learning for a level, given by experts
     @params learningAbility : @Type float the learningAbility of the student in question
     @return learningAchievement : @Type float the value of achievement student gains from the particular level

     Computes and returns the value of the LA for a Level based on the given formula 
     """

     return maximumLA * (1.0 - math.exp(-1.0 * learningAbility * time))
     #return maximumLA * (1.0 - math.exp((-1.0 * time )/(1 - learningAbility))) if learningAbility < 1.0 else maximumLA


