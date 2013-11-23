import sys, math, IOUtils

def pathValue(currentLearningAim, path, RF_table, data, logfile, flowParam):
     """
     (int, Path, ACO) ---> float

     @params currentLearningAim : @Type integer tells the Priority of the student
     @params path : @Type class Path stores the path taken by the User
     @params RF_Table: @Type matrix containing the recommendation values
     @params data : @Type class ACO stores the data for the user alongwith the one related to his progress
     @return flowParam : @Type integer gives the position of the learner, thereby, providing information about how to compute the pathValue, etc.
        
     Function returns the fitness function value for a particular path in a particular ant Colony setup and internally sets the timeSpent variable of the path.
     """

     #Local Variables
     timeSpent = 0.0                 # Total time spent on the course
     difficulty = 0.0                # Cumulative Difficulty Level
     CF, DF, RF = 0.0, 0.0, 0.0      # Coverage, Depth & Reco Factors
     timeSpentOnVertex = [0.0]          # time Spent on each perspective i.e. Vertices
     startVertexIndex = 1            # point to index where student will start in course
        
     # Additional Handling added in order to make sure that the same vertex is not counted twice, in case of Dynamic recommedation
     IOUtils.printPath(path, logfile)
     isMiddleOfCourse = (flowParam is not 0)
     if isMiddleOfCourse:
         logfile.write("The path value is computed from middle of course, the next vertex on her path is ")
         currentLevel = path.vertexes[startVertexIndex].levelIndex
         while path.vertexes[startVertexIndex].levelIndex == currentLevel and startVertexIndex < (len(path.vertexes)-1):  
             startVertexIndex += 1                      # Look whether next vertex is where user starts
             timeSpentOnVertex.append(0.0)              # time spent on this vertex by user is none
     else:
         logfile.write("\nThe path value is computed from start of course, the starting vertex is ")
     
     logfile.write(path.vertexes[startVertexIndex].toString() + " ...")
     ###############
     ## TIME SPENT
     # Review the Path followed thus updating the spent time of the user

     for i in range(startVertexIndex, len(path.vertexes)):
         vertex = path.vertexes[i]
         timeSpentVertex = 0.0
         for j in range(len(vertex.SubVertexes)):
             if (path.chosenLO[i] & 1<<j) != 0:
                  timeSpentVertex += vertex.timeAssigned * data.course.LALOPT[vertex.levelIndex][currentLearningAim][j]
         timeSpent += timeSpentVertex
         timeSpentOnVertex.append(timeSpentVertex)
     
     logfile.write("\nVertex-wise Time distinction: " + ' '.join(map(str, timeSpentOnVertex)))
     path.timeTaken = timeSpent
     logfile.write("\n Time taken = %f" %timeSpent)
     
     # Check for the fact that total time does not overflow the max time for the course !!!
     if timeSpent > data.maximumTime:
         return -1.0*float('inf')
        
     ################################
     ## CUMULATIVE DIFFICULTY LEVEL
     # Review the User's path again to store the values for the difficulty

     i, j = 0, 1
     #print len(path.vertexes)
     while j < len(path.vertexes):
         for edge in path.vertexes[i].edgeList:
             if edge.destination == path.vertexes[j]:
                 difficulty += edge.difficulty
         i, j = i+1, j+1
     logfile.write("\nDifficulty of path = %f" %difficulty)
     
     ####################
     ## COVERAGE FACTOR
     # Review of the path again for the computation of the Coverage Factor

     seenLevels = [False]*data.course.numberOfLevels
     for i in range(startVertexIndex, len(path.vertexes)):
         vertex = path.vertexes[i]
         if not seenLevels[vertex.levelIndex]:
             seenLevels[vertex.levelIndex] = True
             # print "Time Spent = ", timeSpentOnVertex[i]
             # print "Max LA Val = ", data.course.maximumLAAtLevel[vertex.levelIndex]
             # print "RF Value   = ", RF_table[vertex.levelIndex][vertex.perspectiveIndex]
             CF += calculateLA(timeSpentOnVertex[i], data.course.maximumLAAtLevel[vertex.levelIndex], data.user.learningAbility, RF_table[vertex.levelIndex][vertex.perspectiveIndex], logfile)
     logfile.write("\nCoverage factor of path = %f\n" %CF)
     
     #################
     ## DEPTH FACTOR
     # Compute the value of the Depth factor for the student

     numerator = [0.0] * data.course.numberOfLevels
     denominator = [0.0] * data.course.numberOfLevels
     for i in range(startVertexIndex, len(path.vertexes)):
         vertex = path.vertexes[i]
         LA = calculateLA(timeSpentOnVertex[i], data.course.maximumLAAtLevel[vertex.levelIndex], data.user.learningAbility, RF_table[vertex.levelIndex][vertex.perspectiveIndex], logfile)
         numerator[vertex.levelIndex] += LA * data.course.PACT[vertex.levelIndex][currentLearningAim][vertex.perspectiveIndex]
         #denominator[vertex.levelIndex] += data.course.PACT[vertex.levelIndex][currentLearningAim][vertex.perspectiveIndex]
         #denominator[vertex.levelIndex] += LA
     for i in range(data.course.numberOfLevels):
          DF += numerator[i]
          #if denominator[i] != 0.0:
               #DF += numerator[i] / denominator[i]
     logfile.write("\nDepth factor of path = %f\n" %DF)
     
     ###########################
     ## RECOMMENDATION FACTOR
     # Compute the value of the Recommendation Factor for the student

     seenLevels = [False]* data.course.numberOfLevels
     #for i in range(1, len(path.vertexes)):
     #     vertex = path.vertexes[i]
     #     if not seenLevels[vertex.levelIndex]:
     #          seenLevels[vertex.levelIndex] = True
     #          RF += RF_table[vertex.levelIndex][vertex.perspectiveIndex]
     #logfile.write("\nRecommendation value of path = %f\n" %RF)
     
     PV = CF + (7 * DF) - (0.5 * difficulty) 
     logfile.write("\nPathvalue = %f\n" %PV)
     return PV

def calculateLA(time, maximumLA, learningAbility, recVal, logfile):
     """ 
     (int, float, float) ---> float

     @params time : @Type integer  time taken to complete a Level / Topic
     @params maximumLA : @Type float the maximum learning for a level, given by experts
     @params learningAbility : @Type float the learningAbility of the student in question
     @return learningAchievement : @Type float the value of achievement student gains from the particular level

     Computes and returns the value of the LA for a Level based on the given formula 
     """
     
     val = math.exp(-1.0 * learningAbility * time * recVal)
     LA = maximumLA * (1.0 - val )
     logfile.write("\nlearning Ability = %f" %learningAbility)
     logfile.write("\ntime = %f" %time)
     logfile.write("\nrecVal = %f" %recVal)
     logfile.write("\nval = %f" %val)
     logfile.write("\nLA = %f" %LA)
     
     return LA
     #return maximumLA * (1.0 - math.exp((-1.0 * time )/(1 - learningAbility))) if learningAbility < 1.0 else maximumLA


