import random
import ast
from randomizer import Random
from utils import Utils
# from dataProcessor import Process




class ListGenerator:
    def __init__(self, process):
        self.counters = {}
        self.process = process
        already_selected = []
    
    def generate_list(self, parent_node):
        from dataProcessor import Process
        """Generate a list based on the _generate_list key and assign it directly to the parent node."""
        # _generate_list: {schema: <path>, count: <tuple>, append: <path>}

        if '_generate_list' in parent_node:
            list_meta = parent_node.pop('_generate_list', None)  # Use pop to remove the _generate_list key and get its value
            schema_path = list_meta['schema']
            count_info = list_meta['count']
            append_path = list_meta.get('append', None) # Get the append path if it exists
            
            # Load the list schema
            list_schema = Utils.load_schema(schema_path)

            generated_list = []  # Initialize an empty list to hold generated items
            generated_ids = []
            
            # Determine the number of items to generate
            if isinstance(count_info, str):
                count = Random.random_from_tuple(count_info)
            else:
                count = int(count_info)    

            if isinstance(list_schema, list):
                # Convert list_schema from a list to a dictionary using list index as key
                list_schema_dict = {str(index): item for index, item in enumerate(list_schema)}
                list_schema = list_schema_dict

            if isinstance(list_schema, dict):
                # Now list_schema is always a dictionary, proceed as before
                list_schema_values = list(list_schema.values())  # Convert dict values to list

                for _ in range(count):
                    # Randomly select an item from the list schema values
                    item_schema = random.choice(list_schema_values)
                    # If append_param is provided, merge it with the selected item schema before processing
                    if append_path:
                        append_schema = Utils.load_schema(append_path)
                        if isinstance(append_schema, dict):
                            item_schema = {**item_schema, **append_schema}
                        else:
                            raise ValueError(f"Invalid append_schema type: {type(append_schema)}")
                    # Recursively generate data for the selected item
                    generated_item = self.process.process_node(item_schema)
                    generated_list.append(generated_item)
                    
                    # if 'insult_id' in generated_item:
                    #     generated_ids.append(generated_item['insult_id'])

            # Assign the generated list directly to the parent node
            if count_info == 1: # TODO: break out into a separate function _get_single_item()
                return generated_list[0]
            else:
                return generated_list
        else:
            # If no _generate_list key, return an empty list or handle accordingly
            return []