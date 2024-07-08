import random
import uuid
from utils import Utils

class IDGenerator:
    def __init__(self):
        self.counters = {}
        self.isop_ids = []
        
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

    def get_id(self, node_dict):
        """
        Retrieve a UUID generated for isop_details and assign it to isop_id for isop_state.

        :param node_dict: The node containing the _get_id key.
        :return: The UUID as a string if _get_id matches "isop_id"; otherwise, None.
        """
        get_id_spec = node_dict.pop('_get_id', None)
        if get_id_spec == "isop_id":
            # Assuming the UUIDs are assigned in the same order as they are generated
            if self.isop_ids:
                # Retrieve and remove the first UUID from the list
                uuid = self.isop_ids.pop(0)
                return uuid
            else:
                # Handle the case where no UUIDs are available (e.g., all have been assigned)
                print("Warning: No available UUIDs to assign for isop_id.")
                return None
        else:
            # _get_id does not match "isop_id" or is not present
            return None



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