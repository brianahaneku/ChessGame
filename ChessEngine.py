"""


@author: brianahaneku

where we store all info about current state of chess game.
Also determines valid moves at current state.
Also keeps a move log
"""


class GameState():
    #consider a list of gamestates
    def __init__(self):
        # board is 8by8 2d list, each element is represented by 2 characters where
        # first represents color and the second the kind of piece
        # the dashes represent empty space
        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"]
            , ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
                      ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
                      ]
        self.checkMate=False
        self.staleMate=False
        self.whiteToMove = True
        self.moveLog = []
        self.moveLog_obj=[]
        self.whiteKingLoc=(7,4)
        self.blackKingLoc=(0,4)
        self.inCheck=False #Checks for if current player is in check
        self.pins=[]
        self.checks=[]
        self.enpassantPossible=()#square where an enpassant capture is possible
        self.enpassantPossibleLog=[self.enpassantPossible]
        self.currentCastlingRight=CastleRights(True,True,True,True)
        self.castleRightsLog=[CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
                                           self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)]

    def makeMove(self,move):
        self.board[move.endRow][move.endCol]=move.pieceMoved
        self.board[move.startRow][move.startCol]="--"
        self.moveLog_obj.append(move)
        self.moveLog.append(move.pieceMoved[1:]+move.getChessNotation())#log the move
        self.whiteToMove=not self.whiteToMove
        if move.pieceMoved=='wK':
            self.whiteKingLoc=(move.endRow,move.endCol)
        elif move.pieceMoved=='bK':
            self.blackKingLoc=(move.endRow,move.endCol)
        
        
        
        #Updating enpassantPossible
        if move.pieceMoved[1]=='p' and abs(move.startRow-move.endRow)==2:
            self.enpassantPossible=((move.startRow+move.endRow)//2,move.endCol)#enpassant square
            #is the square in between the start square and end square of pawn that moved up or down two
        else:
            self.enpassantPossible=()
        
        #enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol]='--'
        
        #pawn promotion
        if move.isPawnPromotion:
            promotedPiece='Q'
            #promotedPiece=input("Promote to Q,R,B, or N")
            self.board[move.endRow][move.endCol]=move.pieceMoved[0]+promotedPiece
        
        
        
        #castle Move
        
        if move.isCastleMove:
            if move.endCol-move.startCol==2:# Kingside castle
                self.board[move.endRow][move.endCol-1]=self.board[move.endRow][move.endCol+1]#move the rook
                self.board[move.endRow][move.endCol+1]='--'
            else:#Queenside castle
                self.board[move.endRow][move.endCol+1]=self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2]='--'
        
        self.enpassantPossibleLog.append(self.enpassantPossible)
        
        #updating castling rights - when rook or king has moved
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
                                           self.currentCastlingRight.wqs,self.currentCastlingRight.bqs))
        
        
        
            

    def undoMove(self):
        lastMove = self.moveLog_obj[-1]
        self.board[lastMove.endRow][lastMove.endCol] = lastMove.pieceCaptured
        self.board[lastMove.startRow][lastMove.startCol] = lastMove.pieceMoved
        del (self.moveLog_obj[-1])
        del (self.moveLog[-1])
        self.whiteToMove=not self.whiteToMove
        if lastMove.pieceMoved=='wK':
            self.whiteKingLoc=(lastMove.startRow,lastMove.startCol)
        if lastMove.pieceMoved=='bK':
            self.blackKingLoc=(lastMove.startRow,lastMove.startCol)
        
        #Need to add back "captured piece" on enpassant move
        if lastMove.isEnpassantMove:
            enemyPiece='wp' if lastMove.pieceMoved=='bp' else 'bp'
            self.board[lastMove.startRow][lastMove.endCol]=enemyPiece
        
        self.enpassantPossibleLog.pop()
        self.enpassantPossible=self.enpassantPossibleLog[-1]
        
        
        
        
        
        #Undoing castling rights
        self.castleRightsLog.pop()
        castleRights=self.castleRightsLog[-1]
        self.currentCastlingRight=CastleRights(castleRights.wks,castleRights.bks,castleRights.wqs,castleRights.bqs)
        
        #Undoing castle move
        if lastMove.isCastleMove:
            if lastMove.endCol-lastMove.startCol==2: #kingside
                self.board[lastMove.endRow][lastMove.endCol+1]=self.board[lastMove.endRow][lastMove.endCol-1]
                self.board[lastMove.endRow][lastMove.endCol-1]='--'
            else:
                self.board[lastMove.endRow][lastMove.endCol-2]=self.board[lastMove.endRow][lastMove.endCol+1]
                self.board[lastMove.endRow][lastMove.endCol+1]='--'
        
        self.checkMate=False
        self.staleMate=False
                
    
    def updateCastleRights(self,move):
        if move.pieceMoved=='wK':
            self.currentCastlingRight.wks=False
            self.currentCastlingRight.wqs=False
        elif move.pieceMoved=='bK':
            self.currentCastlingRight.bks=False
            self.currentCastlingRight.bqs=False
        elif move.pieceMoved=='wR':
            if move.startRow==7:
                if move.startCol==0:#left rook
                    self.currentCastlingRight.wqs=False
                elif move.startCol==7:#right rook
                    self.currentCastlingRight.wks=False
        elif move.pieceCaptured=='wR':
            if move.endRow==7:
                if move.endCol==0:#left rook
                    self.currentCastlingRight.wqs=False
                elif move.endCol==7:#right rook
                    self.currentCastlingRight.wks=False
        elif move.pieceMoved=='bR':
            if move.startRow==0:
                if move.startCol==0:
                    self.currentCastlingRight.bqs=False
                elif move.startCol==7:
                    self.currentCastlingRight.bks=False
        elif move.pieceCaptured=='bR':
            if move.endRow==0:
                if move.endCol==0:
                    self.currentCastlingRight.bqs=False
                elif move.endCol==7:
                    self.currentCastlingRight.bks=False

    def generateValidMoves(self):
        moves=[]
        self.inCheck,self.pins,self.checks=self.checkForPinsAndChecks()
        
        if self.whiteToMove:
            kingRow=self.whiteKingLoc[0]
            kingCol=self.whiteKingLoc[1]
        else:
            kingRow=self.blackKingLoc[0]
            kingCol=self.blackKingLoc[1]
        
        if self.inCheck:
            if len(self.checks)==1:#I can block the check or move the king
                moves=self.generateAllMoves()
                check=self.checks[0]
                checkRow=check[0]
                checkCol=check[1]
                pieceChecking=self.board[checkRow][checkCol] #Piece causing the check
                validSquares=[] #Squares that pieces can move to, if the piece checking is a knight it must be 
                #captured or the king must move
                if pieceChecking[1]=='N':
                    validSquares=[(checkRow,checkCol)]
                else:
                    for k in range(1,8):
                        validSquare=(kingRow+check[2]*k,kingCol+check[3]*k)#check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0]==checkRow and validSquare[1]==checkCol:#We have reached the checking piece
                            break
                
                for i in range(len(moves)-1,-1,-1):
                    if moves[i].pieceMoved[1]!='K':
                        if not (moves[i].endRow,moves[i].endCol) in validSquares:#Move doesnt block check or capture piece
                            moves.remove(moves[i])
            else:#Double check
                if self.whiteToMove:
                    self.getKingMoves(kingRow,kingCol, moves,'w')
                else:
                    self.getKingMoves(kingRow,kingCol, moves,'b')
        
        else:
            moves= self.generateAllMoves()
        
        #Checking for checkmate or stalemate
        if len(moves)==0:
            if self.inCheck:
                self.checkMate=True
                self.staleMate=False
            else:
                self.staleMate=True
                self.checkMate=False
        else:
        
            self.checkMate=False
            self.staleMate=False
        
        return moves



    def generateAllMoves(self):
        moves=[]
        for r in range(8):
            for c in range(8):
                if self.board[r][c]=='--':
                    continue
                color=self.board[r][c][0]
                piece=self.board[r][c][1]
                if (self.whiteToMove and color=="w") or (not self.whiteToMove and color=="b"):
                    if piece=="p":
                        self.getPawnMoves(r,c,moves,color)
                    elif piece=="B":
                        self.getBishopMoves(r,c,moves,color)
                    elif piece=="K":
                        self.getKingMoves(r,c,moves,color)
                    elif piece=="N":
                        self.getKnightMoves(r,c,moves,color)
                    elif piece=="Q":
                        self.getQueenMoves(r,c,moves,color)
                    elif piece=="R":
                        self.getRookMoves(r,c,moves,color)


        return moves
    
    def squareUnderAttack(self,r,c):
        knightMoves=((-2,-1),(-2,1),(-1,-2),(-1,2),(2,-1),(2,1),(1,-2),(1,2))
        startRow=r
        startCol=c
        
        if self.whiteToMove:
            allyColor='w'
            enemyColor='b'
            
        else:
            allyColor='b'
            enemyColor='w'
            
        
            
        for m in knightMoves:
            endRow=startRow+m[0]
            endCol=startCol+m[1]
            if 0<=endRow<8 and 0<=endCol<8:
                piece=self.board[endRow][endCol]
                if piece==enemyColor+'N':
                    return True
        
        directions=((1,0),(-1,0),(0,1),(0,-1),(-1,-1),(-1,1),(1,-1),(1,1))
        
        for j in range(len(directions)):
            for i in range(1,8):
                endRow=startRow+directions[j][0]*i
                endCol=startCol+directions[j][1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    piece=self.board[endRow][endCol]
                    if piece[0]==enemyColor:
                        if 0<=j<=3 and (piece[1]=='R' or piece[1]=='Q' or (piece[1]=='K' and i==1)):
                            return True
                        elif j>3 and ((i==1 and enemyColor=='w' and 6<=j<=7) or (i==1 and enemyColor=='b' and 4<=j<=5) or 
                                      piece[1]=='B' or piece[1]=='Q' or (piece[1]=='K' and i==1)):
                            return True
                        break
                    elif piece[0]==allyColor:
                        break
                else:
                    break
        return False
                
                        
                

    def getPawnMoves(self,r,c,moves,color):
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
            
        if self.whiteToMove:#white pawn moves
            if self.board[r-1][c]=='--':#1 square move up and 2 square move
                if not piecePinned or pinDirection==(-1,0):
                    moves.append(Move((r,c),(r-1,c),self.board))
                    if r==6 and self.board[r-2][c]=='--':
                        moves.append(Move((r,c),(r-2,c),self.board))
            
            #captures
            if c-1>=0:
                if not piecePinned or pinDirection==(-1,-1):
                    if self.board[r-1][c-1][0]=='b': 
                        moves.append(Move((r,c),(r-1,c-1),self.board))
                    elif (r-1,c-1)==self.enpassantPossible:
                        moves.append(Move((r,c),(r-1,c-1),self.board,True))
            
            if c+1<=7:
                if not piecePinned or pinDirection==(-1,1):
                    if self.board[r-1][c+1][0]=='b':
                        moves.append(Move((r,c),(r-1,c+1),self.board))
                    elif (r-1,c+1)==self.enpassantPossible:
                        moves.append(Move((r,c),(r-1,c+1),self.board,True))
        else:#black pawn moves
            if self.board[r+1][c]=='--':
                if not piecePinned or pinDirection==(1,0):
                    moves.append(Move((r,c),(r+1,c),self.board))
                    if r==1 and self.board[r+2][c]=='--':
                        moves.append(Move((r,c),(r+2,c),self.board))
                        
            
            #captures
            if c-1>=0:
                if self.board[r+1][c-1][0]=='w':
                    if not piecePinned or pinDirection==(1,-1):
                        moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1)==self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c-1),self.board,True))
            
            if c+1<=7:
                if self.board[r+1][c+1][0]=='w':
                    if not piecePinned or pinDirection==(1,1):
                        moves.append(Move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1)==self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c+1),self.board,True))
            

    def getBishopMoves(self,r,c,moves,color):
        
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        directions=((-1,-1),(-1,1),(1,-1),(1,1))
        enemyColor='b' if self.whiteToMove else 'w'
        
        for d in directions:
            for i in range(1,8):
                endRow=r+d[0]*i
                endCol=c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    if not piecePinned or pinDirection==d or pinDirection==(-d[0],-d[1]):
                        endPiece=self.board[endRow][endCol]
                        if endPiece=='--':
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                        elif endPiece[0]==enemyColor:
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break


    def getKingMoves(self,r,c,moves,color):
        rowMoves=(-1,-1,-1,0,0,1,1,1)
        colMoves=(-1,0,1,-1,1,-1,0,1)
        allyColor='w' if self.whiteToMove else 'b'
        
        for i in range(8):
            endRow=r+rowMoves[i]
            endCol=c+colMoves[i]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]!=allyColor:
                    #Place king on end square and see if its in check
                    if allyColor=='w':
                        self.whiteKingLoc=(endRow,endCol)
                    else:
                        self.blackKingLoc=(endRow,endCol)
                    inCheck,pins,checks=self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    
                    #Place king back at original location
                    if allyColor=='w':
                        self.whiteKingLoc=(r,c)
                    else:
                        self.blackKingLoc=(r,c)
        self.getCastleMoves(r,c,moves,allyColor)
        
    def getCastleMoves(self,r,c,moves,allyColor):
        if self.inCheck:
            return #Can't castle when in check
        
        if self.whiteToMove:
            if self.currentCastlingRight.wks:
                self.getKingsideCastleMoves(r, c, moves, allyColor)
                
            if self.currentCastlingRight.wqs:
                self.getQueensideCastleMoves(r, c, moves, allyColor)
                
        else:
            if self.currentCastlingRight.bks:
                self.getKingsideCastleMoves(r, c, moves, allyColor)
                
            if self.currentCastlingRight.bqs:
                self.getQueensideCastleMoves(r, c, moves, allyColor)
        
        
    
    def getKingsideCastleMoves(self,r,c,moves,allyColor):
        if self.board[r][c+1]=='--' and self.board[r][c+2]=='--':
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,False,True))
    
    def getQueensideCastleMoves(self,r,c,moves,allyColor):
        if self.board[r][c-1]=='--' and self.board[r][c-2]=='--' and self.board[r][c-3]=='--':
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board,False,True))
    

    def getKnightMoves(self,r,c,moves,color):
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])#Not actually neccessary
                self.pins.remove(self.pins[i])
                break
        
        knightMoves=((-2,-1),(-2,1),(-1,-2),(-1,2),(2,-1),(2,1),(1,-2),(1,2))
        allyColor='w' if self.whiteToMove else 'b'
        
        for m in knightMoves:
            endRow=r+m[0]
            endCol=c+m[1]
            if 0<=endRow<8 and 0<=endCol<8:
                if not piecePinned:
                    endPiece=self.board[endRow][endCol]
                    if endPiece[0]!=allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
        

    def getQueenMoves(self,r,c,moves,color):
        self.getRookMoves(r,c,moves,color)
        self.getBishopMoves(r,c,moves,color)

    def getRookMoves(self,r,c,moves,color):
        
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                
                if self.board[r][c][1]!='Q': #can't remove queen from pin on rook moves,only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break
        
        directions=((-1,0),(0,-1),(1,0),(0,1))
        enemyColor='b' if self.whiteToMove else 'w'
        
        for d in directions:
            for i in range(1,8):
                endRow=r+d[0]*i
                endCol=c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    if not piecePinned or pinDirection==d or pinDirection==(-d[0],-d[1]):
                        endPiece=self.board[endRow][endCol]
                        if endPiece=='--':
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0]==enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: #friendly piece reached
                            break
                else: #off the board
                    break
        
    
    def checkForPinsAndChecks(self):
        pins=[]#location of pinned piece and direction it is pinned
        checks=[]#
        inCheck=False
        
        if self.whiteToMove:
            enemyColor='b'
            allyColor='w'
            startRow=self.whiteKingLoc[0]
            startCol=self.whiteKingLoc[1]
        else:
            enemyColor='w'
            allyColor='b'
            startRow=self.blackKingLoc[0]
            startCol=self.blackKingLoc[1]
        
        #Check outward from king in all directions
        directions=[(-1,0),(0,1),(1,0),(0,-1),(-1,-1),(-1,1),(1,1),(1,-1)]
        
        for i in range(len(directions)):
            d=directions[i]
            potentialPin=()
            for k in range(1,8):
                endRow=startRow+d[0]*k
                endCol=startCol+d[1]*k
                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece=self.board[endRow][endCol]
                    if endPiece[0]==allyColor and endPiece[1]!='K':#Neccessary because when we call getKingMoves
                    #we don't actually move the king so we kind've have a phantom king 
                        if potentialPin==():#First allied piece found
                            potentialPin=(endRow,endCol,d[0],d[1])
                        else:
                            break #Second allied piece found so no pin
                    elif endPiece[0]==enemyColor:
                        attacker=endPiece[1]
                        #Cases
                        #1. Vertically or horizontally away and attacker is rook
                        #2.Diagonally away and attacker is bishop
                        #3. One square away and diagonal and piece is pawn
                        #4. Any direction and attacker is queen
                        #5. Any direction one square away and piece is a king(prevents a king move
                        #to a square controlled by another king)
                        
                        if (0<=i<=3 and attacker=='R') or \
                            (4<=i<=7 and attacker=='B') or \
                                (k==1 and attacker=='p' and ((enemyColor=='w' and 6<=i<=7) or (enemyColor=='b' and 4<=i<=5))) or \
                                    (attacker=='Q') or (k==1 and attacker=='K'):
                                        if potentialPin==():#No piece blocking attacker
                                            inCheck=True
                                            checks.append((endRow,endCol,d[0],d[1]))
                                            break
                                        else:#Piece is blocking so there is a pin
                                            pins.append(potentialPin)
                                            break
                        else:#Enemy piece is not applying a check
                            break
                else:
                    break #we moved off the board
        
        knightMoves=((-2,-1),(-1,-2),(-2,1),(-1,2),(2,-1),(1,-2),(2,1),(1,2))
        
        for move in knightMoves:
            endRow=startRow+move[0]
            endCol=startCol+move[1]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]==enemyColor and endPiece[1]=='N':#Enemy knight attacking king
                    inCheck=True
                    checks.append((endRow,endCol,move[0],move[1]))
        return inCheck,pins,checks

class CastleRights:
    def __init__(self,wks,bks,wqs,bqs):
        self.wks=wqs
        self.bks=bks
        self.wqs=wqs
        self.bqs=bqs
    
                
class Move():

    ranksToRows={"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    rowsToRanks={v:k for k,v in ranksToRows.items()}
    filesToCols={"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    colsToFiles={v:k for k,v in filesToCols.items()}
    def __init__(self,startSq,endSq,board,isEnpassantMove=False,isCastleMove=False):
        self.startRow=startSq[0]
        self.startCol=startSq[1]
        self.endRow=endSq[0]
        self.endCol=endSq[1]
        self.pieceMoved=board[self.startRow][self.startCol]
        self.pieceCaptured=board[self.endRow][self.endCol]
        
        #pawn promotion
        self.isPawnPromotion=False
        self.promotionChoice=['Q,N,B,R']
        if (self.pieceMoved=='wp' and self.endRow==0) or (self.pieceMoved=='bp' and self.endRow==7):
            self.isPawnPromotion=True
        
        #enpassant
        self.isEnpassantMove=isEnpassantMove
        
        #castling
        self.isCastleMove=isCastleMove
        
        
        
        

    def getChessNotation(self):
        return self.getRankFile(self.startRow,self.startCol)+ self.getRankFile(self.endRow,self.endCol)

    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    def __eq__(self, o):
        return (self.startRow==o.startRow and self.startCol==o.startCol and 
        self.endRow==o.endRow and self.endCol==o.endCol)
    
    