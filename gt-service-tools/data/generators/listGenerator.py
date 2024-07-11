import random
import ast
from randomizer import Random
from utils import Utils
# from dataProcessor import Process




class ListGenerator:
    def __init__(self, process):
        self.process = process

    def load_list_meta(self, parent_node):
        """Extract and return list metadata."""
        if '_generate_list' not in parent_node:
            return None, None, None, False
        list_meta = parent_node.pop('_generate_list')
        return (
            list_meta['schema'],
            list_meta['count'],
            list_meta.get('append', None),
            list_meta.get('unique_instances', False)  # Extract unique_instances flag
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

    def generate_items(self, schema_path, count, append_path, unique_instances):
        """Generate and return a list of items based on the schema, ensuring uniqueness if required."""
        list_schema = Utils.load_schema(schema_path)
        if isinstance(list_schema, list):
            list_schema = {str(index): item for index, item in enumerate(list_schema)}
        if not isinstance(list_schema, dict):
            raise ValueError("List schema must be a dictionary or a list.")

        generated_list = []
        generated_instances = {}  # Track generated instances for uniqueness
        list_schema_values = list(list_schema.values())

        while len(generated_list) < count:
            item_schema = random.choice(list_schema_values)
            item_schema = self.merge_append_schema(item_schema, append_path)
            generated_item = self.process_item_schema(item_schema)

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
        schema_path, count_info, append_path, unique_instances = self.load_list_meta(parent_node)
        if schema_path is None:
            return []

        count = Random.random_from_tuple(count_info) if isinstance(count_info, str) else int(count_info)
        generated_list = self.generate_items(schema_path, count, append_path, unique_instances)

        return generated_list[0] if count_info == 1 else generated_list