import random
from string import ascii_letters
from copy import deepcopy
import time
import threading 
from datetime import datetime
from tkinter import *
import math

#Size sensors parameters
NB_COLUMNS = 6
NB_LINES = 3

#Size of the real tapis (mètre)
WIDTH_CARPET = 2.0
HEIGHT_CARPET = 1.0

#Limite minimum pour que le capteur soit pertinent
MIN_RELEVANT = 50

#Size of GUI
WIDTH_GUI = 600
HEIGHT_GUI = 300

CASE_WIDTH = WIDTH_GUI / NB_COLUMNS
CASE_HEIGHT = HEIGHT_GUI / NB_LINES

##################################################################################################################################
#                                                                                                                                #
#                                                          Classe Data                                                           #
#                                                                                                                                #
##################################################################################################################################
class Data:
    """docstring for Grid"""
    def __init__(self, data):

    	#Récupération des données brutes
        self.listCases = deepcopy(data)

        #Création de la grille
        self.grid = []
        for i in range(NB_LINES):
        	self.grid.append([])
        	for j in range(NB_COLUMNS):
        		self.grid[i].append(0)

        for i in range(NB_LINES*NB_COLUMNS):
            self.grid[i // NB_COLUMNS][i % NB_COLUMNS] = deepcopy(int(self.listCases[i]))


        #Test de la pertinence de la donnée : y a -t -il quelqu'un sur le tapis
        self.relevant = False
        for i in range(NB_LINES*NB_COLUMNS):
            if self.listCases[i] > MIN_RELEVANT:
                self.relevant = True

    def getRedCases(self):
        l = []
        for i in range(NB_LINES):
            for j in range(NB_COLUMNS):
                if self.grid[i][j] > MIN_RELEVANT:
                    l.append((i,j))
        return l

    #Affichage de la grille
    def __str__(self):
    	p = []
    	for i in range(NB_LINES):
    		l = []
    		for j in range(NB_COLUMNS):
    			l.append(str(self.grid[i][j]))
    		s = "\t".join(l)
    		p.append(s)
    	return "\n".join(p)

##################################################################################################################################
#                                                                                                                                #
#                                                          Classe Foot                                                           #
#                                                                                                                                #
##################################################################################################################################

def degToRad(deg):
	return deg*0.0174533

#Rotation d'un point autour de (cx,cy) d'angle angle
def rotate_point(cx,cy,angle,x,y):
	s = math.sin(degToRad(angle));
	c = math.cos(degToRad(angle));

	#translate point back to origin:
	x1 = x - cx;
	y1 = y - cy;

	#rotate point
	xnew = x1 * c - y1 * s;
	ynew = x1 * s + y1 * c;

	#translate point back:
	x1 = xnew + cx;
	y1 = ynew + cy;
	return x1,y1

class Foot:
	"""docstring for Foot
		t : instant auquel est associé le pied
		x : coordonnée selon x du pied
		y : coordonnée selon y du pied
		footWidth : largeur du pied
		footHeight : hauteur du pied
		angle : angle de rotation du pied
	"""
	def __init__(self, t,x,y,footWidth,footHeight, angle):
		self.t = t
		self.x = x
		self.y = y
		self.footWidth = footWidth
		self.footHeight = footHeight
		self.angle = angle

		#A B
		#C D

		self.xG = self.x + footWidth/2.0
		self.yG = self.y + footHeight/2.0

		self.xA, self.yA = rotate_point(self.xG,self.yG,self.angle,x,y)
		self.xB, self.yB = rotate_point(self.xG,self.yG,self.angle,x + footWidth,y)
		self.xC, self.yC = rotate_point(self.xG,self.yG,self.angle,x,y + footHeight)
		self.xD, self.yD = rotate_point(self.xG,self.yG,self.angle,x + footWidth,y + footHeight)


	def printGui(self,canva):
		canva.delete("AB_1")
		canva.delete("BD_1")
		canva.delete("DC_1")
		canva.delete("CA_1")
		canva.create_line(self.xA, self.yA, self.xB,self.yB, fill="green",tags="AB_1")
		canva.create_line(self.xB, self.yB, self.xD,self.yD, fill="yellow",tags="BD_1")
		canva.create_line(self.xD, self.yD, self.xC,self.yC, fill="blue",tags="DC_1")
		canva.create_line(self.xC, self.yC, self.xA,self.yA, fill="white",tags="CA_1")
		canva.update()

##################################################################################################################################
#                                                                                                                                #
#                                                         Parseur                                                                #
#                                                                                                                                #
##################################################################################################################################

#Tableau de données
st_datas = []
st_datas_relevant = []


#Parseur
while True:
	try:
		st_datas.append(Data(list(map(int,eval(input())))))
	except EOFError:
		break

serieStart = False
for i in range(len(st_datas)):
	if serieStart and not st_datas[i].relevant:
		break
	if st_datas[i].relevant:
		st_datas_relevant.append(st_datas[i])
		serieStart = True

######################################################################################################################
#                                                                                                                    #
#                                                          Algo génétique                                            #
#                                                                                                                    #
######################################################################################################################

#min inclus et max exclus
def getRandom(n_min,n_max):
    return int(random.uniform(n_min,n_max))

#Probabilié de mutation
CHANCE_TO_MUTATE = 0.1

#Proportion des meilleurs scores gardés pour la prochaine génération
GRADED_RETAIN_PERCENT = 0.2

#Probabilité de garder un génome mal gradé
CHANCE_RETAIN_NONGRATED = 0.05

#Taille de notre population
POPULATION_COUNT = 100

#Nombre de générations à faire
GENERATION_COUNT_MAX = 1000

#Nombre dindividus gardé au bout d'une génération
GRADED_INDIVIDUAL_RETAIN_COUNT = int(POPULATION_COUNT * GRADED_RETAIN_PERCENT)

#Liste d'individu qui représente la population initiale
populationInitiale = []

class Individu:
	"""
	foots : liste de foot
	"""
	def __init__(self,footHeight,footWidth):
		#Liste des pieds à l'instant t
		self.foots = []
		self.footHeight = footHeight
		self.footWidth = footWidth

	def generateRandomIndividu(self):
		for i in range(len(st_datas_relevant)):

			angleMin, angleMax, xMin, xMax, yMin, yMax = self.getBorneNextFoot(i-1);

			#On tire au hasard l'angle (en degré)
			angle = getRandom(angleMin,angleMax)

			#On tire au hasard la position du centre de gravité
			x = getRandom(xMin,xMax)
			y = getRandom(yMin,yMax)

			self.foots.append(Foot(i,x,y,self.footWidth,self.footHeight,angle))

	def getBorneNextFoot(self, i):
		if i >= 0:
			footPrec = self.foots[i]

			GAP_ANGLE = 10
			GAP_DISTANCE = 50

			#Angle min
			angleMin = footPrec.angle - GAP_ANGLE
			while angleMin < 0:
				angleMin += 360;

			#Angle max
			angleMax = footPrec.angle + GAP_ANGLE
			while angleMax < 0:
				angleMax += 360;

			#X min
			xMin = footPrec.x - GAP_DISTANCE
			if xMin < 0:
				xMin = 0

			#X max
			xMax = footPrec.x + GAP_DISTANCE
			if xMax > WIDTH_GUI:
				xMax = WIDTH_GUI

			#yMin
			yMin = footPrec.y - GAP_DISTANCE
			if yMin < 0:
				yMin = 0

			#yMax
			yMax = footPrec.y + GAP_DISTANCE
			if yMax > HEIGHT_GUI:
				yMax = HEIGHT_GUI

			return angleMin,angleMax,xMin,xMax,yMin,yMax
		else:
			return 0,360,0,WIDTH_GUI,0,HEIGHT_GUI;


def isPointInRectangle(x,y,ax,ay,bx,by,dx,dy):
	# Pseudo code
	# Corners in ax,ay,bx,by,dx,dy
	# Point in x, y

	bax = bx - ax
	bay = by - ay
	dax = dx - ax
	day = dy - ay

	if ((x - ax) * bax + (y - ay) * bay < 0.0):
		return False
	if ((x - bx) * bax + (y - by) * bay > 0.0):
		return False
	if ((x - ax) * dax + (y - ay) * day < 0.0):
		return False
	if ((x - dx) * dax + (y - dy) * day > 0.0):
		return False

	return True




##################################################################################################################################
#                                                                                                                                #
#                                                         Tapis Gui                                                              #
#                                                                                                                                #
##################################################################################################################################

def getDist(x1,y1,x2,y2):
    return math.sqrt((x1-x2)*(x1-x2) + (y1 - y2)*(y1 - y2))

class TapisGui(Frame):

    def __init__(self, fenetre, **kwargs):
        Frame.__init__(self, fenetre, width=768, height=576, **kwargs)
        self.pack(fill=BOTH)

        self.w = Canvas(self, width=WIDTH_GUI, height=HEIGHT_GUI, bd=0,relief='ridge',)
        self.w.pack()

        self.draw_grid()
        #Foot(0.0,50.0,20.0,70.0,33.0, 270.0).printGui(self.w)
        #individu = Individu(38,15)
        #individu.generateRandomIndividu()
        #for i in range(len(st_datas_relevant)):
        #    self.printData(st_datas_relevant[i].listCases)
        #    individu.foots[i].printGui(self.w)
        #    time.sleep(0.1)


        for i in range(1):
            MARGE = 100
            x = getRandom(MARGE , WIDTH_GUI - MARGE)
            y = getRandom(MARGE , HEIGHT_GUI - MARGE)

            angle = getRandom(0,360)

            footHeight = 400 + getRandom(-100,100)
            footWidth = 150 + getRandom(-50,50)

            foot = Foot(0,x,y,footWidth,footHeight,angle)

            l = []

            cTotal = 0

            for j in range(NB_LINES*NB_COLUMNS):
                line = j // NB_COLUMNS
                col = j % NB_COLUMNS

                xMin = col*CASE_WIDTH
                yMin = line*CASE_HEIGHT

                xMax = xMin + CASE_WIDTH
                yMax = yMin + CASE_HEIGHT

                c = 0
                d = getDist(xMin,yMin,foot.xG,foot.yG)
                d = min(d,getDist(xMin,yMax,foot.xG,foot.yG))
                d = min(d,getDist(xMax,yMin,foot.xG,foot.yG))
                d = min(d,getDist(xMax,yMax,foot.xG,foot.yG))
                if d < 2*max(footHeight,footWidth):
                    for x in range(int(xMin),int(xMax+1)):

                        for y in range(int(yMin),int(yMax+1)):
                            if isPointInRectangle(x,y,foot.xA,foot.yA,foot.xB,foot.yB,foot.xD,foot.yD):
                                c += 1
                #print(c)
                cTotal += c
                x0 = 750.0
                y0 = 250.0

                a = y0 / x0
                val = 0
                if c == 0:
                    val = getRandom(0,20)
                else:
                    val = int(min(250 - getRandom(0,20),a*c))
                l.append(val)
            if cTotal > 50:
                self.printData(l)
                foot.printGui(self.w)
                print(l)
                print('1')



    def draw_grid(self):
        rect = []
        a=0
        for j in range (0,NB_LINES):
            for i in range(0,NB_COLUMNS):         
                coord = i*(WIDTH_GUI/NB_COLUMNS*1.0), \
                j*(HEIGHT_GUI/NB_LINES*1.0),\
                (i+1)*(WIDTH_GUI/NB_COLUMNS*1.0), (j+1)*(HEIGHT_GUI/NB_LINES*1.0)
                
                rect.append(self.w.create_rectangle(coord,fill="red",tags="rect"+str(a)))

                self.w.create_text(coord[0]+WIDTH_GUI/NB_COLUMNS*1.0/2.0,\
                coord[1]+HEIGHT_GUI/NB_LINES*1.0/2.0,text="0%",fill="white",tags="text"+str(a))
                #self.tag_bind(rect[len(rect)-1] , '<ButtonPress-1>', onObjectClick)
                a+=1

    def printData(self, line_input):
       
        for i in range(0,NB_LINES*NB_COLUMNS):
            r = 1
            g = 1
            b = 1

            val = int(line_input[i])   

            rgb = val, g, b
            Hex = '#%02x%02x%02x' % rgb

            #print i,'=>',rgb  
            self.w.itemconfig("rect"+str(i),fill=str(Hex))
            self.w.itemconfig("text"+str(i),text=str(val))  
            
        self.w.update()   


##################################################################################################################################
#                                                                                                                                #
#                                                          Main                                                                  #
#                                                                                                                                #
##################################################################################################################################

fenetre = Tk()
tapis_view = TapisGui(fenetre)

tapis_view.mainloop()
