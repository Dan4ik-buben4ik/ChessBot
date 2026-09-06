import json
import time




class SearchLogger:
    data = {
        "root": {"moves": [], "move evaluations": [], "evaluation": 0, "depth": 0}
    }
    parent_path = "root"
    nodes = 0


    def log_intro(self, move, depth):
        self.nodes += 1
        new_path = f"{self.parent_path}/{move.to_uci()}"
        self.data[self.parent_path]["moves"].append(move.to_uci())
        self.data[self.parent_path]["depth"] = depth
        self.parent_path = new_path

        self.data[new_path] = {"moves": [], "move evaluations": [], "evaluation": 0, "depth": 0}

    def log_outro(self, evaluation):
        new_path = "/".join(self.parent_path.split("/")[:-1])
        self.data[self.parent_path]["evaluation"] = evaluation
        if new_path:
            self.data[new_path]["move evaluations"].append(evaluation)
        self.parent_path = new_path


    def print_dict(self):
        with open("log.txt", "w", encoding="utf-8") as file:
            file.write(json.dumps(self.data, indent=4))
            file.write("\n")
            file.flush()
        # print(json.dumps(self.data, indent=4))

    def view_dict(self):
        try:
            path = input("\nInput the path to check the values: ")
            temp = self.data[path]
            print(f"path: {path}")
            print(f"moves: {temp['moves']}")
            print(f"path evaluation: {temp['evaluation']}")
            print(f"move evaluations: {temp['move evaluations']}")
            print(f"depth: {temp['depth']}")
        except BaseException:
            print("There is no such path")


def timer(func):
    def wrapper(*args, **kwargs):
        time_start = time.time()
        result = func(*args, **kwargs)
        time_taken = time.time() - time_start
        print(f"time taken: {time_taken}")
        return result

    return wrapper



def perfit(depth):
    #TODO: finish the function
    pass