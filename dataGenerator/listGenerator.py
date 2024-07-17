import random
import ast
from randomizer import Random
from utils import Utils
from timestampGenerator2 import TimestampGenerator2
# from dataProcessor import Process




class ListGenerator:
    def __init__(self, process):
        self.process = process
        self.timestamp_generator = TimestampGenerator2(process, Utils)

    
    def _load_list_meta(self, parent_node):
        """Extract and return list metadata."""
        schema_path = None  # Initialize schema_path to None
        schema_paths = None  # Initialize schema_paths to None
        timestamp_meta = None  # Initialize timestamp_meta to None

        if '_generate_list' not in parent_node:
            return None, None, None, False
        
        list_meta = parent_node.pop('_generate_list')
        
        if 'schema' in list_meta:
            schema_path = list_meta['schema']
        elif 'schemas' in list_meta:
            schema_paths = list_meta['schemas']
            schema_path = self._choose_random_from_schemas(schema_paths)
        else:
            raise ValueError("List schema or schemas not specified.")
        
        if 'count' not in list_meta:
            raise ValueError("List count not specified. Should be a tuple eg. (0, 10)")
        
        if 'timestamp' in list_meta:
            timestamp_meta = list_meta['timestamp']
        
        return (
            schema_path,
            list_meta['count'],
            list_meta.get('append', None),
            list_meta.get('unique_instances', False),  # Extract unique_instances flag
            timestamp_meta  # Return timestamp_meta
        )

    def merge_append_schema(self, item_schema, append_path):
        """Merge append schema if provided."""
        if append_path:
            append_schema = Utils.load_schema(append_path)
            if not isinstance(append_schema, dict):
                raise ValueError(f"Invalid append_schema type: {type(append_schema)}")
            item_schema = {**item_schema, **append_schema}
        return item_schema

    def process_item_schema(self, item_schema):
        """Process and return a generated item from the schema."""
        return self.process.process_node(item_schema)

    def _generate_items(self, schema_path, count, append_path, unique_instances, timestamp_meta):
        """Generate and return a list of items based on the schema, ensuring uniqueness if required."""
        list_schema = Utils.load_schema(schema_path)
        if isinstance(list_schema, list):
            list_schema = {str(index): item for index, item in enumerate(list_schema)}
        if not isinstance(list_schema, dict):
            raise ValueError("List schema must be a dictionary or a list.")

        generated_list = []
        generated_instances = {}  # Track generated instances for uniqueness
        list_schema_values = list(list_schema.values())
        
        # if timestamp, this tracks the last timestamp generated
        last_timestamp = None
        
        while len(generated_list) < count:
            item_schema = random.choice(list_schema_values)
            item_schema = self.merge_append_schema(item_schema, append_path)
            generated_item = self.process_item_schema(item_schema)
            
            # If timestamp_meta is provided, generate a timestamp for the generated item following the timestamp metadata
            if timestamp_meta:
                generated_item, last_timestamp = self.timestamp_generator.generate_timestamp(generated_item, timestamp_meta, last_timestamp)
                

            # Ensure uniqueness if required
            if unique_instances:
                item_key = str(generated_item)  # Convert the item to a string to use as a dict key
                if item_key in generated_instances:
                    continue  # Skip this item since it's not unique
                generated_instances[item_key] = True

            generated_list.append(generated_item)

            # If unique_instances is True and we've exhausted possible unique items, break to avoid infinite loop
            if unique_instances and len(generated_instances) == len(list_schema_values):
                break

        return generated_list

    def generate_list(self, parent_node):
        schema_path, count_info, append_path, unique_instances, timestamp_meta = self._load_list_meta(parent_node)
        if schema_path is None:
            return []
        # todo: handle if schema_path is actually a list of multiple schemas

       
        count = Random.random_from_tuple(count_info) if isinstance(count_info, str) else int(count_info)
        generated_list = self._generate_items(schema_path, count, append_path, unique_instances, timestamp_meta)

        return generated_list[0] if count_info == 1 else generated_list
    
    def _choose_random_from_schemas(self, all_schemas):
        schema_path = None
        schema_meta = random.choice(all_schemas)

        # Handle schema_meta with  'max_count'
        if 'max_count' in schema_meta:
            print(f"max_count needs work")
            return
            schema_key = str(schema_meta['schema'])  # Convert schema_meta to string to use as key
            if schema_key in schemas_with_max_count and schemas_with_max_count[schema_key]['max_count'] <= 0:
                return None, schemas_with_max_count
            schemas_with_max_count = self._update_max_count(schema_meta, schema_key, schemas_with_max_count)
            schema_path = schema_meta['schema']
        else:
            schema_path = schema_meta['schema']

        return schema_path