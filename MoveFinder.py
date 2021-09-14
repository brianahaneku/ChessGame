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



def getRandomMove(validMoves):
    return validMoves[random.randint(0,len(validMoves)-1)]

def getBestMoveGreedy(gs,validMoves):
    
    turn= 1 if gs.whiteToMove else -1
    maxScore=-CHECKMATE
    bestMove=None
    
    for move in validMoves:
        
        gs.makeMove(move)
        score=turn*scorePosition(gs.board)
        
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
                score=(-turn)*scorePosition(gs.board)
                
            if maxScoreOpp<score:
                maxScoreOpp=score
                bestOppMove=oppMove
            gs.undoMove()
                
        if maxScoreOpp<maxScore:
            maxScore=maxScoreOpp
            bestMove=move
            
        
                
        gs.undoMove()
        
    if bestMove is None:
        return getRandomMove(validMoves)
    
    return bestMove
        
        
        

def scorePosition(board):
    #This function only takes into account the difference in material of both players
    score=0
    for r in range(len(board)):
        for c in range(len(board[0])):
            piece=board[r][c]
            if piece[0]=='w':
                score+=pieceValues[piece[1]]
            elif piece[0]=='b':
                score-=pieceValues[piece[1]]
    
    return score
    