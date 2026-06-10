from position import PositionVector2D

import json

class Move:
    def __init__(self):
        self.original_position
        self.current_position
        self.piece

class MoveTracker:
    def __init__(self, half_moves=0, full_moves=1, json_tree=None, new=True):
        self.half_moves = 0
        self.full_moves = 0
        self.main_branch = []
        self.json_file = json_tree

        # code for the creation of the json tree
        if new:
            f = open(json_tree, "w+")
            f.close()


    def add_move(self, move, index):
        pass

    def remove_move(self, index, move):
        pass

    def check_if_draw(self):
        pass

