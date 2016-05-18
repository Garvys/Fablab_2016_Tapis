import random

class TrainingData(object):
	def __init__(self):
		self.x = []
		self.y = []

		self.l = []

		myfile = open('trainingData.txt','r')
		lines = myfile.readlines()

		for i in range(int(len(lines)/2)):
			line1 = lines[2*i]
			line2 = lines[2*i+1]
			self.l.append([line1,line2])

		random.shuffle(self.l)

		for a in self.l:
			self.x.append(eval(a[0]))
			val = eval(a[1])
			if val==0:
				self.y.append([1, 0])
			else:
				self.y.append([0, 1])
