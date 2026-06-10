import re



'''
move format:  f"{piece}{init_pos}-{new_pos}"
'''

class PGNEditor:
    @staticmethod
    def load(root):
        print(f"PGNEditor.load: {root}")
        #TODO: add support for multiple games in a pgn
        with open(root, "r") as pgn:
            result = dict()
            data = pgn.read().split("\n\n")

            game_data = data[0].split("\n")
            result["Event"] = re.findall(r'"([^"]+)"', game_data[0])[0]
            result["Site"] = re.findall(r'"([^"]+)"', game_data[1])[0]
            result["Date"] = re.findall(r'"([^"]+)"', game_data[2])[0]
            result["Round"] = re.findall(r'"([^"]+)"', game_data[3])[0]
            result["White"] = re.findall(r'"([^"]+)"', game_data[4])[0]
            result["Black"] = re.findall(r'"([^"]+)"', game_data[5])[0]
            result["Result"] = re.findall(r'"([^"]+)"', game_data[6])[0]
            result["ECO"] = re.findall(r'"([^"]+)"', game_data[7])[0]
            result["Annotator"] = re.findall(r'"([^"]+)"', game_data[8])[0]
            result["HalfMoves"] = re.findall(r'"([^"]+)"', game_data[9])[0]
            result["Event Date"] = re.findall(r'"([^"]+)"', game_data[10])[0]
            result["SourceTitle"] = re.findall(r'"([^"]+)"', game_data[11])[0]
            result["Source"] = re.findall(r'"([^"]+)"', game_data[12])[0]
            result["SourceDate"] = re.findall(r'"([^"]+)"', game_data[13])[0]

            # TODO: add for the search for the game (skip "" lines)
            # data[14] is space
            game = data[1]
            game = re.sub(r'(?<=,)\n+', '', game)
            game = re.sub(r'\n+', ' ', game)
            print(game)

            print(result)



PGNEditor.load("italian.pgn")
