#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 16:29:30 2021

@author: brianahaneku
"""
import random
import ChessEngine

pieceValues={'K':0,'p':1,'N':3,'B':3,'R':5,'Q':9}
CHECKMATE=1000
STALEMATE=0
PAWNDECAY=0.85
PASSEDPAWNBENEFIT=1
DIFFCONTROLLEDSQUARESBENEFIT=1/85



def getRandomMove(validMoves):
    return validMoves[random.randint(0,len(validMoves)-1)]

def getBestMoveGreedy(gs,validMoves):
    
    turn= 1 if gs.whiteToMove else -1
    maxScore=-CHECKMATE
    bestMove=None
    
    for move in validMoves:
        
        gs.makeMove(move)
        score=turn*scorePosition(gs.board,validMoves)
        
        if gs.checkMate:
            score=CHECKMATE
        elif gs.staleMate:
            score=STALEMATE
            
        if score>maxScore:
            maxScore=score
            bestMove=move
            
        gs.undoMove()
    
    return bestMove

def getBestMoveMiniMax(gs,validMoves):
    
    turn = 1 if gs.whiteToMove else -1
    maxScore=CHECKMATE
    bestMove=None
    bestOppMove=None
    bestMoves=[]
    
    for move in validMoves:
        
        gs.makeMove(move)
        opponentMoves=gs.generateValidMoves()
        
        if gs.checkMate:
            gs.undoMove()
            return move
        
        elif gs.staleMate:
            maxScoreOpp=0
        else:
            maxScoreOpp=-CHECKMATE
        
        for oppMove in opponentMoves:
            
            gs.makeMove(oppMove)
            gs.generateValidMoves()
            
            if gs.checkMate:
                score=CHECKMATE
                maxScoreOpp=CHECKMATE
                bestOppMove=oppMove
                gs.undoMove()
                
                
                break
            
            elif gs.staleMate:
                score=STALEMATE
                
            
            else:
                score=(-turn)*scorePosition(gs.board,validMoves)
                
            if maxScoreOpp<score:
                maxScoreOpp=score
                bestOppMove=oppMove
            gs.undoMove()
                
        if maxScoreOpp<maxScore:
            maxScore=maxScoreOpp
            bestMove=move
            bestMoves=[move]
        elif maxScoreOpp==maxScore:
            bestMoves.append(move)
            
        
                
        gs.undoMove()
        
    #if bestMove is None:
        #return getRandomMove(validMoves)
    
    return getRandomMove(bestMoves)


def alphaBetaMax(gs,alpha, beta, depthleft):
    if depthleft == 0:
        return scorePosition(gs.board,gs.generateValidMoves()),None
    bestMove=None
    for move in gs.generateValidMoves():
        gs.makeMove(move)
        score,x=alphaBetaMin(gs,alpha,beta,depthleft-1)
        gs.undoMove()
        if score>=beta:
            return beta,bestMove
        if score>alpha:
            alpha=score
            bestMove=move
    return alpha,bestMove

def alphaBetaMin(gs,alpha, beta, depthleft):
    if depthleft == 0:
        return -scorePosition(gs.board,gs.generateValidMoves()),None
    bestMove=None
    for move in gs.generateValidMoves():
        gs.makeMove(move)
        score,x=alphaBetaMax(gs,alpha,beta,depthleft-1)
        gs.undoMove()
        if score<=alpha:
            return alpha,bestMove
        if score<beta:
            beta=score
            bestMove=move
    return beta,bestMove

def scorePosition(board,validMoves):
    #This function only takes into account the difference in material of both players
    score=0
    
    whitePawnsInColumn={c:0 for c in range(len(board[0]))}
    blackPawnsInColumn={c:0 for c in range(len(board[0]))}

    #Adding the sum of the values of the white pieces minus that of the black pieces not including pawns
    #which will be handled seperately.
    for r in range(len(board)):
        for c in range(len(board[0])):
            piece=board[r][c]

            if piece[0]=='w':
                if piece[1]=='p':
                    whitePawnsInColumn[c]+=1
                else:
                    score+=pieceValues[piece[1]]

            elif piece[0]=='b':
                if piece[1]=='p':
                    blackPawnsInColumn[c]+=1
                else:
                    score-=pieceValues[piece[1]]
    
    #Assign score of pawns based on whether they are doubled, tripled, etc and if they are passed pawns or not
    #where passed pawn means there are no enemy pawns in front of it or to the right of it
    for c in range(len(board[0])):
        numOfWhitePawns=whitePawnsInColumn[c]
        score+=(PAWNDECAY**(numOfWhitePawns)-1)/(PAWNDECAY-1)
        numOfBlackPawns=blackPawnsInColumn[c]
        score-=(PAWNDECAY**(numOfBlackPawns)-1)/(PAWNDECAY-1)

        if numOfWhitePawns>0 and numOfBlackPawns==0:
            isPassedPawn=True
            for neighborCol in (c-1,c+1):
                if 0<=neighborCol<len(board[0]) and blackPawnsInColumn[neighborCol]>0:
                    isPassedPawn=False
                    break
            if isPassedPawn:
                score+=PASSEDPAWNBENEFIT
        
        if numOfBlackPawns>0 and numOfWhitePawns==0:
            isPassedPawn=True
            for neighborCol in (c-1,c+1):
                if 0<=neighborCol<len(board[0]) and whitePawnsInColumn[neighborCol]>0:
                    isPassedPawn=False
                    break
            if isPassedPawn:
                score-=PASSEDPAWNBENEFIT
    

    differenceOfSquaresControlled=0

    #Finding out which player controls more squares on the board and assigning a benefit scaled by the difference
    for move in validMoves:
        color=board[move.startRow][move.startCol][0]
        if color=='w':
            differenceOfSquaresControlled+=1
        else:
            differenceOfSquaresControlled-=1
    
    score+=differenceOfSquaresControlled*DIFFCONTROLLEDSQUARESBENEFIT

    return score
    
