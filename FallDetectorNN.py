import tensorflow as tf
import trainingData

class LinearModel:
	def __init__(self, data):

		#On récupère la longueur de l'ensemble de training
		self.nbData = len(data.x)

		#On ne va utiliser que 5/6 du dataset pour entrainer notre modèle, le reste sera pour la validation
		self.nbTraining = self.nbData * 5 / 6

		#On scinde les tables en deux, la première partie pour le training et la seconde pour la validation
		self.trainingDataX = data.x[:self.nbTraining]
		self.trainingDataY = data.y[:self.nbTraining]
		self.validationDataX = data.x[self.nbTraining:]
		self.validationDataY = data.y[self.nbTraining:]

		#On définit les paramètres de notre modèle
		#x = placeholder puisque c'est la variable d'entrée i.e une matrice 3*6
		self.x = tf.placeholder(tf.float32, [None, 3 * 6])
		#W et b correspondent aux variables de notre régression linéaire : y = x*W + b
		self.W = tf.Variable(tf.zeros([3 * 6, 2]))
		self.b = tf.Variable(tf.zeros([2]))
		#Le softmax va permettre de convertir une valeur en probabilitée
		self.y = tf.nn.softmax(tf.matmul(self.x, self.W) + self.b)

		#Placeholder qui va contenir les réponses correctes
		self.y_ = tf.placeholder(tf.float32, [None, 2])

		#Calcul la cross entropy
		self.cross_entropy = tf.reduce_mean(-tf.reduce_sum(self.y_ * tf.log(tf.clip_by_value(self.y, 1e-10, 1.0)), reduction_indices=[1]))
		
		#Descente de gradient pour minimiser la cross entropie
		self.train_step = tf.train.GradientDescentOptimizer(0.5).minimize(self.cross_entropy)

		#Prediction correcte?
		self.correct_prediction = tf.equal(tf.argmax(self.y, 1), tf.argmax(self.y_, 1))

		#Moyenne de précision
		self.accuracy = tf.reduce_mean(tf.cast(self.correct_prediction, tf.float32))

		#Lancement du modèle dans une session
		self.sess = tf.Session()
		self.sess.run(tf.initialize_all_variables())

		#Entrainement
		batchSize = 1000
		for i in xrange(100):
			batchX = [self.trainingDataX[j % len(self.trainingDataX)] for j in xrange(i * batchSize, (i + 1) * batchSize)]
			batchY = [self.trainingDataY[j % len(self.trainingDataY)] for j in xrange(i * batchSize, (i + 1) * batchSize)]
			
			#trainingAccuracy = self.sess.run(self.accuracy, feed_dict = {self.x : batchX, self.y_: batchY})
			#print("LM : step %d, training accuracy %g" % (i, trainingAccuracy))
			
			self.sess.run(self.train_step, feed_dict = {self.x : batchX, self.y_ : batchY})

		#Calcul de poucentage de bonne réponse sur la trainingSet et ValidationSet
		self.trainingAccuracy = self.sess.run(self.accuracy, feed_dict = {self.x : self.trainingDataX, self.y_: self.trainingDataY})
		self.validationAccuracy = self.sess.run(self.accuracy, feed_dict = {self.x : self.validationDataX, self.y_: self.validationDataY})

		print "LM : Training accuracy =", self.trainingAccuracy
		print "LM : Validation accuracy =", self.validationAccuracy

		#Permet de faire une prédiction
	def predict(self, x):
		return self.sess.run(self.y, feed_dict = {self.x : x})



class NeuralNetwork:
	def weight_variable(self, shape):
		initial = tf.truncated_normal(shape, stddev=0.1)
		return tf.Variable(initial)

	def bias_variable(self, shape):
		initial = tf.constant(0.1, shape=shape)
		return tf.Variable(initial)

	def conv2d(self, x, W):
		return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

	def max_pool_2x2(self, x):
		return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

	def __init__(self, data):
		self.nbData = len(data.x)
		self.nbTraining = self.nbData * 5 / 6

		self.trainingDataX = data.x[:self.nbTraining]
		self.trainingDataY = data.y[:self.nbTraining]
		self.validationDataX = data.x[self.nbTraining:]
		self.validationDataY = data.y[self.nbTraining:]

		self.x = tf.placeholder(tf.float32, [None, 3 * 6])
		self.W = tf.Variable(tf.zeros([3 * 6, 2]))
		self.b = tf.Variable(tf.zeros([2]))

		self.y_ = tf.placeholder(tf.float32, [None, 2])

		self.x_image = tf.reshape(self.x, [-1, 3, 6, 1])
		self.W_conv1 = self.weight_variable([2, 2, 1, 32])
		self.b_conv1 = self.bias_variable([32])
		self.h_conv1 = tf.nn.relu(self.conv2d(self.x_image, self.W_conv1) + self.b_conv1)
		self.h_pool1 = self.max_pool_2x2(self.h_conv1)
		self.W_conv2 = self.weight_variable([2, 2, 32, 64])
		self.b_conv2 = self.bias_variable([64])
		self.h_conv2 = tf.nn.relu(self.conv2d(self.h_pool1, self.W_conv2) + self.b_conv2)
		self.h_pool2 = self.max_pool_2x2(self.h_conv2)
		self.W_fc1 = self.weight_variable([2 * 64, 1024])
		self.b_fc1 = self.bias_variable([1024])
		self.h_pool2_flat = tf.reshape(self.h_pool2, [-1, 2 * 64])
		self.h_fc1 = tf.nn.relu(tf.matmul(self.h_pool2_flat, self.W_fc1) + self.b_fc1)
		self.keep_prob = tf.placeholder(tf.float32)
		self.h_fc1_drop = tf.nn.dropout(self.h_fc1, self.keep_prob)
		self.W_fc2 = self.weight_variable([1024, 2])
		self.b_fc2 = self.bias_variable([2])
		self.y = tf.nn.softmax(tf.matmul(self.h_fc1_drop, self.W_fc2) + self.b_fc2)

		self.cross_entropy = tf.reduce_mean(-tf.reduce_sum(self.y_ * tf.log(tf.clip_by_value(self.y, 1e-10, 1.0)), reduction_indices=[1]))
		self.train_step = tf.train.AdamOptimizer(1e-4).minimize(self.cross_entropy)
		self.correct_prediction = tf.equal(tf.argmax(self.y, 1), tf.argmax(self.y_, 1))
		self.accuracy = tf.reduce_mean(tf.cast(self.correct_prediction, tf.float32))
		
		self.sess = tf.Session()
		self.sess.run(tf.initialize_all_variables())
		
		batchSize = 1000
		for i in xrange(1000):
			batchX = [self.trainingDataX[j % len(self.trainingDataX)] for j in xrange(i * batchSize, (i + 1) * batchSize)]
			batchY = [self.trainingDataY[j % len(self.trainingDataY)] for j in xrange(i * batchSize, (i + 1) * batchSize)]
			
			trainingAccuracy = self.sess.run(self.accuracy, feed_dict = {self.x : batchX, self.y_: batchY, self.keep_prob: 1.0})
			print("NN : step %d, training accuracy %g" % (i, trainingAccuracy))
			
			self.sess.run(self.train_step, feed_dict = {self.x: batchX, self.y_: batchY, self.keep_prob: 0.5})

		self.trainingAccuracy = self.sess.run(self.accuracy, feed_dict = {self.x : self.trainingDataX, self.y_: self.trainingDataY, self.keep_prob: 1.0})
		self.validationAccuracy = self.sess.run(self.accuracy, feed_dict = {self.x : self.validationDataX, self.y_: self.validationDataY, self.keep_prob: 1.0})

		print "NN : Training accuracy =", self.trainingAccuracy
		print "NN : Validation accuracy =", self.validationAccuracy

	def predict(self, x):
		return self.sess.run(self.y, feed_dict = {self.x : x, self.keep_prob: 1.0})
	


data = trainingData.TrainingData()
lm = LinearModel(data)
nn = NeuralNetwork(data)
