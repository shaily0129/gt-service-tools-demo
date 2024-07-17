import re
from randomizer import Random
from idGenerator import IDGenerator
from listGenerator import ListGenerator
from timestampGenerator import TimestampGenerator
from setRangeGenerator import SetRangeGenerator
from utils import Utils


class Process:
    def __init__(self):
        # self.counters = {}
        self.id_generator = IDGenerator()
        self.list_generator = ListGenerator(self)
        self.timestamp_generator = TimestampGenerator(self, Utils)
        self.set_range_generator = SetRangeGenerator()
        self.special_keys = {
            "first_name": Random.fake_first_name,
            "last_name": Random.fake_last_name,
            "callsign": Random.fake_callsign,
            "dateTime": Random.fake_datetime,
            "date": Random.date_today,
            "time": Random.fake_time, # some random time in the past on today's date
        }
        self.generator_tags = {
            '_generate_uuid': self.id_generator.generate_uuid,
            '_generate_id': self.id_generator.generate_id,
            '_get_id': self.id_generator.get_id,
            '_get_ids': self.id_generator.get_ids,
            '_generate_list': self.list_generator.generate_list,
            '_generate_timestamps': self.timestamp_generator.generate_timestamps,
            '_set_range': self.set_range_generator.random_from_set_range
        }
        # TODO: _get_single_item

    # Process the node in the schema
    def process_node(self, node):
        """
        Recursively process each node based on its type and specific keys.

        Args:
            node: The node to be processed.

        Returns:
            The processed node.

        """
        if isinstance(node, dict):
            return self.process_dict(node)
        elif isinstance(node, list):
            return [self.process_node(item) for item in node]
        else:
            # Directly return the node if it's neither a dict nor a list
            return node

    def process_dict(self, node_dict):
        """Process a dictionary node, applying specific logic based on keys.

        Args:
            node_dict (dict): The dictionary node to be processed.

        Returns:
            dict: The processed dictionary node.

        """
        processed_node = {}

        # TODO: Refactor to def handle_generator_tags(self, node_dict):
        # Handle the generator_tags
        generator_tags = self.generator_tags
        for key in generator_tags:
            if key in node_dict:

                generated_data = generator_tags[key](node_dict)
                
                if isinstance(generated_data, dict):
                    processed_node.update(generated_data)  # Update processed_node with the generated data if it's a dict
                elif isinstance(generated_data, list):
                    processed_node = generated_data  # Update processed_node with the generated data
                elif key == '_generate_uuid' and isinstance(generated_data, str):
                    # self.isop_ids.append(generated_data)
                    processed_node = generated_data  # Update processed_node with the generated data
                elif key == '_get_id' and isinstance(generated_data, str):
                    processed_node = generated_data  # Update processed_node with the generated data
                elif key == '_generate_id' and isinstance(generated_data, str) or isinstance(generated_data, int):
                    processed_node = generated_data  # Update processed_node with the generated data
                else:
                    # Handle the case where generated_data is neither a dictionary nor a list
                    print(f"Unexpected generated_data type: {type(generated_data)}")

        for key, value in node_dict.items():
            try:
                # TODO: Refactor to def handle_special_keys(self, node_dict):
                # Handle the special_keys
                if key in self.special_keys:
                    processed_node[key] = self.special_keys[key](value)

                # TODO: Refactor to handle_other_types(self, node_dict):
                # Handle other types of values 
                elif isinstance(value, str) and re.match(r"\(\d+,\d+\)", value):
                    processed_node[key] = Random.random_from_tuple(value)
                elif isinstance(value, dict) and 'options' in value and 'selection_type' in value:
                    processed_node[key] = Random.select_from_options(value['options'], value['selection_type'])
                elif isinstance(value, dict) or isinstance(value, list):
                    # Skip processing for '_timestampMeta' and '_listGenMeta' keys as they're already handled
                    if key not in generator_tags:
                        processed_node[key] = self.process_node(value)
                else:
                    processed_node[key] = value
            except ValueError as e:
                print(f"Error processing {key}: {e}")
        return processed_node