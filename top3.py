import chess
from numpy import array
from numpy import e

board = chess.Board()

# knobs

BISHOP_VALUE = 4
KNIGHT_VALUE = 3
QUEEN_VALUE = 10
PAWN_VALUE = .5
ROOK_VALUE = 5

PIN_PENALITY = .2
ATTACK_MULTIPLIER = QUEEN_VALUE/5
FIELD_SCALAR = .1

#####################################################################################
###################################### Fields #######################################
#####################################################################################

bishopsField = (
 (1.12,1.16,1.22,1.24,1.24,1.22,1.16,1.12),# 8
 (1.16,1.22,1.31,1.4 ,1.4 ,1.31,1.22,1.16),# 7
 (1.22,1.31,1.1 ,1.8 ,1.8 ,1.1 ,1.31,1.22),# 6
 (1.24,1.8 ,1.8 ,2.  ,2.  ,1.8 ,1.8 ,1.24),# 5
 (1.24,1.8 ,1.8 ,2.  ,2.  ,1.8 ,1.8 ,1.24),# 4
 (1.22,1.31,1.1 ,1.8 ,1.8 ,1.1 ,1.31,1.22),# 3
 (1.16,1.22,1.31,1.4 ,1.4 ,1.31,1.22,1.16),# 2
 (1.12,1.16,1.22,1.24,1.24,1.22,1.16,1.12) # 1
)#  A    B    C    D    E    F    G    H

knightsField: tuple = (
 (1.12,1.16,1.22,1.24,1.24,1.22,1.16,1.12),# 8
 (1.16,1.22,1.31,1.4 ,1.4 ,1.31,1.22,1.16),# 7
 (1.  ,1.31,1.8 ,1.4 ,1.4 ,1.8 ,1.31,1.  ),# 6
 (1.24,1.40,1.4 ,1.8  ,1.8,1.4 ,1.4 ,1.24),# 5
 (1.24,1.40,1.4 ,1.8  ,1.8,1.4 ,1.4 ,1.24),# 4
 (1.  ,1.31,1.8 ,1.4 ,1.4 ,1.8 ,1.31,1.  ),# 3
 (1.16,1.22,1.31,1.4 ,1.4 ,1.31,1.22,1.16),# 2
 (1.12,1.16,1.22,1.24,1.24,1.22,1.16,1.12) # 1
)#  A    B    C    D    E    F    G    H

rooksField = (
 (1.12,1   ,1.22,1.8 ,1.8 ,1.8 ,.2  ,1.12),# 8
 (1.16,1.22,1.31,1.4 ,1.4 ,1.31,1.22,1.16),# 7
 (1.22,1.31,1.5 ,1.8 ,1.8 ,1.5 ,1.31,1.22),# 6
 (1.24,1.8 ,1.8 ,2.  ,2.  ,1.8 ,1.8 ,1.24),# 5
 (1.24,1.8 ,1.8 ,2.  ,2.  ,1.8 ,1.8 ,1.24),# 4
 (1.22,1.31,1.5 ,1.8 ,1.8 ,1.5 ,1.31,1.22),# 3
 (1.16,1.22,1.31,1.4 ,1.4 ,1.31,1.22,1.16),# 2
 (1.12,1   ,1.22,1.8 ,1.8 ,1.8 ,.1  ,1.12)#  1
)#  A    B    C    D    E    F    G    H

pawnsField = (
 (2   ,2   ,2   ,2   ,2   ,2   ,2   ,2   ),
 (1   ,1   ,1   ,1   ,1   ,1   ,1   ,1   ),
 (1.23,1.2 ,1.5 ,1.53,1.83,1.13,1.13,1.13),
 (1.22,1.2 ,1.5 ,1.52,2.82,1.12,1.12,1.12),
 (1.21,1.2 ,1.5 ,1.51,2.81,1.11,1.11,1.11),
 (1.2 ,1.2 ,1.5 ,1.5 ,1.8 ,1.1 ,1.1 ,1.1 ),
 (1   ,1   ,1   ,1   ,1   ,1   ,1   ,1   ),
 (2   ,2   ,2   ,2   ,2   ,2   ,2   ,2   )
)#   A    B    C    D    E    F    G    H

kingsFiels = (
       (1, 3, 1, 1, 1, 3, 1, 1), # 1
       (.1,.1,.1,.1,.1,.1,.1,.1), # 2
       (.1,.1,.1,.1,.1,.1,.1,.1), # 3 
       (.1,.1,.1,.1,.1,.1,.1,.1), # 4
       (.1,.1,.1,.1,.1,.1,.1,.1), # 5
       (.1,.1,.1,.1,.1,.1,.1,.1), # 6
       (.1,.1,.1,.1,.1,.1,.1,.1), # 7
       (1, 1, 3, 1, 1, 1, 3, 1), # 8
)#	 A  B  C  D  E  F  G  H


#####################################################################################
############################## Evaluation & Conversion ##############################
#####################################################################################

def getPos(pos):
    file_coordinate = chess.square_file(pos)
    rank_coordinate = chess.square_rank(pos)

    # Restituisci le coordinate come tuple
    return rank_coordinate, file_coordinate 

def getInvertedPos(row, col):
	return col+1 + (row-1)*8

def countAttackers(board, square, color):
	if square >= 64: square = 63
	elif square < 0: square = 0
	attackers_mask = board.attackers_mask(color, square-1)
	num_attackers = bin(attackers_mask).count('1')
	return num_attackers
def getKingMask(pos):
	row_p, col_p = getPos(pos)
	res = []
	for col in range(col_p-1, col_p+2):
		if col > 8 or col < 1: continue
		for row in range(row_p-1, row_p+2):
			if row > 8 or row < 1: continue 
			res.append(getInvertedPos(row, col))
	try: res.remove(pos)
	except: ValueError: ...
	return res


def evaluate(board, report = False):
	if report: return evalReport(board)
	evaluation = 0
	if board.is_checkmate(): return 10e6 * (-1 if board.turn  else 1)
	for turn in [False, True]:
		if turn: evaluation = -evaluation
		scalingFactor = FIELD_SCALAR
		
		# Cerca di trovare la possibilità di matto
		KingPos = list(board.pieces(chess.KING, not turn))[0]
		adiacenti = getKingMask(KingPos)
		attackers = 0
		for square in adiacenti: attackers += countAttackers(board, square, turn)
		evaluation += ATTACK_MULTIPLIER*attackers/len(adiacenti)
		
		# KNIGHTS
		for pos in board.pieces(chess.KNIGHT, turn):
			pos1 = getPos(pos)
			add = (knightsField[pos1[0]][pos1[1]]-1)**2 * FIELD_SCALAR + KNIGHT_VALUE
			if board.is_pinned(not turn, pos): add *= PIN_PENALITY
			evaluation += add

		# BISHOPS
		for pos in board.pieces(chess.BISHOP, turn):			
			pos1 = getPos(pos)
			add += (bishopsField[pos1[0]][pos1[1]]-1)**2 * scalingFactor + BISHOP_VALUE
			if board.is_pinned(not turn, pos): add *= PIN_PENALITY
			evaluation += add
		# QUEENS
		for pos in board.pieces(chess.QUEEN, turn): 
			pos1 = getPos(pos)
			evaluation += (bishopsField[pos1[0]][pos1[1]])**2 * scalingFactor + QUEEN_VALUE

              #ROOKS
		for pos in board.pieces(chess.ROOK, turn):  
			pos1 = getPos(pos)
			add += (rooksField[pos1[0]][pos1[1]]-1)**2 * scalingFactor + ROOK_VALUE
			if board.is_pinned(not turn, pos): add *= PIN_PENALITY
			evaluation += add
		# PAWNS
		for pos in board.pieces(chess.PAWN, turn):  
			pos1 = getPos(pos)
			evaluation += (pawnsField[pos1[0] if turn else 8-pos1[0]][pos1[1]]-1)**2 * scalingFactor + PAWN_VALUE
			if board.is_pinned(not turn, pos): add *= PIN_PENALITY
			evaluation += add
		# KINGS
		KingPos = list(board.pieces(chess.KING, turn))[0]
		KingPos = getPos(KingPos)
		evaluation += (kingsFiels[KingPos[0]][KingPos[1]]-1)**2 * scalingFactor
	print(evaluation)
	return evaluation

def evalReport(board):
	evaluation = 0
	report: dict = {}
	if board.is_checkmate(): return 10e6 * (-1 if board.turn  else 1)
	for turn in [False, True]:
		if turn: evaluation = -evaluation
		scalingFactor = FIELD_SCALAR
		
		# Cerca di trovare la possibilità di matto
		KingPos = list(board.pieces(chess.KING, not turn))[0]
		adiacenti = getKingMask(KingPos)
		attackers = 0
		for square in adiacenti: attackers += countAttackers(board, square, turn)
		report[f'mate% {turn}'] = ATTACK_MULTIPLIER*attackers/len(adiacenti)
		evaluation += report[f'mate% {turn}']
		
		# KNIGHTS
		for pos in board.pieces(chess.KNIGHT, turn):
			pos1 = getPos(pos)
			add = (knightsField[pos1[0]][pos1[1]]-1)**2 * FIELD_SCALAR + KNIGHT_VALUE
			if board.is_pinned(not turn, pos): add *= PIN_PENALITY	
			evaluation += add
		report[f'knight {turn}'] = add

		# BISHOPS
		for pos in board.pieces(chess.BISHOP, turn):			
			pos1 = getPos(pos)
			add += (bishopsField[pos1[0]][pos1[1]]-1)**2 * FIELD_SCALAR + BISHOP_VALUE
			if board.is_pinned(not turn, pos): add *= PIN_PENALITY
			evaluation += add
		report[f'bishop {turn}'] = add
		
		# QUEENS
		for pos in board.pieces(chess.QUEEN, turn): 
			pos1 = getPos(pos)
			add = (bishopsField[pos1[0]][pos1[1]])**2 * FIELD_SCALAR + QUEEN_VALUE
			evaluation += add
		report[f'queen {turn}'] = add

              #ROOKS
		for pos in board.pieces(chess.ROOK, turn):  
			pos1 = getPos(pos)
			add += (rooksField[pos1[0]][pos1[1]]-1)**2 * FIELD_SCALAR + ROOK_VALUE
			if board.is_pinned(not turn, pos): add *= PIN_PENALITY
			evaluation += add
		report[f'rook {turn}'] = add

		# PAWNS
		for pos in board.pieces(chess.PAWN, turn):  
			pos1 = getPos(pos)
			evaluation += (pawnsField[pos1[0] if turn else 8-pos1[0]][pos1[1]]-1)**2 * FIELD_SCALAR + PAWN_VALUE
			if board.is_pinned(not turn, pos): add *= PIN_PENALITY
			evaluation += add
		report[f'pawns {turn}'] = add

		# KINGS
		KingPos = list(board.pieces(chess.KING, turn))[0]
		KingPos = getPos(KingPos)
		add = (kingsFiels[KingPos[0]][KingPos[1]]-1)**2 * FIELD_SCALAR
		evaluation += add
		report[f'king {turn}'] = add

	return evaluation, report

#####################################################################################
###################################### Minimax ######################################
#####################################################################################

def cutBranch(board, best):
	if board.turn: return False
	if evaluate(board) > best*10e-5:
		return True 

def scanMoves(moves, depth, Board):
	turn =  1 if Board.turn else -1
	best, foundMove = 1000*-turn, moves[0]
	for move in moves:
		# se è scaccomatto ritorna la mossa che lo causa
		if Board.is_checkmate(): return move 
		
		# gioca la mossa selezionata
		Board.push_uci(move.xboard())

		if cutBranch(Board, best): 
			Board.pop()
			continue
		
		# gioca la mossa migliore dell'avversario
		if depth > 1: Board.push_uci(minimax(Board, depth-1).xboard())
		
		# valuta la posizione
		evaluation = evaluate(Board)	
		if (evaluation > best if turn == 1 else evaluation < best): 
			best, foundMove = evaluation, move
		
		# rimette la scacchiera a posto
		for _ in range(1+(depth > 1)): Board.pop()	
	
	return foundMove

def minimax(board, depth, useThreads = False):
	*legalMoves, = board.generate_legal_moves()
	return scanMoves(legalMoves, depth, board)

livello = 3
import os
while not board.is_checkmate():
	try:
		print(evalReport(board))
		try:board.push_san(input("input:   "))
		except Exception as e:
			print("Mossa non Valida")
			continue 
		os.system("clear")
		print(board.unicode().replace("⭘ ", "  "))
		move = minimax(board, livello)
		print(move)
		try: board.push_san(move.xboard())
		except Exception: input()
		os.system("clear")
		print(board.unicode().replace("⭘ ", "  "))
	except Exception: 
		print(list(board.move_stack))
		break