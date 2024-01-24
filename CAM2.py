# -*- encoding: utf-8 -*-

import chess
from numpy import array
from tensorflow import constant_initializer, random
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Flatten, InputLayer, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.initializers import RandomNormal
import chess.engine
import tensorflow as tf
import logging
from threading import Thread, Lock
from tqdm import tqdm
from random import randint

stockfish = "C:\\Users\\federico\\Desktop\\Scacchi\\stockfish\\stockfish-windows-x86-64-avx2.exe"

class Model:
    def __init__(self):
        self.model = ...
        self.predict = lambda x: self.model.predict(x)
        self.build()

    def build(self):
        #crea il modello
        model = Sequential()

        # crea i primi due strati uno con un una griglia l'altro la converte in un vettore
        model.add(Flatten(input_shape=(12,8,8), name='input_layer'))

        # inserisce i layer intermedi
        model.add(Dense(512, activation='relu', kernel_initializer=RandomNormal(stddev=0.01)))
        model.add(Dropout(0.6))
        model.add(Dense(1024, activation='relu', kernel_initializer=RandomNormal(stddev=0.01)))
        model.add(Dropout(0.6))
        model.add(Dense(2048, activation='relu', kernel_initializer=RandomNormal(stddev=0.01)))
        model.add(Dropout(0.6))
        model.add(Dense(4096, activation='relu', kernel_initializer=RandomNormal(stddev=0.01)))
        model.add(Dropout(0.6))
        model.add(Dense(2048, activation='relu', kernel_initializer=RandomNormal(stddev=0.01)))
        model.add(Dropout(0.6))
        model.add(Dense(1024, activation='relu', kernel_initializer=RandomNormal(stddev=0.01)))
        model.add(Dropout(0.6))
        model.add(Dense(512, activation='relu', kernel_initializer=RandomNormal(stddev=0.01)))
        model.add(Dropout(0.6))

        # imposta l'ultimo layer per ritornare un numero decimale relativo
        model.add(Dense(1, activation='linear', name='output_layer'))
        
        # compila e salva il modello
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        self.model = model
        
        return self.model


    def convertBoard(self, position):
        position = [position.replace(" ", "").replace("\n", "")[i * 8 : (i + 1) * 8] for i in range(8)]
        conversion = [9820, 9822, 9821, 9819, 9818, 9823, 9817, 9814, 9816, 9815, 9813, 9812, 11096]
            
        encodedMat = []
        for row in position: encodedMat.append([conversion.index(ord(i)) for i in row])

        m8x8 = [[0 for _ in range(8)] for _ in range(8)]
        altrores = [m8x8 for _ in range(12)]

        del conversion, position,  m8x8

        for index, piece in enumerate(altrores):
            m8x8 = [[0 for _ in range(8)] for _ in range(8)]
            for x in range(len(encodedMat)):
                for y in range(len(encodedMat)):
                    square = encodedMat[x][y]
                    if square == index: 
                        m8x8[x][y] = 1
            altrores[index] = m8x8

        return altrores

    def reward(self, data, rew):
        self.model.train_on_batch(data, array([rew]))

    @property
    def print(self):
        self.model.summary()

def scanMoves(Board, model):
    *moves, = board.generate_legal_moves()
    
    turn = 1 if Board.turn else -1
    best, foundMove = 1000*-turn, moves[0]
    for move in moves:
        # gioca la mossa selezionata
        Board.push_uci(move.xboard())
        
        evaluation = model.predict(array([model.convertBoard(Board.unicode())]))
        if (evaluation > best if turn == 1 else evaluation < best): 
            best, foundMove = evaluation, move
        
        # rimette la scacchiera a posto
        Board.pop()  
    return foundMove

def generatePrediction(positions, bar, engine, n):
    for index, pos in enumerate(positions): 
        prediction = engine.analyse(pos, chess.engine.Limit(time=2.0))['score'].relative.score()
        with lock:
            predictions[n*(samples//4)+index] = prediction if prediction else 0
            bar.update(1)
    del prediction


model = Model()
if input("hai gia eseguito questo script: ") == "si":
    model.model = load_model("model1.h5")

samples = int(input("samples: "))

boards = [chess.Board() for _ in range(samples)]
data = []
predictions = [ 0 for _ in range(samples)]

# genera data
for index, item in enumerate(tqdm(range(samples), desc=f"[ + ] Generating batch samples     ")):
    consideratedBoard = boards[index]
    for move in range(randint(0,25)): 
        *moves, = consideratedBoard.generate_legal_moves()
        if len(moves) == 0: break
        moves = moves[randint(0,len(moves)-1)]
        consideratedBoard.push_uci(moves.xboard())
    data.append(model.convertBoard(consideratedBoard.unicode()))



with tqdm(total = samples, desc=f"[ + ] Getting stockfish predictions") as bar:
    lock = Lock()
    threads = []
    length = len(boards)//4
    for i in range(3):
        thread = Thread( target = generatePrediction, args=( boards[i*length:(i+1)*length:], bar, chess.engine.SimpleEngine.popen_uci(stockfish), i))
        threads.append(thread)
    threads.append(Thread(target = generatePrediction, args=( boards[3*length::], bar, chess.engine.SimpleEngine.popen_uci(stockfish), 3)))
    for i in threads: i.start()
    for i in threads: i.join()

#for index, item in enumerate(): predictions.append(stockfish.analyse(boards[index], chess.engine.Limit(time=2.0))['score'].relative.score())


print("Training model...")
print(array(data), array(predictions))
model.model.fit(array(data), array(predictions), epochs=17)

model.model.save("model1.h5")
print(model.model.summary())
print("done")
exit()