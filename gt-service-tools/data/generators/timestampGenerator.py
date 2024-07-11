from datetime import datetime, timedelta
import random
import ast
from randomizer import Random
from utils import Utils
from setRangeGenerator import SetRangeGenerator
# from dataProcessor import Process


TIMESTAMP_KEY = '_generate_timestamps'
class TimestampGenerator:
    def __init__(self, process_instance, Utils):
        self.process_instance = process_instance
        self.Utils = Utils
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



        timestamps = []
        unique_selections = {}
        
        if 'schemas' in timestamp_meta:
            schema_details = timestamp_meta['schemas']
            total_count_range = timestamp_meta.get('count', (1, 1))
            
            if isinstance(total_count_range, str):
                total_count_range = ast.literal_eval(total_count_range)
            
            total_count = random.randint(*total_count_range) if isinstance(total_count_range, tuple) else total_count_range
            schema_instance_counts = {schema_detail['schema']: 0 for schema_detail in schema_details}  # Track instances per schema
            
            while total_count > 0:
                schema_selected = False
                for schema_detail in schema_details:
                    # TODO: Ensure that if schema_detail includes 'no_duplicate_combination_of_fields: [array of parent schema fields]', then we don't generate a duplicate timestamp object with the same combination of fields.
                    # For example, with insults, we don't want multiple instances of the same type of insult with the same location, sublocation, lateral_position, etc.
                    if total_count <= 0:
                        break
                    schema_path = schema_detail['schema']
                    max_count_range = schema_detail.get('max_count', (1, 1))
                    
                    if isinstance(max_count_range, str):
                        max_count_range = ast.literal_eval(max_count_range)
                    
                    max_count = random.randint(*max_count_range) if isinstance(max_count_range, tuple) else max_count_range
                    
                    # Check if we can generate more instances for this schema
                    if schema_instance_counts[schema_path] < max_count:
                        loaded_schemas = self.Utils.load_schema(schema_path)
                        if isinstance(loaded_schemas, list):
                            schema = random.choice(loaded_schemas)
                        else:
                            schema = loaded_schemas
                        
                        timestamp_obj, next_datetime, unique_selections = self.generate_single_timestamp(
                            base_datetime, schema, min_delta, max_delta, unique_selections)
                        timestamps.append(timestamp_obj)
                        base_datetime = next_datetime
                        
                        schema_instance_counts[schema_path] += 1  # Increment count for this schema
                        total_count -= 1  # Decrement the total count after generating an instance
                        schema_selected = True
                        if total_count <= 0:
                            break
                
                # If no schema was selected in this iteration, it means we're stuck and should break out to prevent an infinite loop
                if not schema_selected:
                    break
                    
        return timestamps

    # def generate_timestamps_from_multiple_schemas(self, timestamp_meta, base_datetime, min_delta, max_delta):
        """ Generate a list of timestamp objects based on the timestamp schema.
            This function is called by the generate_timestamps() function and called recursively for each item in the schema.
            Args:
                timestamp_meta: The timestamp meta data.
                base_datetime: The base datetime.
                min_delta: The minimum delta.
                max_delta: The maximum delta.
        """
        timestamps = []
        unique_selections = {}

        if 'schemas' in timestamp_meta:
            schema_details = timestamp_meta['schemas']
            count_range = timestamp_meta.get('count', (1, 1))
            
            # Check if count_range is a string and convert it
            if isinstance(count_range, str):
                count_range = ast.literal_eval(count_range)

            count = random.randint(*count_range) if isinstance(count_range, tuple) else count_range

            for _ in range(count):
                schema_detail = random.choice(schema_details)
                schema_path = schema_detail['schema']
                max_count_range = schema_detail.get('max_count', (1, 1))
                allow_duplicate = schema_detail.get('allow_duplicate', True)
                
                # Ensure max_count_range is correctly interpreted as a tuple and converted if necessary
                if isinstance(max_count_range, str):
                    max_count_range = ast.literal_eval(max_count_range)
                
                # Correctly determine max_count as a random number within the range specified by max_count_range
                max_count = random.randint(*max_count_range) if isinstance(max_count_range, tuple) else max_count_range
                print

                for _ in range(max_count):
                    loaded_schemas = self.Utils.load_schema(schema_path)
                    # If loaded_schemas is a list, select a random schema from the list
                    if isinstance(loaded_schemas, list):
                        if allow_duplicate:
                            schema = random.choice(loaded_schemas)
                        else:
                            # Convert the schema to a string for a hashable representation
                            hashable_loaded_schemas = [str(s) for s in loaded_schemas if str(s) not in unique_selections]
                            if not hashable_loaded_schemas:
                                continue  # Skip if no unique schemas are left
                            schema_str = random.choice(hashable_loaded_schemas)
                            unique_selections[schema_str] = True
                            schema = ast.literal_eval(schema_str)  # Convert back to dict
                    else:
                        schema = loaded_schemas

                    timestamp_obj, next_datetime, unique_selections = self.generate_single_timestamp(
                        base_datetime, schema, min_delta, max_delta, unique_selections)
                    timestamps.append(timestamp_obj)
                    base_datetime = next_datetime

        return timestamps

    # def generate_timestamps(self, node):
        timestamps = []
        if isinstance(node, dict):
            timestamp_meta = node.pop('_generate_timestamps', None)
            if timestamp_meta:
                count = Random.random_from_tuple(timestamp_meta['count'])
                min_delta, max_delta = map(int, timestamp_meta['timedelta(min)'].strip("()").split(","))
                base_datetime = datetime.now()
                unique_selections = {}
                schema_path = None
                schemas_with_max_count = {}

                for _ in range(count):
                    if 'schemas' in timestamp_meta:
                        all_schemas = timestamp_meta['schemas']
                        schema_meta = random.choice(all_schemas)
                        schema_key = str(schema_meta['schema'])  # Convert schema_meta to string to use as key
                        # if max_count <= 0 for the schema, do not generate any more instances of this schema
                        if schema_key in schemas_with_max_count and schemas_with_max_count[schema_key]['max_count'] <= 0:
                            schema_path = None
                            continue

                        if 'max_count' in schema_meta:
                            # if schema_meta not already in schemas_with_max_count, set the max_count to a random number -1 and add to schemas_with_max_count
                            if schema_key not in schemas_with_max_count:
                                schema_meta['max_count'] = Random.random_from_tuple(schema_meta['max_count']) - 1
                                schemas_with_max_count[schema_key] = schema_meta
                            else:
                                # find the schema_meta in schemas_with_max_count and decrement the max_count by 1
                                schemas_with_max_count[schema_key]['max_count'] -= 1
                                

                        schema_path = schema_meta['schema']
                    else:
                        schema_path = timestamp_meta.get('schema')

                    if schema_path:
                        loaded_schema = Utils.load_schema(schema_path)
                        # Ensure loaded_schema is a dictionary
                        schema = loaded_schema if isinstance(loaded_schema, dict) else loaded_schema[0]
                       
                        timestamp_obj, next_datetime, unique_selections = self.generate_single_timestamp(base_datetime, schema, min_delta, max_delta, unique_selections)
                        timestamps.append(timestamp_obj)
                        base_datetime = next_datetime
        return timestamps
    

    def generate_timestamps(self, node):
        timestamps = []
        if isinstance(node, dict):
            timestamp_meta = node.pop(TIMESTAMP_KEY, None)
            if timestamp_meta:
                total_timestamps = Random.random_from_tuple(timestamp_meta['count'])
                min_delta, max_delta = self.get_time_deltas(timestamp_meta)
                base_datetime = datetime.now()
                unique_selections = {}
                schemas_with_max_count = {}

                for _ in range(total_timestamps):
                    schema_path, schemas_with_max_count = self.get_schema_path(timestamp_meta, schemas_with_max_count)
                    if schema_path:
                        timestamp_obj, base_datetime = self.generate_and_append_timestamp(schema_path, base_datetime, min_delta, max_delta, unique_selections, timestamps)
        return timestamps

    def get_time_deltas(self, timestamp_meta):
        return map(int, timestamp_meta['timedelta(min)'].strip("()").split(","))

    def get_schema_path(self, timestamp_meta, schemas_with_max_count):
        schema_path = None
        if 'schemas' in timestamp_meta:
            all_schemas = timestamp_meta['schemas']
            schema_meta = random.choice(all_schemas)
            schema_key = str(schema_meta['schema'])  # Convert schema_meta to string to use as key
            if schema_key in schemas_with_max_count and schemas_with_max_count[schema_key]['max_count'] <= 0:
                return None, schemas_with_max_count
            schemas_with_max_count = self.update_max_count(schema_meta, schema_key, schemas_with_max_count)
            schema_path = schema_meta['schema']
        else:
            schema_path = timestamp_meta.get('schema')
        return schema_path, schemas_with_max_count

    def update_max_count(self, schema_meta, schema_key, schemas_with_max_count):
        if 'max_count' in schema_meta:
            if schema_key not in schemas_with_max_count:
                schema_meta['max_count'] = Random.random_from_tuple(schema_meta['max_count']) - 1
                schemas_with_max_count[schema_key] = schema_meta
            else:
                schemas_with_max_count[schema_key]['max_count'] -= 1
        return schemas_with_max_count

    def generate_and_append_timestamp(self, schema_path, base_datetime, min_delta, max_delta, unique_selections, timestamps):
        loaded_schema = Utils.load_schema(schema_path)
        schema = loaded_schema if isinstance(loaded_schema, dict) else loaded_schema[0]
        timestamp_obj, next_datetime, unique_selections = self.generate_single_timestamp(base_datetime, schema, min_delta, max_delta, unique_selections)
        timestamps.append(timestamp_obj)
        return timestamp_obj, next_datetime

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
        # Ensure unique_selections[key] is initialized as a list if not already
        if key not in unique_selections:
            unique_selections[key] = []
        selected_option = Random.select_from_options(value['options'], value['selection_type'], unique_selections[key])
        timestamp_obj[key] = selected_option
        if value['selection_type'] == 'unique':
            unique_selections[key].append(selected_option)


