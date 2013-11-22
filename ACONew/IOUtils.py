import sys
from StaticACO import *

def readArray(x):
    " Utility function to read an array "
    
    return map(x, sys.stdin.readline().split())

def readMatrix(rowLength, x):
    " Utility function to read a matrix "
    
    return [readArray(x) for i in range(rowLength)]

def readUser():
    " The utility function to read and return an object of @Type class User "
    
    numberOfAims, learningAbility = raw_input().split()
    #print numberOfAims, learningAbility
    user = User(int(numberOfAims), float(learningAbility))
    return user

def readCourse(user):
    " The utility function to read and return an object of @Type class Course "
    
    numberOfLevels = input()

    # Adding of Vital Course Elements
    course = Course(numberOfLevels)
    course.numberOfPerspectivesAtLevel = readArray(int)
    course.totalNumberOfVertexes = sum(course.numberOfPerspectivesAtLevel)
    course.numberOfLOsAtLevel = readArray(int)
    course.maximumLAAtLevel = MiscUtils.normalize(readArray(float))

    # Adding Tables

    # The Perspective Contribution Table
    for i in range(numberOfLevels):
        course.PACT[i] = readMatrix(user.numberOfAims,float)

    # The LO contribution Table
    for i in range(numberOfLevels):
        course.LALOPT[i] = readMatrix(user.numberOfAims, float)

    # The table for maximum time assigned
    for i in range(numberOfLevels):
        course.levels[i] = Level(i, course.numberOfPerspectivesAtLevel[i])
        for j in range(course.numberOfPerspectivesAtLevel[i]):
            timeAssigned = input()
            #print "Level : ", i, j

            # Making the vertex for a perspective, Important to note that j == perspectiveIndex Always, can be directly used
            course.levels[i].vertexes[j] = Vertex(i, j, timeAssigned, course.numberOfLOsAtLevel[i])
            for k in range(course.numberOfLOsAtLevel[i]):
                course.levels[i].vertexes[j].SubVertexes[k] = SubVertex(k)

    # The table for difficulty of transition
    for i in range(numberOfLevels):
        for j in range(course.numberOfPerspectivesAtLevel[i]):
            maxDifficulty = 0.0
            k = 0
            while i+1 < numberOfLevels and k < course.numberOfPerspectivesAtLevel[i+1]:
                difficulty = input()
                course.levels[i].vertexes[j].edgeList.append(Edge(course.levels[i+1].vertexes[k], float(difficulty)))
                maxDifficulty = max([maxDifficulty, difficulty])
                k += 1
            for edge in course.levels[i].vertexes[j].edgeList:
                edge.difficulty /= maxDifficulty
            for l in range(course.numberOfPerspectivesAtLevel[i]):
                if l != j:
                    course.levels[i].vertexes[j].edgeList.append(Edge(course.levels[i].vertexes[l], 0.0))

    return course

def printPath(path, os):
    " The utility function to print the path object given as a parameter "
    " An additional parameter is passed into the function in order the send the output to some output stream "
    
    if path.vertexes:
        os.write("Path Value = " + str(path.pathValue) + "\n")
        os.write("Time Taken = " + str(path.timeTaken) + "\n")
        for i in range(1, len(path.vertexes)):
            os.write(str(path.vertexes[i].toString()) + "," + str(path.chosenLO[i]))   # ------- > Check for Long.toBinaryString(path.chosenLO.get(i))
            if i != len(path.vertexes) -1:
                os.write(" -> ")
        os.write("\n") 
    else:
        os.write("No Path Found.\n")

def printCourse(course):
    " The utility function to print the course object passed to it as an argument "
    
    print "|Levels| : %d" % course.numberOfLevels
    print "|Vertex| : %d" % course.totalNumberOfVertexes
    print "Perspectives : ", course.numberOfPerspectivesAtLevel
    print "Max LA: ", course.maximumLAAtLevel
    print "LALOPT"
    print '\n'.join(map(str, [level for level in course.LALOPT]))
    print "PACT"
    print '\n'.join(map(str, [level for level in course.PACT]))


