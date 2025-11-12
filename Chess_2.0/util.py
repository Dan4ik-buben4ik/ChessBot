def pos_to_cord(pos):
    return "".join((chr(96 - pos[0] + 8), str(pos[1] + 1)))


def cord_to_pos(cord):
    return 7 - (ord(cord[0]) - 97), int(cord[1]) - 1

