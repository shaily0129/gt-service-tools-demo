import random
import uuid
from utils import Utils
from randomizer import Random

class IDGenerator:
    def __init__(self):
        self.counters = {}
        self.isop_ids = []
        # self.ids_copy = []
    
    num_iterations = 0 

    @classmethod
    def set_number_of_iterations(cls, number_of_iterations):
        cls.num_iterations = number_of_iterations
        
    def generate_uuid(self, node_dict):
        """
        Generate a UUID based on the _generate_uuid specifications.

        :param node: The node containing the_generate_uuid key.
        :return: The generated UUID as a string.
        """
        # _generate_uuid: {type: <type='sequential' or 'random'>, start: <int>, increment: <int>}
        id_meta = node_dict.pop('_generate_uuid', None)
        new_uuid = str(uuid.uuid4())
        if id_meta == "isop_id":
            self.isop_ids.append(new_uuid)
        return new_uuid

    def get_id(self, node_dict, index=0):
        """
        Retrieve a UUID generated for isop_details and assign it to isop_id for isop_state.

        :param node_dict: The node containing the _get_id key.
        :return: The UUID as a string if _get_id matches "isop_id"; otherwise, None.
        """
        get_id_spec = node_dict.pop('_get_id', None)
        if get_id_spec == "isop_id":
            # Assuming the UUIDs are assigned in the same order as they are generated
            if 0<= index < len(self.isop_ids):           
                # Retrieve and remove the first UUID from the list
                uuid = self.isop_ids[index]
                return uuid
            else:
                # Handle the case where no UUIDs are available (e.g., all have been assigned)
                print("Warning: No available UUIDs to assign for isop_id.")
                return None
        else:
            # _get_id does not match "isop_id" or is not present
            return None

    def get_ids(self, node_dict):
        """
        Return random length arrays of specific ids based on the _get_ids metadata.

        :param node_dict: The node containing the _get_ids key.
        :return: A list of ids of random length specified by the count in _get_ids metadata.
        """
        # Extract _get_ids metadata and remove it from node_dict
        get_ids_meta = node_dict.pop('_get_ids', None)
        if not get_ids_meta:
            return []

        id_name = get_ids_meta.get('id_name')
        count_range = get_ids_meta.get('count', (0,))  # Default to a tuple with a single zero if not specified

        # Randomly pick a count from the count_range tuple
        # count = random.choice(count_range)
        count = Random.random_from_tuple(count_range)

        if id_name == "isop_id":
            if len(self.isop_ids) == 0:
                print("Warning: No available UUIDs to assign for isop_id.")
                return []
            
            if not hasattr(self, 'ids_copy'):
                # Initialize ids_copy on the first call
                # print("Initializing isop_id copy.")
                self.ids_copy = self.isop_ids.copy()
            
            if len(self.ids_copy) == 0:
                print("All UUIDs have been assigned.")
                return []
                
            # Calculate the maximum number of ids that can be assigned per iteration
            max_ids_per_iteration = len(self.ids_copy) // IDGenerator.num_iterations

            # If max_ids_per_iteration is 0, it means there are not enough ids for each iteration
            # In this case, we should assign at least 1 id per iteration if possible
            max_ids_per_iteration = max(1, max_ids_per_iteration)

            # Randomly pick a count from the count_range tuple, considering the max_ids_per_iteration
            count = min(Random.random_from_tuple(count_range), max_ids_per_iteration)

            # Ensure the count does not exceed the number of available ids
            count = min(count, len(self.ids_copy))

            # Randomly pick 'count' number of ids from the copy, ensuring uniqueness
            selected_ids = random.sample(self.ids_copy, count)
            # Ensure the count does not exceed the number of available ids
            
            # count = min(count, len(self.ids_copy))

            # # Randomly pick 'count' number of ids from the copy, ensuring uniqueness
            # selected_ids = random.sample(self.ids_copy, count)

            # Remove the selected ids from the copied list to ensure each array is unique
            for id in selected_ids:
                self.ids_copy.remove(id)

            return selected_ids

        # If id_name does not match any known id collections, return an empty list
        return []

    def generate_id(self, node_dict):
        """
        Generate an ID based on the _generate_id specifications.

        :param node: The node containing the_generate_id key.
        :return: The generated ID as a string, ensuring it meets the min_length requirement.
        """
        # _generate_id: {type: <type='sequential' or 'random'>, start: <int>, increment: <int>, min_length: <int>}
        

        id_meta = node_dict.pop('_generate_id', None)
      
        if id_meta['type'] == 'sequential':
            # Convert node_dict to a hashable object (tuple of tuples sorted by key to ensure consistency)
            node_dict_hashable = Utils.make_hashable(node_dict)

            # Initialize the counter for this ID if it hasn't been already
            if node_dict_hashable not in self.counters:
                self.counters[node_dict_hashable] = id_meta['start']
            else:
                self.counters[node_dict_hashable] += id_meta['increment']

            generated_id = str(self.counters[node_dict_hashable])
        elif id_meta['type'] == 'random':
            # Generate a random ID between the start value and a large number, assuming start is the minimum
            generated_id = str(random.randint(id_meta['start'], id_meta['start'] + 1000000))
        else:
            raise ValueError("Unsupported ID generation type")

        # Ensure the generated ID meets the min_length requirement
        min_length = id_meta.get('min_length', 1)
        generated_id = generated_id.zfill(min_length)
      
        return int(generated_id) if id_meta['type'] == 'sequential' else generated_id