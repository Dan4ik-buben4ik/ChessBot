import json
import time





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