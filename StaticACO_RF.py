import sys, time, random, math
import IOUtils, MiscUtils, RandomUtils, Exam
import  Recommend, ObjectiveFunction


## global Table needed
recoMatrix = []

# -> in place of Course.java
class Course:

    """
    The class is for the storing of the parts of the course.
    
    @variables
    numberOfLevels -> @Type integer the total topics in a course
    LALOPT -> @Type 3D array the LO Contributions for currentLearningAim topicwise
    PACT -> @Type 3D array of integers perspective Contributions for currentLearningAim topicwise
    levels -> @Type array of class Level stores the Topic data as node
    numberOfPerspectivesAtLevel -> @Type array of integers store the number of perspectives in a topic
    numberOfLOsAtLevel -> @Type array of integers store the number of LOs in a topic
    maximumLAAtLevel -> @Type array of integers Maximum learningAchievement for a student stored topicwise
    """

    def __init__(self, numberOfLevels):
        self.numberOfLevels = numberOfLevels
        self.LALOPT = [[]]*numberOfLevels
        self.PACT = [[]]*numberOfLevels
        self.levels = [0]*numberOfLevels
        self.numberOfPerspectivesAtLevel = []
        self.numberOfLOsAtLevel = []
        self.maximumLAAtLevel = []
        return

    def dequeue(self):
        self.numberOfLevels -= 1
        self.LALOPT.pop(0)
        self.PACT.pop(0)
        self.levels.pop(0)
        self.numberOfPerspectivesAtLevel.pop(0)
        self.numberOfLOsAtLevel.pop(0)
        self.maximumLAAtLevel.pop(0)
        return

    def getLevel(levelId):
        for level in self.levels:
            if level.levelIndex == levelId:
                return level
        return None

# -> in place of User.java
class User:

    """
    The class is for storing data of a user.
    
    @variables 
    numberOfAims -> @Type integer store the Aim number for a student
    learningAbility -> @Type float store the learningAbility for a student
    """

    def __init__(self, numberOfAims, learningAbility):
        self.numberOfAims = numberOfAims
        self.learningAbility = learningAbility
        self.choiceOfReco = 1.0
        return

# -> in place of SubVertex.java
class SubVertex:

    """
    The class stores the data for LOs inside a particular LOIndex
    
    @variables
    LOIndex -> @Type integer store the index for an LO in a perspectives
    """

    def __init__(self, LOIndex):
        self.LOIndex = LOIndex
        return

# -> in place of Vertex.java
class Vertex:

    """
    The class stores the data for perspectives in a particular Level
    
    @variables
    levelIndex -> @Type integer store the index for the topic under which the perspective is
    perspectiveIndex -> @Type integer store the index for perspective to uniquely identify it
    timeAssigned -> @Type float store the time assigned to complete the LOs inside this perspective
    subVertexes -> @Type array of class SubVertex store the LOs under the perspective
    edgeList -> @Type array of class Edge store the outgoing edges from the perspective  
    """

    def __init__(self, levelIndex, perspectiveIndex, timeAssigned, numberOfLOs):
        self.levelIndex = levelIndex
        self.perspectiveIndex = perspectiveIndex
        self.timeAssigned = timeAssigned
        self.SubVertexes = [SubVertex(i) for i in range(numberOfLOs)]
        self.edgeList = []
        return

    def toString(self):
        " Function returns the id for the perspective alongwith the parent Level "
        return "(" + str(self.levelIndex) + ", " + str(self.perspectiveIndex) + ")"

    def vid(self):
        return self.perspectiveIndex

# -> in place of Edge.java
class Edge:

    """
    The class stores the data for an edge connecting the various perspectives
    
    @variables
    destination -> @Type class Vertex store the perspective where edge goes
    difficulty -> @Type float store the difficulty value of the edge
    pheromone -> @Type float store the current pheromone level on this edge
    """

    def __init__(self, destination, difficulty):
        self.destination = destination
        self.difficulty = difficulty
        self.pheromone = 0.0
        return

    def toString(self):
        " Function returns the id of the edge showing the destination and difficulty "
        return self.destination.toString() + ", " + str(self.difficulty)

# -> in place of Level.java
class Level:

    """
    The class stores the data for Level that includes various vertexes
    
    @variables
    levelIndex -> @Type integer store the index for uniquely defining a Level
    vertexes -> @Type array of class Vertex store the perspectives which are inside this course topic
    """

    def __init__(self, levelIndex, numberOfPerspectives):
        self.levelIndex = levelIndex
        self.vertexes = [0]*numberOfPerspectives
        return

# -> in place of Path.java
class Path:

    """
    The class is for storing the path followed by an Ant or presented to the student.
    It contains functions for adding, clearing, cloning and querying the path.
    
    @variables
    pathValue -> @Type float store the value of a path in terms of its difficulty
    vertexes -> @Type array of class Vertex store the vertexes in the path
    chosenLO -> @Type integer store the number of LOs taken in a vertex
    vertexSet -> @Type set of class Vertex store unique vertices in the path
    timeTaken -> @Type float store the time spent across the path 
    """

    def __init__(self):
        self.pathValue = -1*float('inf')
        self.vertexes = []
        self.chosenLO = []
        self.vertexSet = set([])
        self.timeTaken = 0.0

    def add(self, vertex, mask):
        """
        (Vertex, int) ---> None

        @params vertex : @Type class Vertex store the data for the new vertex
        @params mask : @Type integer store the number of LOs chosen by the user

        Function adds a new vertex to the current path including the LOs
        """

        self.vertexes.append(vertex)
        self.chosenLO.append(mask)
        self.vertexSet |= set([vertex])

    def last(self):
        " Function returns the last vertex on the current path "
        
        return self.vertexes[-1]

    def getLastEdge(self):
        "Function returns the Last edge taken in the current path "

        # get the second Last Element of the path
        source = self.vertexes[-2]

        # Brute Search for the edge that takes us to the last vertex
        for edge in source.edgeList:
            if edge.destination == self.last():
                return edge

        return None

    def clear(self):
        " Function clears the path and re-initialize it with standard attributes "

        del self.vertexes[:]
        self.vertexSet.clear()
        del self.chosenLO[:]
        self.pathValue = -1.0 * float('inf')

    def clone(self):
        " Function returns the path that is a separate entity and is similar to the current path "
        
        path = Path()
        path.pathValue = self.pathValue
        path.timeTaken = self.timeTaken
        path.vertexes = [v for v in self.vertexes]
        path.vertexSet = set([V for V in self.vertexSet])
        path.chosenLO = [mask for mask in self.chosenLO]
        return path

# -> in place of ACO.java
class ACO:
    
    """
    The class is for the Ant Colony Optimization template.
    It contains the variables for the respective algorithm.
    
    @variables
    user -> @Type class User 
    course -> @Type class Course
    maximumTime -> @Type double
    numberOfIterations -> @Type integer
    numberOfAnts -> @Type integer
    alpha -> @Type float
    beta -> @Type float
    phi -> @Type float
    evaporationRate -> @Type float
    initialPheromone -> @Type float
    ants -> @Type array of @Type class Ant
    """

    def __init__(self, user, course, maximumTime):
        """
        (User, Course, float) ---> None

        @params user : contains the object of class User
        @params course : contains the object of class Course
        @params maximumTime : Type double stores the time in ms

        Function intializes the variables of the class ACO
        """
        
        self.user = user
        self.course = course
        self.maximumTime = maximumTime
        self.numberOfIterations = course.totalNumberOfVertexes * 50
        self.numberOfAnts = 10
        self.alpha = 0.1
        self.beta = 1.2
        self.phi = maximumTime
        self.evaporationRate = 0.3
        self.initialPheromone = 0.1
        self.ants = [Ant(i) for i in range(self.numberOfAnts)]
        return

# -> in place of Ant.java
class Ant:
    
    """
    The class is for storing the attributes of an Ant.
    
    @variables
    @Static dummyVertex -> @Type class Vertex stores the starting vertex for an Ant
    antIndex -> @Type integer store the id for an Ant
    path -> @Type class Path store the path taken by the Ant
    """
    
    dummyVertex = Vertex(0,0,0.0,0)

    def __init__(self, antIndex):
        """
        (int) ---> None

        @params antIndex : @Type integer stores the id for the ants

        Function intializes the variables of the class Ant
        """

        self.antIndex = antIndex
        self.path = Path()
        self.startOver()
        return

    def visited(self, vertex):
        """
        (Vertex) ---> boolean

        @params vertex : @Type class Vertex 
        @return boolean

        Function return whether the vertex is in path or not
        """

        return vertex in self.path.vertexSet

    def startOver(self):
        " Function to start the moving of the ants on the course at a virtual vertex on the start "
        
        self.path.clear()
        self.path.add(self.dummyVertex, 0)
        return 

# -> in place of ACOExperimenter.java
class ACOExperimenter:

    """
    The class is for the Ant Colony Optimization experimenter.
    It contains the functions for the regressions of ACO on our e-learning model.
    
    @variables
    data -> @Type class ACO holds the data for Ant Colony setup
    destination -> @Type class Vertex stores the vertex to be reached
    """

    def __init__(self, data):
        """
        (ACO) ---> None

        @params data :  @Type ACO holds the data for ant Colony setup

        Function intializes the path for the working of the algorithm
        """

        self.data = data
        
        # Assumption made that the final level will have a single source of material
        self.destination = data.course.levels[len(data.course.levels)-1].vertexes[0]

        return

    def start(self, currentLearningAim, logfile):     
        """
        (int, Stream) ---> None

        @params currentLearningAim : @Type integer shows the current learning aim for user
        @params out : @Type Stream depicts the output stream for the module
        
        Function allows the regressions to start and run for numberOfIterations times
        """

        ######
        # PHASE 1 => INITIALIZATION 

        # Initialization of the variables
        bestPath = Path()                                       # The variable to store the best Path through the course
        self.initialiseAnts()                                   # Setup the Ants so that they are ready to move
        self.initialisePheromoneTrails()                        # Initialize the edges with the default pheromone levels

        #######
        # PHASE 2 => GENERATION OF PATHS

        # Make ants run for noOfIterations times
        for iteration in range(1, self.data.numberOfIterations+1):
            lastEdgeTraversed = []                              # Stores the list of the last edges taken by list of ants
            
            for ant in self.data.ants:

                # Next -> stores the vertex taken by the *ant* and add to *ant*'s path
                Next = self.takeBestChoice(ant, logfile)    
                logfile.write("Iteration: %d Ant: %d Vertex: %s\n" % (iteration, ant.antIndex, Next.toString()))

                # Randomly choose some LOs including the first one which is mandatory
                chosenLOs = (RandomUtils.getInt(1<<len(Next.SubVertexes)) | 1)
                assert chosenLOs < (1 << len(Next.SubVertexes)), "LOs chosen > LOs available by ant %d in iteration %d" % (ant.antIndex, iteration)

                # Add the choices made above to ant's path
                ant.path.add(Next, chosenLOs)
                lastEdgeTraversed.append(ant.path.getLastEdge())

                # Check if the next vertex is destination of the course
                if Next == self.destination:

                    # If yes, then compute the pathValue of this path and update the best path
                    ant.path.pathValue = ObjectiveFunction.pathValue(currentLearningAim, ant.path, recoMatrix, self.data)
                    
                    # Store Various Paths taken by ants
                    paths = open("../Standard.paths", "a")
                    paths.write("PATH {No.: %d, Ant: %d}\n" % (iteration, ant.antIndex))
                    IOUtils.printPath(ant.path, paths)
                    paths.close()

                    # Replace the best path if ant's path has better fitness
                    if bestPath.pathValue < ant.path.pathValue:
                        bestPath = ant.path.clone()
                        
                        # Additional Info, If a real path has been found
                        logfile.write("---------------------------------NEW BEST PATH----------------------------------\n")
                        logfile.write("Iteration -> %d, Ant -> %d\n" % (iteration, ant.antIndex))
                        IOUtils.printPath(bestPath, logfile)
                        logfile.write("--------------------------------------------------------------------------------\n")
                    
                    # Reset the attributes of the target ant
                    ant.startOver()

        #######
        # PHASE 3 => UPDATION OF PATH PRIORITIES
                              
            # Pheromone Updation after ants have moved along one step
            for edge in lastEdgeTraversed:

                # For the edges between vertexes of same Level
                if edge.difficulty == 0.0:
                    edge.pheromone += self.data.initialPheromone * 100
                # For the edges between vertexes at different levels
                else:
                    edge.pheromone += self.data.initialPheromone / edge.difficulty
            
            # Adjust Pheromone for the best Path to destination
            i, j = 0, 1
            while j < len(bestPath.vertexes):
                currentEdge = None
                for edge in bestPath.vertexes[i].edgeList:
                    if edge.destination == bestPath.vertexes[j]:
                        currentEdge = edge
                        break
                currentEdge.pheromone += self.data.phi * abs(bestPath.pathValue)
                i, j = i+1, j+1

            # evaporate the pheromones from the paths but do not fall below a certain threshhold    
            for i in range(self.data.course.numberOfLevels):
                for j in range(self.data.course.numberOfPerspectivesAtLevel[i]):
                    current = self.data.course.levels[i].vertexes[j]
                    for edge in current.edgeList:
                        edge.pheromone = max([self.data.initialPheromone, edge.pheromone * (1 - self.data.evaporationRate)])

        return bestPath

    def initialiseAnts(self):
        " Creates the Ants for the algorithm with respective class "

        for i in range(self.data.numberOfAnts):
            self.data.ants[i] = Ant(i)
        return

    def initialisePheromoneTrails(self):
        " Set each edge in the given Course graph to have an intial pheromone level "

        for level in self.data.course.levels:
            for source in level.vertexes:
                for edge in source.edgeList:
                    edge.pheromone = self.data.initialPheromone
        return

    def takeBestChoice(self, ant, logfile):
        """
        (Ant) ---> Vertex

        @params ant : @Type class Ant stores the ant attributes
        @return d : @Type class Vertex The destination vertex to which the ant is headed

        Function determines the probability of paths for the "ant" and return the fitness for the particular path
        """

        # Local variables
        probability = []                                # Probabilty vector for each outgoing Edge
        destinations = []                               # Vertex to which the edge terminates
        cumulativeProbability = []                      # cumulative Probability of the edge choice
        randomProbability = RandomUtils.getDouble()     # The random probability for an ant to take an edge
        assert 0.0 <= randomProbability <= 1.0, "probability out of bounds"

        logfile.write("Ant Id = %d\n" % ant.antIndex)
        for edge in ant.path.last().edgeList:            
            if not ant.visited(edge.destination):

                logfile.write("Edge data ---> " + edge.toString())
                              
                # Compute the probablity for visiting an unvisited node
                p = self.calculateProbability(edge.pheromone, edge.difficulty, ObjectiveFunction.calculateLA(edge.destination.timeAssigned, self.data.course.maximumLAAtLevel[edge.destination.levelIndex], self.data.user.learningAbility))
                logfile.write(" p = %f\n" % p)
                assert 0.0 <= p <= 1.0, "probability out of bounds"
  
                # Add it to the existing list of probabilities for the ant
                probability.append(p)
                destinations.append(edge.destination)

        # Normalize the vector obtained for probabilities and compute cumulative probablity (so that cumProb[-1] == 1)
        probability = MiscUtils.normalize(probability)
        cumulativeProbability = MiscUtils.cumulative(1.0, probability)
        assert len(cumulativeProbability) == 1 or 0.99 <= cumulativeProbability[-1] <= 1.01, "Value = " + str(cumulativeProbability)
        
        # Take the action for the ant as first unvisited node intially
        res = destinations[0]

        # Take the destination Edge as the one whose cumulative Probability lies in between the random Probability for the Ant.
        i, j = 0, 1
        while j < len(cumulativeProbability):
            if cumulativeProbability[i] <= randomProbability <= cumulativeProbability[j]:
                res = destinations[i]
            i, j = i+1, j+1

        assert res in destinations, "A vertex outside of available ones has been chosen"
        return res

    def calculateProbability(self, pheromone, difficulty, learningAchievement):
        """
        (float, float, float) ---> float

        @params pheromone : @Type float stores the pheromone level of the edge
        @params difficulty : @Type float stores the value of difficulty of the edge
        @params LA : @Type float stores the expected LA on reaching the destination
        @return f : @Type float returns the probability of taking this edge
      
        Function to compute the probability for taking a particular path by an Ant
        """

        
               # Pheromone Part               # Heuristics Part
        return (pheromone**self.data.alpha) * (learningAchievement**self.data.beta)
 
# -> in place of Solver.java
# My View: This class can be removed and the function can be moved to a newer file capable of executing any course available in above framework.
class Solver:

    """

    Function returns the fitness function value for a particular path in a particular ant Colony setup
    The main Aim of the module is :-
    1. Maximise the fitness function
    2. Stabilise the solution
    3. Analyse the solution - Concept Perspectives and LO combination exaclty or getting stuck at local optima
    4. ACOGen
    """

    def __init__(self):
        return

    def solve(self, testNumber):
        """
        (int) ---> None

        @params testNumber : @Type integer shows the number of the times code runs
        
        The function prints the Path for each type of learning Aim
        """

        user = IOUtils.readUser()
        course = IOUtils.readCourse(user)
        maximumTime = input()
        dummyVertex = Vertex(-1, -1, 0, 0)
        dummyVertex.edgeList.append(Edge(course.levels[0].vertexes[0], 0))
        Ant.dummyVertex = dummyVertex
        data = ACO(user, course, maximumTime)
        experimenter = ACOExperimenter(data)
        print "Course Structure :-"
        IOUtils.printCourse(course)
        for aim in range(user.numberOfAims):
            stats = open("StaticAim%d.log"%aim,"w")
            path = experimenter.start(aim, logfile)
            print "Path for Learning Aim  ---> " + str(aim+1)
            print path
            IOUtils.printPath(path, sys.stdout)
            stats.close()
        return

    def takeIP(self):
        " The function takes the input from the file with same name in the same folder "
        
        user = IOUtils.readUser()
        course = IOUtils.readCourse(user)
        maximumTime = input()
        return user, course, maximumTime

    def regress(self, idx, user, course, maximumTime, vertexId, aim):
        """
        (User, Course, float, array, int) ---> Path

        @params user: @Type class User The data for the target user
        @params course: @Type class Course The data for the course he is taking 
        @params maximumTime: @Type float gives the maximum time to complete the course
        @params startDifficulty: @Type integer array store the data for initial difficulty transition
        @params aim: @Type integer provides the aim number of the user
        @return path: @Type class Path returns the best possible path for the user given his main aim

        The function returns the path for the user with particular aim in the course with starting difficulty as startDifficulty
        """    

        dummyVertex = Vertex(-1, -1, 0, 0)
        dummyVertex.edgeList.append(Edge(course.levels[idx].vertexes[vertexId], 0))
        #if not idx:
        #    dummyVertex.edgeList.append(Edge(course.levels[idx].vertexes[0], 0))
        #else:
        #    for i in range(len(course.levels[idx].vertexes)):
        #        dummyVertex.edgeList.append(Edge(course.levels[idx].vertexes[i], startDifficulty[i].difficulty))
        Ant.dummyVertex = dummyVertex
        data = ACO(user, course, maximumTime)
        experimenter = ACOExperimenter(data)
        stats = open("DynamicLevel%dAim%d.log" % (idx, aim), "w")
        path = experimenter.start(aim, stats)
        stats.close()
        return path

## Function Newly Added to handle the Dynamism of the code ##
class Dynamic:

    """
    This class includes the Dynamism into the otherwise static code for ACO-e-learning

    @variables
    s -> @Type Solver class stores the main class object
    aimOfUser -> @Type integer stores the main aim of the user
    pathTaken -> @Type class Path stores the path taken by the user
    dummyVertex -> @Type class Vertex stores the virtual vertex to start the path 
    """

    def __init__(self):
        self.s = Solver()                               # Not needed if class is removed.
        self.aimOfUser = 0                              # Should be added in class User.
        self.pathTaken = Path()                         # should not be taken here. Can be global
        self.dummyVertex = Vertex(-1, -1, 0, 0)         # added for the sake of start thing, mainly to get the computation 
        self.scores = []                                # Should be added in class User.
        return
    
    def Run(self, index):
        " Function is the main function to find the path for the target user "

        user, course, maximumTime = self.s.takeIP()                                 ## Fills in required values for variables
        self.aimOfUser = input()                                                    ## Stores the aim of the user separately
        self.dummyVertex.edgeList.append(Edge(course.levels[0].vertexes[0], 0))     ## Make a virtual vertex before the graph actually start
        self.pathTaken.add(self.dummyVertex, 0)                                     ## add it to the path of the user
        self.scores.append(user.learningAbility)                                    ## keep the track of performance of the user in terms of his learning ability
        loopTimes = course.numberOfLevels                               
        remainingTime = maximumTime
        vertexId = 0                                                                ## Starting vertex id used for regress function of the solver

        global recoMatrix
        recoMatrix = [[0.0 for j in range(course.numberOfPerspectivesAtLevel[i])] for i in range(course.numberOfLevels)]
        for idx in range(loopTimes):

            ## Beautification of the output ##
            print "*"*30 + " LEVEL %d " % (idx+1) + "*"*30
            print "Time Remaining: " + str(remainingTime)
            levelId = idx-1 if idx != 0 else 0
            raw_path = self.s.regress(levelId, user, course, remainingTime, vertexId, self.aimOfUser)
            path = self.strip(raw_path, idx-1, course)                              ## To get the path which actually starts from the upcoming level
            path.pathValue = ObjectiveFunction.pathValue(self.aimOfUser, path, recoMatrix, ACO(user, course, maximumTime))
            IOUtils.printPath(path, sys.stdout)
            ##------------------------------##

            ## 1. Modification of the entities ##
            self.addLevel(path, idx)   # ----> modified
            vertexId = self.pathTaken.last().perspectiveIndex
            remainingTime = self.modifyTime(path, remainingTime, course)

            # 2. Following function works on getting new ability, simple application is used till now:-
            # -> more complex computation can be used
            # -> LALOPT table can be used for the computation as well.
            user.learningAbility, score_in_exam = self.modifyAbility(user) 
            self.scores.append(score_in_exam)
            performance = score_in_exam
            #performance = Improvement.computePerformance(self.scores, idx, score_in_exam)           

            ## 3. Adjustment of the path using the objective function. py file ##
            self.pathTaken.pathValue = ObjectiveFunction.pathValue(self.aimOfUser, self.pathTaken, recoMatrix, ACO(user, course, maximumTime))

            ## Uncomment them if you want to look at the path followed by the user step by step ##
            #print "Path followed till now :-"
            #IOUtils.printPath(self.pathTaken, sys.stdout)
    
            ##--------------------------------------------------------------##
            
            # If this level is not the end then compute the next vertex
            if (idx+1) < loopTimes:

                # Adjust the pheromone levels on the vertices which are being given either by the experts or by the recommendation
                #sVertex, p1 = self.nextVertex(path), performance / (performance + user.learningAbility)
                #sVertex, p1 = self.nextVertex(path), (performance - user.learningAbility)/(user.learningAbility) if performance > user.learningAbility else (performance)/(performance + user.learningAbility)
                #rVertex, p2 = Recommend.getRecommendations(self.aimOfUser, course, user, self.pathTaken)

                #----> Modified to return an array.
                reco_values = Recommend.getRecommendations(self.aimOfUser, course, user, self.pathTaken)
                for i,val in enumerate(reco_values):
                    recoMatrix[idx+1][i] = val
                
                # Decide which one can be taken for this purpose, by the ants basis.
                #probs = MiscUtils.cumulative(1.0, MiscUtils.normalize([p1, p2]))
                #choice = RandomUtils.getDouble()
                #vertexId = sVertex if choice <= probs[1] else rVertex
                
                #print "Static Vertex is %d" % sVertex
                #print "Recommended Vertex is %d" % rVertex
                print "Current Vertex is %d" % vertexId

        # Add the current student to the set of past students
        print "\n\nUpdating Database.......",
        Recommend.addStudent(self.pathTaken, self.scores, self.aimOfUser)
        print "done."

        # Present the regression results on Screen
        print "-"*100
        self.pathTaken.pathValue = ObjectiveFunction.pathValue(self.aimOfUser, self.pathTaken, recoMatrix, ACO(user, course, maximumTime))
        IOUtils.printPath(self.pathTaken, sys.stdout)
        print "-"*100
        ## ------- End 1. -------##
        return

    def strip(self, raw_path, levelId, course):
        """
        (Path, currentLevel, Course) ---> Path
        
        @params raw_path: @Type class Path provide the path returned from the regression function.
        @params levelId:  @Type int contains the index of the current level of the user.
        @params course:   @Type class Course contains the course structure, to link the dummy node to new start vertex for the user.
        @return path: @Type class Path modified path starting from the node, which the user is recommended by the system to take at the next level.
        
        Function strips the raw_path by removing the unncessary vertices and edges from it and constructing a path from the vertex on the upcoming level.
        """

        path = Path()
        dummyVertex = Vertex(-1, -1, 0, 0)
        start = -1
        for i in range(len(raw_path.vertexes)):
            vertex = raw_path.vertexes[i]
            if vertex.levelIndex > levelId:
                path.add(vertex, raw_path.chosenLO[i])
                if start == -1:
                    start = vertex.perspectiveIndex
                    
        dummyVertex.edgeList.append(Edge(course.levels[levelId+1].vertexes[start], 0))
        path.vertexes = [dummyVertex] + path.vertexes
        path.chosenLO = [0] + path.chosenLO
        path.vertexSet = set(path.vertexes)
        return path

    def addLevel(self, path, currentLevel):
        """
        (Path, currentLevel) ---> None

        @params path: @Type class Path provide the path being suggested to the user
        @params currentLevel: @Type int tells the id of the current level of the user, or the level whose vertices are to be added to the path.
        @note: The function modifies the class variable pathTaken with the currentLevel vertices

        Function tries to append the current level's vertices taken by user to his followed path
        """
        
        for i in range(len(path.vertexes)):
            vertex = path.vertexes[i]
            if vertex.levelIndex != -1 and vertex.levelIndex == currentLevel:
                self.pathTaken.add(vertex, path.chosenLO[i])
        return

    def modifyTime(self, path, maximumTime, course):
        """
        (Path, float, Course) ---> float

        @params path: @Type class Path store the current suggested path
        @params maximumTime: @Type float store the maximum time user can spend on course
        @params course: @Type class Course store the structure of the course
        @return remainingTime: @Type float store the value of the time remaining after giving the exam for the currentLevel

        Function is computing the value of the remaining time based on the time spent on a level
        """

        currentLevel = path.vertexes[1].levelIndex
        timeSpent = 0.0

        for i in range(len(path.vertexes)):
            vertex = path.vertexes[i]

            #print vertex.toString()
            if vertex.levelIndex != -1 and currentLevel != vertex.levelIndex:
                break

            for j in range(len(vertex.SubVertexes)):
                if (path.chosenLO[i] & 1<<j) != 0:
                    timeSpent += vertex.timeAssigned * course.LALOPT[vertex.levelIndex][self.aimOfUser][j]

        #print "%f on Level %d" % (timeSpent, currentLevel)
        return maximumTime - timeSpent

    def modifyAbility(self, user):
        """
        (User) ---> float

        @params user: @Type class User stores the data for the target user
        @return ability: @Type float stores the value of modified Ability

        @variables
        Adaptability: @range (0, 1) stores the tuning parameter
        scoreOfUser: @Type float array stores the students scores in exam
        ExamTemplate: @Type float array stores the revelance of the question to the user

        Function adjusts the currentAbility of the user based on exam results.
        """

        currentAbility = user.learningAbility
        print "Current Ability: %f" % currentAbility
        Adaptability = 0.8
        numberOfQuestions = RandomUtils.getRange(10, 15)

        scoreOfUser = Exam.getMarks(numberOfQuestions) 
        print "User's Score: ", scoreOfUser
        ExamTemplate = Exam.getTemplate(numberOfQuestions)
        print "Exam Template: ", ExamTemplate
        
        computedAbility = Exam.getScore(numberOfQuestions, scoreOfUser, ExamTemplate)
        print "Computed Ability: %f" % computedAbility
        
        return currentAbility * Adaptability + computedAbility * (1 - Adaptability), computedAbility

    
# -> in place of main.java
# My View: useless thing, the dynamic class can itself do this thing
millis = lambda: int(round(time.time()*1000))
def main():
    " Main function for the execution of StaticACO "

    # The main function and the starting point of the code #
    start = millis()
    run()
    stop = millis()
    return "Time taken: " +  str(stop - start) + " ms"

def run():
    "The actual running of the script starts from here"

    # This function is called by main and the computation work is done by this #
    testCases = input()
    dynamic = Dynamic()
    for i in range(1,testCases+1):
        dynamic.Run(i)

## These lines make sure that whenever the function is called from cmd main() is executed
if __name__=="__main__":
    oldin = sys.stdin
    sys.stdin = open("Input", "r")
    print main()
    sys.stdin = oldin
