import helpers as h

# Ask user for length and width of board
BoardHeight = h._input("Input the height of the board (must be an integer): ", int)
BoardWidth = h._input("Input the width of the board (must be an integer): ", int)

print("This is the board's dimensions: " + str(BoardHeight) + " H x " + str(BoardWidth) + " W")

# Generate array according to user inputted height and width
Board = h.generateArray(BoardHeight, BoardWidth)
print(Board)

while True:
    input("Press enter to generate next board")
    Board = h.applyRules(Board)

    # h.cls()
    print(Board)
