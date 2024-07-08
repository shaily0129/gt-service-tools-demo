from datetime import datetime, timedelta
import random
from randomizer import Random
from utils import Utils
from setRangeGenerator import SetRangeGenerator
# from dataProcessor import Process


class TimestampGenerator:
    def __init__(self, process_instance):
        self.process_instance = process_instance
        self.counters = {}
        already_selected = []

    
    def generate_single_timestamp(self, base_datetime, schema, min_delta, max_delta, unique_selections):
        """ Generate a single timestamp object based on the timestamp schema.
            This function is called by the generate_timestamps_data() function and called recursively for each item in the schema.
        """
        timestamp_obj = {'timestamp': base_datetime.isoformat()}
        for key, value in schema.items():
            if key == 'since_last_location':
                # TODO: write function to calculate distance and duration values since last location and assign to timestamp_obj['since_last_location'] distance and duration values
                # TODO: write function to calculate average_speed value since last location and assign to timestamp_obj['since_last_location'] average_speed value
                # TODO: write function to calculate average_speed_delta value since last location and assign to timestamp_obj['since_last_location'] average_speed_delta value
                continue
            elif key == 'total_all_locations':
                # TODO: write function to total all since_last_location distance and duration values and assign to timestamp_obj['total_all_locations'] distance and duration values
                # TODO: write function to average all since_last_location.average_speed values and assign to timestamp_obj['total_all_locations'] average_speed value
                continue
            
            self._process_schema_item(key, value, timestamp_obj, unique_selections)

        delta_minutes = random.randint(min_delta, max_delta)
        next_datetime = base_datetime + timedelta(minutes=delta_minutes)
        return timestamp_obj, next_datetime, unique_selections


    def generate_timestamps(self, node):
        timestamps = []
        if isinstance(node, dict):
            timestamp_meta = node.pop('_generate_timestamps', None)
            if timestamp_meta:
                count = Random.random_from_tuple(timestamp_meta['count'])
                min_delta, max_delta = map(int, timestamp_meta['timedelta(min)'].strip("()").split(","))
                base_datetime = datetime.now()
                unique_selections = {}

                if 'schemas' in timestamp_meta:
                    schema_paths = timestamp_meta['schemas']
                    for _ in range(count):
                        schema_path = random.choice(schema_paths)
                        loaded_schemas = Utils.load_schema(schema_path)
                        # If loaded_schemas is a list, select a random schema from the list
                        schema = random.choice(loaded_schemas) if isinstance(loaded_schemas, list) else loaded_schemas
                        timestamp_obj, next_datetime, unique_selections = self.generate_single_timestamp(
                            base_datetime, schema, min_delta, max_delta, unique_selections)
                        timestamps.append(timestamp_obj)
                        base_datetime = next_datetime
                else:
                    schema_path = timestamp_meta.get('schema')
                    if schema_path:
                        loaded_schema = Utils.load_schema(schema_path)
                        # Ensure loaded_schema is a dictionary
                        schema = loaded_schema if isinstance(loaded_schema, dict) else loaded_schema[0]
                        for _ in range(count):
                            timestamp_obj, next_datetime, unique_selections = self.generate_single_timestamp(
                                base_datetime, schema, min_delta, max_delta, unique_selections)
                            timestamps.append(timestamp_obj)
                            base_datetime = next_datetime
        return timestamps


    def _process_schema_item(self, key, value, timestamp_obj, unique_selections):
        """ Process each item in the schema.
            This function is called by the generate_single_timestamp() function and called recursively for each item in the schema.
            Args:
                key: The key of the item in the schema.
                value: The value of the item in the schema.
                timestamp_obj: The timestamp object to be updated.
                unique_selections: A dictionary of unique selections for each key.
            
        """
        # Check if key or value is empty and return early if so
        if not key or value is None:
            return

        # Process the schema item based on its type
        if key == 'timestamp':
            return
        elif key == 'location_label':
            timestamp_obj[key] = Random.military_alphabet_phrase(length=2)
        elif isinstance(value, str) and value.startswith("(") and value.endswith(")"):
            timestamp_obj[key] = Random.random_from_tuple(value)
        elif isinstance(value, list):
            self._process_list_value(key, value, timestamp_obj, unique_selections)
        elif isinstance(value, dict) and 'options' in value and 'selection_type' in value:
            self._process_dict_value(key, value, timestamp_obj, unique_selections)
        elif isinstance(value, dict) and '_set_range' in value:
            generator_function = self.process_instance.generator_tags.get('_set_range')
            if generator_function:
                # print(f"key: {key}")
                # print(f"value: {value}")
                timestamp_obj[key] = generator_function(key,value)
        else:
            timestamp_obj[key] = value



    def _process_list_value(self, key, value, timestamp_obj, unique_selections):
        """ Process a list value in the schema.
            This function is called by the process_schema_item() function and called recursively for each item in the schema.
        """
        selected_option = Random.select_from_options(value, "single" if len(value) == 1 else "multiple", unique_selections.get(key, []))
        timestamp_obj[key] = selected_option if isinstance(selected_option, list) else [selected_option]
        if 'unique' in value:
            unique_selections[key] = unique_selections.get(key, []) + [selected_option]



    def _process_dict_value(self, key, value, timestamp_obj, unique_selections):
        """ Process a dict value in the schema.
            This function is called by the process_schema_item() function and called recursively for each item in the schema.
        """
        selected_option = Random.select_from_options(value['options'], value['selection_type'], unique_selections.get(key, []))
        timestamp_obj[key] = selected_option
        if value['selection_type'] == 'unique':
            unique_selections[key] = unique_selections.get(key, []) + [selected_option]


