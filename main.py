import pygame as pg
import math as m
import random as r


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (100, 100, 0)
TEAL = (0, 80, 80)


scale = 6

numAnts = 1000
leetQ = 5
initFeromone = 1.0


foodList = []
numFood = 30
minFoodDistance = 20
maxFoodDistance = 100
foodAmounts = []
initialFoodAmount = 50


numObstacles = 4000
freeSpace = 3


alpha = 3
beta = 3
q = 100
p = 0.0003
gp = 0.0007

pg.init()
pg.display.set_caption("Hangya algoritmus")
screen = pg.display.set_mode([int(100 * scale), int(100 * scale)])
clock = pg.time.Clock()
ants = []
matrix = []
spawnX, spawnY = 0, 0
iterations = 0

enableDrawAnts = True
enableMessages = True
enableLostMessage = False

started = False
posx = 0
posy = 0

class Ant:
    global spawnX
    global spawnY

    def __init__(self, x, y, leet):
        self.x = x
        self.y = y
        self.tabooList = []
        self.putFeromone = False
        self.l0 = 0
        self.tabooListIndex = 0
        self.leet = leet
        self.id = r.randint(10000000, 99999999)


    def move(self, dir):
        if [self.x, self.y] not in self.tabooList:
            self.tabooList.append([self.x, self.y])
        dx, dy = 0, 0

        if dir == 0:
            dy = -1
        if dir == 1:
            dy = -1
            dx = 1
        if dir == 2:
            dx = 1
        if dir == 3:
            dx = 1
            dy = 1
        if dir == 4:
            dy = 1
        if dir == 5:
            dy = 1
            dx = -1
        if dir == 6:
            dx = -1
        if dir == 7:
            dx = -1
            dy = -1

        self.x += dx
        self.y += dy

        if [self.x, self.y] not in self.tabooList:
            self.tabooList.append([self.x, self.y])

        if (dx * dy == 0):
            self.l0 += 1
        else:
            self.l0 += 2 ** .5

    def tryMove(self, dir):
        if dir == 0:
            return [self.x, self.y - 1]
        if dir == 1:
            return [self.x + 1, self.y - 1]
        if dir == 2:
            return [self.x + 1, self.y]
        if dir == 3:
            return [self.x + 1, self.y + 1]
        if dir == 4:
            return [self.x, self.y + 1]
        if dir == 5:
            return [self.x - 1, self.y + 1]
        if dir == 6:
            return [self.x - 1, self.y]
        if dir == 7:
            return [self.x - 1, self.y - 1]


    def getFeromone(self, dir):
        feromoneX = self.x
        feromoneY = self.y
        if dir == 0:
            feromoneY = self.y - 1
        if dir == 1:
            feromoneY = self.y - 1
            feromoneX = self.x + 1
        if dir == 2:
            feromoneX = self.x + 1
        if dir == 3:
            feromoneX = self.x + 1
            feromoneY = self.y + 1
        if dir == 4:
            feromoneY = self.y + 1
        if dir == 5:
            feromoneY = self.y + 1
            feromoneX = self.x - 1
        if dir == 6:
            feromoneX = self.x - 1
        if dir == 7:
            feromoneX = self.x - 1
            feromoneY = self.y - 1

        if type(matrix[feromoneX][feromoneY]) == type(0.0):
            return matrix[feromoneX][feromoneY]
        else:
            return initFeromone * 10000


    def getInverseDistance(self, dir):
        if (dir == 0) or (dir == 2) or (dir == 4) or (dir == 6):
            return 1.0
        else:
            return float(1 / 2 ** .5)


    possibleTurns = []

    def addPossibleTurns(self, arr):
        self.possibleTurns = []
        for i in arr:
            pp = self.tryMove(i)
            if not (pp in self.tabooList) and (pp[0] in range(0, 100)) and (pp[1] in range(0, 100)) and (
                    matrix[pp[0]][pp[1]] != "obstacle"):
                self.possibleTurns.append(i)


    def respawn(self):
        self.x = spawnX
        self.y = spawnY
        self.tabooList = []
        self.putFeromone = False
        self.tabooListIndex = 0
        self.l0 = 0
        if (enableMessages) and (enableLostMessage):
            print("A hangya a számmal", self.id, "elveszett!")


    def turn(self):
        if not self.putFeromone:


            if (self.x == 0) and (self.y == 0):
                self.addPossibleTurns([2, 3, 4])
            if (self.x == 0) and (self.y == 99):
                self.addPossibleTurns([0, 1, 2])
            if (self.x == 99) and (self.y == 0):
                self.addPossibleTurns([4, 5, 6])
            if (self.x == 99) and (self.y == 99):
                self.addPossibleTurns([6, 7, 0])
            if (self.x == 0) and (self.y in range(1, 99)):
                self.addPossibleTurns([0, 1, 2, 3, 4])
            if (self.x == 99) and (self.y in range(1, 99)):
                self.addPossibleTurns([0, 4, 5, 6, 7])
            if (self.y == 0) and (self.x in range(1, 99)):
                self.addPossibleTurns([2, 3, 4, 5, 6])
            if (self.y == 99) and (self.x in range(1, 99)):
                self.addPossibleTurns([6, 7, 0, 1, 2])
            if (self.x in range(1, 99)) and (self.y in range(1, 99)):
                self.addPossibleTurns([0, 1, 2, 3, 4, 5, 6, 7])

            summ = 0
            probabilities = []
            for i in self.possibleTurns:
                summ += self.getInverseDistance(i) ** beta * self.getFeromone(i) ** alpha
            for i in self.possibleTurns:
                probabilities.append(self.getInverseDistance(i) ** beta * self.getFeromone(i) ** alpha / summ)

            if not self.leet:
                def sumFirstElements(arr, end):
                    summ = 0
                    if end >= len(arr):
                        end = len(arr) - 1
                    for i in range(0, end):
                        summ += arr[i]
                    return summ


                probRange = []
                for i in range(0, len(probabilities)):
                    probRange.append(sumFirstElements(probabilities, i))

                def selectDir():
                    if (len(self.possibleTurns) > 0):
                        rand = r.random()
                        for i in range(len(probRange) - 1):
                            if (rand >= probRange[i]) and (rand < probRange[i + 1]):
                                return self.possibleTurns[i]
                        if rand >= probRange[-1]:
                            return self.possibleTurns[-1]
                    else:
                        self.respawn()
            else:
                def selectDir():
                    if (len(self.possibleTurns) > 0):
                        maxProb = max(probabilities)
                        maxIndexes = [i for i, j in enumerate(probabilities) if j == maxProb]
                        return self.possibleTurns[r.choice(maxIndexes)]
                    else:
                        self.respawn()

            newDir = selectDir()
            self.move(newDir)

            if (matrix[self.x][self.y] == "food"):
                leetStr = ""
                if self.leet:
                    leetStr = "Ez egy ELIT hangya."
                if enableMessages:
                    print("Hangya számmal ", self.id, "megtalált", "%#3d" % foodAmounts[foodList.index([self.x, self.y])],
                          "táplálékegységek a koordinátákon", self.x, self.y, "за", "%#10f" % self.l0, "lépések!", leetStr)
                self.putFeromone = True

                if (initialFoodAmount != 0):
                    foodAmounts[foodList.index([self.x, self.y])] -= 1
                    if foodAmounts[foodList.index([self.x, self.y])] == 0:
                        matrix[self.x][self.y] = initFeromone
                        self.putFeromone = False
                        if enableMessages:
                            print("Étel a koordinátákon", self.x, self.y, "véget ért, de a feromon maradt!")

        else:  # if putFeromone
            self.tabooListIndex += 1
            self.x = self.tabooList[-self.tabooListIndex][0]
            self.y = self.tabooList[-self.tabooListIndex][1]

            if type(matrix[self.x][self.y]) == type(0.0):
                newTau = (1 - p) * matrix[self.x][self.y] + q / self.l0
                matrix[self.x][self.y] = newTau

            if (matrix[self.x][self.y] == "spawn"):
                self.respawn()
        return


def drawPoint(color, alpha, x, y):
    s = pg.Surface((scale, scale))
    s.set_alpha(alpha)
    s.fill(color)
    screen.blit(s, (x * scale, y * scale))

    return (x * scale, y * scale)


def initField(x,y):
    for i in range(100):
        matrix.append([])
        for j in range(100):
            matrix[i].append(initFeromone)
    global spawnX
    global spawnY
    spawnX = x // 6
    spawnY = y // 6
    matrix[spawnX][spawnY] = "spawn"
    #Randomizációk

    # global foodList
    # for i in range(numFood):
    #     putFoodSuccess = False
    #     while not putFoodSuccess:
    #         foodX = r.randint(5, 94)
    #         foodY = r.randint(5, 94)
    #         foodXSuccess = (abs(foodX - spawnX) in range(minFoodDistance, maxFoodDistance)) and (
    #                     abs(foodY - spawnY) in range(0, maxFoodDistance))
    #         foodYSuccess = (abs(foodY - spawnY) in range(minFoodDistance, maxFoodDistance)) and (
    #                     abs(foodX - spawnX) in range(0, maxFoodDistance))
    #         if foodXSuccess or foodYSuccess:
    #             if [foodX, foodY] not in foodList:
    #                 foodList.append([foodX, foodY])
    #                 foodAmounts.append(initialFoodAmount)
    #                 matrix[foodX][foodY] = "food"
    #                 putFoodSuccess = True

    # for i in range(numObstacles):
    #     putObstacleSuccess = 0
    #     while putObstacleSuccess < numFood + 1:
    #         obstacleX = r.randint(0, 99)
    #         obstacleY = r.randint(0, 99)
    #         if not ((matrix[obstacleX][obstacleY] == "obstacle") and (matrix[obstacleX][obstacleY] == "food") and (
    #                 matrix[obstacleX][obstacleY] == "spawn")):
    #             spawnXSuccess = (obstacleX <= spawnX - freeSpace) or (obstacleX >= spawnX + freeSpace)
    #             spawnYSuccess = (obstacleY <= spawnY - freeSpace) or (obstacleY >= spawnY + freeSpace)
    #             if spawnXSuccess or spawnYSuccess:
    #                 putObstacleSuccess += 1
    #             else:
    #                 putObstacleSuccess = 0
    #                 continue
    #             for i in range(numFood):
    #                 foodX = foodList[i][0]
    #                 foodY = foodList[i][1]
    #                 foodXSuccess = (obstacleX <= foodX - freeSpace) or (obstacleX >= foodX + freeSpace)
    #                 foodYSuccess = (obstacleY <= foodY - freeSpace) or (obstacleY >= foodY + freeSpace)
    #                 if foodXSuccess or foodYSuccess:
    #                     putObstacleSuccess += 1
    #                 else:
    #                     putObstacleSuccess = 0
    #                     continue
    #     matrix[obstacleX][obstacleY] = "obstacle"


def drawField():
    screen.fill(WHITE)
    for i in range(100):
        for j in range(100):
            if matrix[i][j] == "spawn":
                drawPoint(BLUE, 255, i, j)
            elif matrix[i][j] == "food":
                if (initialFoodAmount > 0):
                    foodAlpha = foodAmounts[foodList.index([i, j])] / initialFoodAmount * 200 + 55
                else:
                    foodAlpha = 255
                drawPoint(RED, foodAlpha, i, j)
            elif matrix[i][j] == "obstacle":
                drawPoint(BLACK, 20, i, j)
            else:
                feromoneGray = 255 - (matrix[i][j] - initFeromone) * 1.4
                feromoneGreen = 2 * feromoneGray
                if (feromoneGray > 255):
                    feromoneGray = 255
                if (feromoneGray < 0):
                    feromoneGray = 0
                if (feromoneGreen > 255):
                    feromoneGreen = 255
                if (feromoneGreen < 50):
                    feromoneGreen = 50
                drawPoint((feromoneGray, feromoneGreen, feromoneGray), 255, i, j)



def createAnts():
    numLeet = int(leetQ / 100 * numAnts)

    for i in range(numAnts):
        ants.append(Ant(spawnX, spawnY, False))


    while (numLeet > 0):
        leetCandidate = r.choice(ants)
        if not leetCandidate.leet:
            leetCandidate.leet = True
            numLeet -= 1
            if enableMessages:
                print("Hangya számozott", "%#10d" % leetCandidate.id, "szerencsés! ELIT lett.")


def drawAndMoveAnts():
    for ant in ants:
        ant.turn()
        if enableDrawAnts:
            if not ant.leet:
                drawPoint(BLACK, 70, ant.x, ant.y)
            else:
                drawPoint(TEAL, 127, ant.x, ant.y)


def globalEvaporate():
    for i in range(100):
        for j in range(100):
            if type(matrix[i][j]) == type(0.0):
                matrix[i][j] *= (1 - gp);


def noFood():
    if initialFoodAmount > 0:
        for i in foodAmounts:
            if i > 0:
                return False
        return True
    else:
        return False


def inc():
    global iterations
    iterations += 1

def pre(a, x,y):
    for i in range(100):
        matrix.append([])
        for j in range(100):
            matrix[i].append(initFeromone)
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        if pg.mouse.get_pressed()[2]:
            a = pg.mouse.get_pos()
            x, y = a
            matrix[x//6][y//6] = "obstacle"
            print(a)
        if pg.mouse.get_pressed()[1]:
            a = pg.mouse.get_pos()
            x, y = a
            global foodList
            foodX = x // 6
            foodY = y // 6
            foodXSuccess = foodX
            foodYSuccess = foodY
            if foodXSuccess or foodYSuccess:
                if [foodX, foodY] not in foodList:
                    foodList.append([foodX, foodY])
                    foodAmounts.append(initialFoodAmount)
                    matrix[foodX][foodY] = "food"
                    putFoodSuccess = True
            print(a)
        if pg.mouse.get_pressed()[0]:
            a = pg.mouse.get_pos()
            x,y = a
            global posx
            global posy
            posx = x
            posy = y
            print(posx)

            #main(x,y)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                main(posx,posy)
        drawField()
        pg.display.flip()
        clock.tick()
        globalEvaporate()
        inc()
    pg.quit()

def main(osx, osy):
    global  posx
    osx = posx
    global posy
    osy = posy
    initField(osx, osy)
    createAnts()
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        if pg.mouse.get_pressed()[2]:
            a = pg.mouse.get_pos()
            x, y = a
            matrix[x // 6][y // 6] = "obstacle"
            print(a)
        if pg.mouse.get_pressed()[1]:
            a = pg.mouse.get_pos()
            x, y = a
            global foodList
            foodX = x // 6
            foodY = y // 6
            foodXSuccess = foodX
            foodYSuccess = foodY
            if foodXSuccess or foodYSuccess:
                if [foodX, foodY] not in foodList:
                    foodList.append([foodX, foodY])
                    foodAmounts.append(initialFoodAmount)
                    matrix[foodX][foodY] = "food"
                    putFoodSuccess = True
            print(a)


        drawField()
        drawAndMoveAnts()
        pg.display.flip()
        clock.tick()
        globalEvaporate()
        inc()
        if noFood():
            global enableMessages
            if (enableMessages):
                print("A hangyák megették az összes ételt! Ez kellett nekik.", iterations, "iterációk.")
                enableMessages = False
    pg.quit()

pre(0, 0, 0)
