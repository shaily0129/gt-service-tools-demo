import random
import ast
from randomizer import Random
from utils import Utils
# from dataProcessor import Process


class SetRangeGenerator:
    def __init__(self):
        self.last_for_set_range = {}
    

    def random_from_set_range(self, key, value):
        """Generate a random number within the range specified by the _set_range key."""
        # _set_range: {range: <tuple>, max_delta: <int>}
        set_range = value['_set_range']
        range_tuple = ast.literal_eval(set_range['range'])
        max_delta = set_range['max_delta']
        # print(f"max_delta: {max_delta}")

        # Get the parent node name
        parent_node_name = key
        
        # print(f"parent_node_name: {parent_node_name}")

        # If parent_node_name is in last_for_set_range, adjust the range based on max_delta
        if parent_node_name in self.last_for_set_range:
            last_value = self.last_for_set_range[parent_node_name]
            min_val, max_val = range_tuple
            adjusted_min = max(min_val, last_value - max_delta)
            adjusted_max = min(max_val, last_value + max_delta)
            range_tuple = (adjusted_min, adjusted_max)

        # Generate a random value within the adjusted range
        random_value = Random.random_from_tuple(range_tuple)

        # Update last_for_set_range with the new value for the parent_node_name
        self.last_for_set_range[parent_node_name] = random_value

        # Return the generated random value
        return random_value


        # min_val, max_val = map(int, set_range['min'].strip("()").split(","))
        # random_number = random.randint(min_val, max_val)
        # return random_number