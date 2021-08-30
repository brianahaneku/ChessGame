"""


@author: brianahaneku

Main file is responsible for handling user input and displaying current game state object
"""

import time
import random
import pygame as p
import ChessEngine
import MoveFinder

p.init()
WIDTH=HEIGHT=512 #400 is another option
DIMENSION=8 #dimension of chess board is 8 by 8
SQ_SIZE=HEIGHT//DIMENSION
MAX_FPS=15 #For animations later on
IMAGES={}
colors = [p.Color("white"),p.Color("Grey")]

"""
Initialize a global dictionary of images. Called once in the main
"""

def loadImages():
    pieces=["wp","wN","wR","wB","wK","wQ","bp","bR","bN","bB","bK","bQ"]
    for piece in pieces:
        IMAGES[piece]=p.transform.scale(p.image.load("images/" + piece+".png"),(SQ_SIZE,SQ_SIZE))
        #we can now access an image by using the dictionary IMAGES


"""Main driver for code. Handles user input and updating graphics
"""

def main():
    p.init()
    screen=p.display.set_mode((WIDTH,HEIGHT))
    clock=p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    loadImages() #Only do this once before while loop
    running=True
    sqSelected=()#no square is selected initially
    playerClicks = []#keeps track of player clicks (two tuples: [(6,4),(4,4)])
    valid_moves=gs.generateValidMoves()
    for move in valid_moves:
        print(move.getChessNotation())
    
    
    
    moveMade=False
    animate=False #Flag variable for when we should animate a move
    player1=True #True if human is playing white and false if computer is playing
    player2=True #Same as above for black
    gameOver=False
    humanTurn=(gs.whiteToMove and player1) or (not gs.whiteToMove and player2)
        
    while running:
        
        
        
        
        for e in p.event.get():
            if e.type==p.QUIT:
                running=False
            elif e.type==p.MOUSEBUTTONDOWN:
                if humanTurn and not gameOver:
                    location=p.mouse.get_pos() #(x,y) location of mouse
                    col=location[0]//SQ_SIZE
                    row=location[1]//SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected=()#deselect
                        playerClicks=[]#clear player clicks
                    else:
                        sqSelected=(row,col)
                        playerClicks.append(sqSelected)
                        
                    if len(playerClicks)==2: #after 2nd click
                        move=ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                        for i in range(len(valid_moves)):
                            if move==valid_moves[i]:
                                gs.makeMove(valid_moves[i])
                                valid_moves=gs.generateValidMoves()
                                moveMade=True
                                animate=True
                                sqSelected=()
                                playerClicks=[]
                                
                                break
                            
                           
                        if not moveMade:
                            playerClicks=[sqSelected]
                    
            elif e.type==p.KEYDOWN:
                if e.key==p.K_u and len(gs.moveLog)>0:
                    gs.undoMove()
                    
                    sqSelected=()#deselect
                    playerClicks=[]#clear player clicks
                    valid_moves=gs.generateValidMoves()
                    animate=False
                    
                    
                elif e.key==p.K_r: #Resets the board when r is pressed
                    print(gs.moveLog)
                    gs=ChessEngine.GameState()
                    player1=True
                    player2=True
                    
                    valid_moves=gs.generateValidMoves()
                    sqSelected=()
                    playerClicks=[]
                    moveMade=False
                    animate=False
                    gameOver=False
                    
            
            #AI MoveFinder
            if not gameOver and not humanTurn:
                AIMove=MoveFinder.getRandomMove(valid_moves)
                for i in range(len(valid_moves)):
                    if AIMove==valid_moves[i]:
                        gs.makeMove(valid_moves[i])
                        moveMade=True
                        valid_moves=gs.generateValidMoves()
                        animate=True
                        
                        break
                        
            
            
        if moveMade:
            if animate:
                animateMove(gs.moveLog_obj[-1],screen,gs.board,clock)
            humanTurn=(gs.whiteToMove and player1) or (not gs.whiteToMove and player2)
            #valid_moves=gs.generateValidMoves()
            
                
                
            
            moveMade=False
            animate=False

        drawGameState(screen,gs,valid_moves,sqSelected)
        
        if gs.checkMate:
            
            if gs.whiteToMove:
                drawText(screen,'Black wins by checkmate')
            else:
                drawText(screen,'White wins by checkmate')
            gameOver=True
            
        if gs.staleMate:
            drawText(screen,'Stalemate')
            gameOver=True
            
        
        clock.tick(MAX_FPS)
        p.display.flip()
        
"""Highlight square selected and moves for the selected piece"""
def highlightSquares(screen,gs,validMoves,sqSelected):
    if sqSelected:
        r,c=sqSelected
        if gs.board[r][c][0]==('w' if gs.whiteToMove else 'b'):#sqSelected is of correct color
            s=p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(125)#Transparency value
            s.fill(p.Color('blue'))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            
            #Highlight moves from the piece on the square
            s.fill(p.Color('green'))
            for move in validMoves:
                if move.startRow==r and move.startCol==c:
                    screen.blit(s,(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE))


"""Responsible for graphics in game state"""
def drawGameState(screen,gs,validMoves,sqSelected):
    drawBoard(screen)
    highlightSquares(screen,gs,validMoves,sqSelected)
    drawPieces(screen,gs.board)


def drawBoard(screen):
    
    
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color=colors[(r+c)%2]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE)) #c refers to elements in a row when traversing board



def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            
            piece=board[r][c]
            if piece!="--":
                screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def animateMove(move,screen,board,clock):
    #Fix enpassant animation
    
    dR=move.endRow-move.startRow
    dC=move.endCol-move.startCol
    framesPerSquare=10 #frames to move one square
    frameCount=(abs(dR)+abs(dC))*framesPerSquare
    
    for frame in range(frameCount+1):
        r,c=((move.startRow+dR*frame/frameCount,move.startCol+dC*frame/frameCount))
    
        drawBoard(screen)
        drawPieces(screen,board)
        color=colors[(move.endRow+move.endCol)%2]
        endSquare=p.Rect(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen,color,endSquare)
        
        #draw captured piece onto rectangle
        if move.pieceCaptured!='--':
            screen.blit(IMAGES[move.pieceCaptured],endSquare)
        
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen,text):
    font=p.font.SysFont('Helvitca',32,True,False)
    textObject=font.render(text,0,p.Color('Gray'))
    textLocation=p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH//2-textObject.get_width()//2,HEIGHT//2-textObject.get_height()//2)
    screen.blit(textObject,textLocation)
    textObject=font.render(text,0,p.Color('Black'))
    screen.blit(textObject,textLocation.move(2,2))

if __name__== "__main__":
    main()