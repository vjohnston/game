from display import GameSpace

row1 = [0, 0, 0, 0, 0, 0, 0, 0]
row2 = [0, '1', 0, 0, 0, 0, 0, 0]
row3 = [0, 0, 0, 0, 'f', 0, 0, 0]
row4 = [0, 0, 0, 0, 0, 0, 'b', 0]
row5 = [0, 0, 0, 0, 0, 0, 0, 0]
row6 = [0, 0, 'b', 0, 0, 0, 0, 0]
row7 = [0, 0, 0, 0, 0, 0, 0, 0]
row8 = [0, 0, 0, 0, 0, 0, 0, 0]

board = [row1, row2, row3, row4, row5, row6, row7, row8]

gs = GameSpace()
gs.updateBoard(board)
gs.main()

