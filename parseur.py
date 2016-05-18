from copy import *
import numpy as np
import matplotlib.pyplot as plt
import math

#Size sensors parameters
nb_columns = 6
nb_lines = 3

#Size of GUI
width = 600
height = 300

datas = []
st_datas = []

class Data:
    """docstring for Grid"""
    def __init__(self, data):
        self.listCases = deepcopy(data)

        self.grid = []
        self.relevant = False

        for i in range(nb_lines):
        	self.grid.append([])
        	for j in range(nb_columns):
        		self.grid[i].append(0)

        self.lineG = 0
        self.colG = 0

        self.updateGrid()

        self.calcBarycentre()

        self.toDraw()
        
        

    def toDraw(self):
        for i in range(nb_lines*nb_columns):
            if self.listCases[i] > 50:
                self.relevant = True

    def updateGrid(self):
        for i in range(nb_lines*nb_columns):
            val = self.listCases[i]

            line = deepcopy(i // nb_columns)
            col = deepcopy(i % nb_columns)


            self.grid[line][col] = deepcopy(int(val))

    def calcBarycentre(self):
    	total = 0

    	for i in range(nb_lines):
            for j in range(nb_columns):
                val = self.grid[i][j]
                poids = pow(val,3.0/2)
                total += poids

                self.lineG += poids*i
                self.colG += poids*j
    	self.lineG /= total
    	self.colG /= total

    def getCoordBarycentre(self):
        x = self.colG * width/nb_columns * 1.0 + width/nb_columns*1.0/2.0
        y = self.lineG * height/nb_lines*1.0 + height/nb_lines*1.0/2.0
        return x,y

    def __str__(self):
    	p = []
    	for i in range(nb_lines):
    		l = []
    		for j in range(nb_columns):
    			l.append(str(self.grid[i][j]))
    		s = " ".join(l)
    		p.append(s)
    	return "\n".join(p)


while True:
	try:
		s = input()
		datas.append(list(map(int,eval(s))))
		st_datas.append(Data(list(map(int,eval(s)))))
	except EOFError:
		break


#print(st_datas[1])

#fonction qui détermine la vitesse moyenne de déplacement
#nb : unité de temps et de longueur à reconsidérer ? 
def getSpeed():
    instant_speed = [] #liste des vitesses instantannées du barycentre
    mean_speed = 0
    prev_x = 0
    prev_y = 0
    prev_t = 0
    first = 1
    for t in range (len(st_datas)):
        if st_datas[t].relevant:
            if first:
                x, y = st_datas[t].getCoordBarycentre()
                prev_x, prev_y, prev_t = x, y, t
                first = 0
            else:
                x, y = st_datas[t].getCoordBarycentre()
                speed = math.sqrt((x-prev_x)**2 + (y - prev_y)**2)/(t - prev_t)
                instant_speed.append(speed)
                prev_x, prev_y, prev_t = x, y, t
    print(instant_speed)
    mean_speed = sum(instant_speed)/len(instant_speed)
    print(mean_speed)
    return (mean_speed)
            
#getSpeed()            
        


#fonction qui renvoie une liste de liste des cases ([i,j]) allumées à t 
def getCasesRed():
    list_cases_red = []
    nb = 0
    for t in range(len(st_datas)):
        if st_datas[t].relevant: #si le relevé au temps t est pertinent      
            list_cases_red.append([])
            for i in range(nb_lines):
                for j in range(nb_columns):
                    if st_datas[t].grid[i][j]>50:
                        l = [t,i,j]
                        list_cases_red[nb].append(l)

            nb += 1
    #print(list_cases_red)
    return(list_cases_red)

def checkFurniture():
    list_cases_red = getCasesRed()
    print(list_cases_red)
    list_meubles = []
    if (len(st_datas) == len(list_cases_red)): #à tous les t il y a au moins une case allumée
        for init in range(len(list_cases_red[0])):
            print(init)
            x_init, y_init = list_cases_red[0][init][1], list_cases_red[0][init][2]
            print(x_init)
            print(y_init)
            static = 1
            for t in range(len(list_cases_red)):
                #on parcourt les cases allumées à t
                current = 0
                while (static and (current < len(list_cases_red[t]))): #tant qu'on a pas retrouvé le meuble
                    if (list_cases_red[t][current][1] == x_init or list_cases_red[t][current][2] == y_init):
                        static =  1 #meuble trouvé
                    current += 1
                if (current == len(list_cases_red[t])+1): #si on a tout parcouru sans trouver le "meuble"
                    static = 0
            if static:
                print("il y a un meuble en :")
                print(x_init)
                print(y_init)
                list_meubles.append([x_init,y_init])
    print(list_meubles)
    return(list_meubles)

checkFurniture()

def coord_to_indice(i,j):
    return(i*6 + j)

def deleteFurniture():
    new_st_datas = deepcopy(st_datas)
    furniture = checkFurniture()
    if (len(furniture) == 0):
        print("il n'y a pas de meubles à enlever")
    else:
        for t in range(len(st_datas)):
            for k in range(len(furniture)):
                indice_case = coord_to_indice(furniture[k][0], furniture[k][1])
                new_st_datas[t].listCases[indice_case] = deepcopy(0)
               # print(new_st_datas[t].listCases)
            new_st_datas[t].updateGrid()
    for t in range(len(new_st_datas)):
        print(new_st_datas[t])
        print("\n")
    return(new_st_datas)
    
deleteFurniture()

#Renvoie différentes valeurs entieres suivant l'action déroulée : 0 RAS, 1 couché, 2 PLS, 3 course, 4saut, ... ?     

def getAction():
    list_cases_red = getCasesRed()
    code_retour = 0
    
    #course 
    if getSpeed()>10:
        print("course")
        code_retour = 3
        
    #chute
    for t in range(len(list_cases_red)):
        #s'il y a au moins 3 cases allumées
        if len(list_cases_red[t])>=3:
            #On regarde si la personne occupe 1 ligne ou 1 colonne = chuté couché
            #ou PLS si la personne occupe exactement 2 lignes ou 2 colonnes
            aligned_lines = 1
            aligned_columns = 1
            PLS1 = 0
            PLS2 = 0
            PLS3 = 0
            PLS4 = 0
            line = list_cases_red[t][0][1] 
            column = list_cases_red[t][0][2]
            for i in range (len(list_cases_red[t])):
                if (list_cases_red[t][i][1] != line):
                    aligned_lines = 0
                if (list_cases_red[t][i][2] != column):
                    aligned_columns = 0
                
                #si il n'y a plus l'alignement et 5 cases ou plus active, on regarde si c'est une PLS
                if (aligned_lines == 0 and aligned_columns ==0 and len(list_cases_red[t])>=5):
                    if (PLS2 != 1) and (list_cases_red[t][i][1] == (line or line+1)):
                        PLS1 = 1
                    if (PLS1 != 1) and (list_cases_red[t][i][1] == (line or line-1)):
                        PLS2 = 1
                    if (PLS4 != 1) and (list_cases_red[t][i][2] == (column or column+1)):
                        PLS3 = 1
                    if (PLS3 != 1) and (list_cases_red[t][i][2] == (column or column-1)):
                        PLS4 = 1
                    #Il est possible que 2 PLS passent à 1 en même temps et qu'il soit necessaire
                    #d'en annuler un des deux plus tard quand on fait le choix
                    if (PLS1 == 1) and (list_cases_red[t][i][1] != (line or line+1)):
                        PLS1 = 404
                    if (PLS2 == 1) and (list_cases_red[t][i][1] != (line or line-1)):
                        PLS2 = 404
                    if (PLS3 == 1) and (list_cases_red[t][i][2] != (column or column+1)):
                        PLS3 = 404
                    if (PLS4 == 1) and (list_cases_red[t][i][2] != (column or column-1)):
                        PLS4 = 404
                    
                    
            if aligned_lines or aligned_columns:
                print("couché")
                code_retour = 1
            if (PLS1==1) or (PLS2==1) or (PLS3==1) or (PLS4==1):
                print("PLS !")
                code_retour = 2         
                
    #saut
    for t in range(len(list_cases_red)-1):
        #print(list_cases_red[t])
        
        #on vérifie qu'il y a autant de cases allumées à t et t+1
        if len(list_cases_red[t])==len(list_cases_red[t+1]):
            for k in range(len(list_cases_red[t])):                 
                #on vérifie que ce sont les mêmes cases allumées et que t et t+1 ne sont pas "consécutifs" (temporellement)
                if list_cases_red[t][k][1]==list_cases_red[t+1][k][1] and list_cases_red[t][k][2]==list_cases_red[t+1][k][2] and list_cases_red[t][0][0] +1 != list_cases_red[t+1][0][0]:
                    print("saut")
                    code_retour = 4
                    
       
           
    return (code_retour)
                
def getCurve():
    global st_datas
    tabX = []
    tabY = []
    for i in range(len(st_datas)):
        if st_datas[i].relevant:
            x,y = st_datas[i].getCoordBarycentre()
            tabX.append(x)
            tabY.append(y)

    npx = np.array(tabX)
    npy = np.array(tabY)

    p = np.poly1d(np.polyfit(npx,npy,len(tabX)))

    xp = np.linspace(0,width)

    _ = plt.plot(npx,-npy,'.',xp,-p(xp),'--')

    plt.ylim(-height,0)

    plt.show()

    print(p)

#getCurve()

getAction()



import time
import threading 
from datetime import datetime
from tkinter import *

class TapisGui(Frame):

    def __init__(self, fenetre, **kwargs):
        Frame.__init__(self, fenetre, width=768, height=576, **kwargs)
        self.pack(fill=BOTH)

        self.w = Canvas(self, width=width, height=height, bd=0,relief='ridge',)
        self.w.pack()

        self.draw_grid()
        for i in range(len(datas)):
            self.printData(datas[i])
            if st_datas[i].relevant:
                x,y = st_datas[i].getCoordBarycentre()
                r = 5
                self.w.create_oval(x - r, y - r, x + r, y + r,fill="white")
                self.w.update()
            time.sleep(0.1)
            



    def draw_grid(self):
        rect = []
        a=0
        for j in range (0,nb_lines):
            for i in range(0,nb_columns):         
                coord = i*(width/nb_columns*1.0), \
                j*(height/nb_lines*1.0),\
                (i+1)*(width/nb_columns*1.0), (j+1)*(height/nb_lines*1.0)
                
                rect.append(self.w.create_rectangle(coord,fill="red",tags="rect"+str(a)))

                self.w.create_text(coord[0]+width/nb_columns*1.0/2.0,\
                coord[1]+height/nb_lines*1.0/2.0,text="0%",fill="white",tags="text"+str(a))
                #self.tag_bind(rect[len(rect)-1] , '<ButtonPress-1>', onObjectClick)
                a+=1

    def printData(self, line_input):
       
        for i in range(0,nb_lines*nb_columns):
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


fenetre = Tk()
tapis_view = TapisGui(fenetre)

tapis_view.mainloop()
