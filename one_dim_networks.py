import matplotlib.pyplot as plt
import numpy as np
#from sklearn.neural_network import MLPClassifier
from keras.models import Sequential, load_model
from keras.layers import Dense, Convolution1D, Convolution2D,Flatten
from matplotlib.colors import LinearSegmentedColormap
import time
from keras.utils import np_utils
##### Loading Data #############################################################


data2001 = './data/KGS-2001-19-2298-train10k.dat'
data2002 = './data/KGS-2002-19-3646-train10k.dat'
data2003 = './data/KGS-2003-19-7582-train10k.dat'
data2004 = './data/KGS-2004-19-12106-train10k.dat'
data2005 = './data/KGS-2005-19-13941-train10k.dat'
data2006 = './data/KGS-2006-19-10388-train10k.dat'
data2007 = './data/KGS-2007-19-11644-train10k.dat'


goboard1 = open(data2001, "rb")
goboard2 = open(data2002, "rb")
goboard3 = open(data2003, "rb")
goboard4 = open(data2004, "rb")
goboard5 = open(data2005, "rb")
goboard6 = open(data2006, "rb")
goboard7 = open(data2007, "rb")
'''
pos1 = list(goboard1.read())
pos2 = list(goboard2.read())
pos3 = list(goboard3.read())
pos4 = list(goboard4.read())
pos5 = list(goboard5.read())
pos6 = list(goboard6.read())
pos7 = list(goboard7.read())


goboard1.close()
goboard2.close()
goboard3.close()
goboard4.close()
goboard5.close()
goboard6.close()
goboard7.close()
'''
testset = open('./data/kgsgo-test.dat', "rb")
dataset = open ('./data/kgsgo-test.dat', "rb")#train10k.dat', "rb")

#pos = np.array(list(full_set.read()))
pos = np.array(list(dataset.read()))
# testset.close()
dataset.close()
# transform data to numpy array
#pos = np.concatenate((pos1[:len(pos1)-3],pos3[:len(pos3)-3],pos4[:len(pos4)-3],pos5[:len(pos5)-3], pos6[:len(pos6)-3], pos7[:len(pos7)-3], pos2))
#pos = np.array(pos4)
#np.array(pos)
# single moves are stored as: 2 bytes GO, 2 bytes next move, 19*19 = 361 Bytes Board
bytes_per_move = 365
number_of_moves = int(pos.shape[0]/bytes_per_move)

# array of all moves from file:
go_game = np.zeros((number_of_moves, bytes_per_move))

for move in np.arange(number_of_moves):
    go_game[move] = pos[(move*bytes_per_move):((move+1)*bytes_per_move)]

# get coordinates of next move
next_move = (go_game[:, 2:4]).astype(int)

go_game = go_game[:, 4:] #discard first 4 entries with GO, label for next move

# on final (plotable) go board store data as follows : own stone 1, enemy stone 0,
#                                                      empty field 0.5
go_game_bits = np.unpackbits(go_game.astype(np.uint8), axis=1)
go_game_bits = np.reshape(go_game_bits, (go_game_bits.shape[0], -1, 8))

raw_board = np.zeros_like(go_game)

del pos


#check which bits are 1, depending on which bit might be 1 add/subtract 0.5
# if own stone on field one of bits 2-5 will be 1 -> add 0.5,
# enemy stone on field -> bit 6-8 will be 1 -> subtract 0.5
for i in np.arange(2,5):
    raw_board +=  go_game_bits[:,:,i]
for i in np.arange(5,8):
    raw_board -=  go_game_bits[:,:,i]

print ("loaded %d board positions" % number_of_moves )

training_data = np.reshape(raw_board, (number_of_moves, 19, 19, 1))

del raw_board

target_vectors = np.zeros((number_of_moves, 19 * 19))
target_vectors[np.arange(number_of_moves), 19 * next_move[:,0] + next_move[:,1]] = 1

labels = np.reshape(target_vectors, (number_of_moves, 19 * 19))

del target_vectors
#########################################################################
# Training :
# choose model from: 'CRS_network.h5' -> convolutional - ReLu -> softmax layer
#                    './networks/CS_network.h5' > Conv (4 * 5x5) -> softmax
used_model = './networks/C32S_network.h5'

model = load_model(used_model)
'''
#model = Sequential()

#con_layer = Convolution2D(4, 5,5, border_mode='same', input_shape=(19, 19, 1), name = 'con_layer' )
#model.add(con_layer)

model.add(Convolution2D(4, 5,5, border_mode='same', input_shape=(19, 19, 1), name = 'con_layer' ))
model.add(Flatten())
model.add(Dense(361, init = 'uniform', activation = 'relu'))
model.add(Dense(361, init = 'uniform', activation = 'softmax'))


model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
'''

print("total number of Parameters: ", model.count_params())

#hist = model.fit(training_data,labels, nb_epoch=5, batch_size= 8 * 256, validation_split = 0.1)
# store training results in same file:
'''
model.save(used_model)

weights = []
#for layer in model.layers:

weights = np.array(model.layers[0].get_weights())

weights = weights[0]
#print(weights)

weights = np.reshape(weights, (32,5,5))

#print(weights[0])

fig = plt.figure(figsize = (8,8))

plt1 = fig.add_subplot(2,2,1)
plt2 = fig.add_subplot(2,2,2)
plt3 = fig.add_subplot(2,2,3)
plt4 = fig.add_subplot(2,2,4)

plt1.imshow(weights[0])
plt2.imshow(weights[1])
plt3.imshow(weights[2])
plt4.imshow(weights[3])

plt.show()

#print(weights)
#print("total number of Parameters: ", model.count_params())
#for weight_matrix in weights[0]:

########################################################################################
#plotting training history:
fig = plt.figure(figsize = (8,8))
plt.xlabel("Epoch")
plt.xlabel("Loss")
plt.title("Training History")
#plt.plot(hist.history['val_acc'], label ='validation accuracy')
plt.plot(hist.history['loss'], label ='training loss')
plt.plot(hist.history['val_loss'], label ='validation loss')
#plt.plot(hist.history['acc'], label ='training accuracy')

plt.legend(loc = 'best')
'''
start_time = int(round(time.time() * 1000))
predictions = model.predict(training_data, verbose = 1)
print ("prediction time: ", (int(round(time.time() * 1000))-start_time)/number_of_moves, "milliseconds")
predictions.reshape(number_of_moves, 19,19)
#print (len(predictions), len(predictions[1]),len(predictions[1]))

#########################################################################################
acc = 0
for i in range(number_of_moves):
    predicted_move = np.argmax(predictions[i])
    predicted_move = [int(predicted_move/19), predicted_move % 19]
    #print ("real move: ", next_move[i], "  predicted move: ", predicted_move)
    if next_move[i][0] == predicted_move[0] and predicted_move[1] == next_move[i][1]:
        acc +=1

print ( acc/number_of_moves*100 , "percent of moves predicted correctly (training and validation data)" )

# to also test accuracy on test set apply same steps as in the beginning once again to the test set
# fiinally do predictions on test set as before, compare with labels

test = np.array(list(testset.read()))
testset.close()

# single moves are stored as: 2 bytes GO, 2 bytes next move, 19*19 = 361 Bytes Board
bytes_per_move = 365
number_of_moves = int(test.shape[0]/bytes_per_move)

# array of all moves from file:
go_game = np.zeros((number_of_moves, bytes_per_move))

for move in np.arange(number_of_moves):
    go_game[move] = test[(move*bytes_per_move):((move+1)*bytes_per_move)]

# get coordinates of next move
next_move = (go_game[:, 2:4]).astype(int)

go_game = go_game[:, 4:] #discard first 4 entries with GO, label for next move

# on final (plotable) go board store data as follows : own stone 1, enemy stone 0,
#                                                      empty field 0.5
go_game_bits = np.unpackbits(go_game.astype(np.uint8), axis=1)
go_game_bits = np.reshape(go_game_bits, (go_game_bits.shape[0], -1, 8))

raw_board = np.zeros_like(go_game)
#raw_board += 0.5

#check which bits are 1, depending on which bit might be 1 add/subtract 0.5
# if own stone on field one of bits 2-5 will be 1 -> add 0.5,
# enemy stone on field -> bit 6-8 will be 1 -> subtract 0.5
for i in np.arange(2,5):
    raw_board +=  go_game_bits[:,:,i]
for i in np.arange(5,8):
    raw_board -= go_game_bits[:,:,i]

test_data = np.reshape(raw_board, (number_of_moves, 19, 19, 1))

predictions = model.predict(test_data, verbose = 1)
predictions.reshape(number_of_moves, 19,19)

#########################################################################################
acc = 0
for i in range(number_of_moves):
    predicted_move = np.argmax(predictions[i])
    predicted_move = [int(predicted_move/19), predicted_move % 19]
    #print ("real move: ", next_move[i], "  predicted move: ", predicted_move)
    if next_move[i][0] == predicted_move[0] and predicted_move[1] == next_move[i][1]:
        acc +=1

print ( acc/number_of_moves*100 , "percent of moves predicted correctly (test data)" )

plt.show()
