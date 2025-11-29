# Util file
# THis is the file with additional functions that are wide used across scripts

# Coordinates and Positions Utils

#  (0,0) (<- Coordinate value of the square)
# |-----|-----|
# | A1  | A2  | ... 1  (A1 <- position value)
# |-----|-----|
# | B1  | B2  | ... 2
# |-----|-----|
#   ...   ...
#    A     B

def pos_to_cord(pos: tuple[int, int]) -> str:
    # A function that changes the text position into a coordinate
    # eg. A1 -> (0,0)
    return "".join((chr(96 - pos[0] + 8), str(pos[1] + 1)))


def cord_to_pos(cord: str) -> tuple[int, int]:  # eg. (0, 0)
    # A function that changes the coordinate value to the text position
    # eg. (0,0) -> A1
    return 7 - (ord(cord[0]) - 97), int(cord[1]) - 1

