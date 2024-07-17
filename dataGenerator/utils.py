import os
import yaml

class Utils:
    def __init__(self):
        pass

    def ensure_directory_exists(directory):
        """Ensure the output directory exists."""
        if not os.path.exists(directory):
            os.makedirs(directory)

    def load_schema(schema_path):
        """Load and return the schema from a YAML file."""
        with open(schema_path, 'r') as schema_file:
            return yaml.safe_load(schema_file)
    
    @staticmethod
    def make_hashable(obj):
        if isinstance(obj, dict):
            return tuple(sorted((k, Utils.make_hashable(v)) for k, v in obj.items()))
        elif isinstance(obj, list):
            return tuple(Utils.make_hashable(v) for v in obj)
        else:
            return obj
        
    @staticmethod
    def set_output_file_name(input_schema_path, file_format):
        schema_base_name = os.path.basename(input_schema_path).split('.')[0]  # Extract base name without extension
        plural_schema_base_name = schema_base_name + 's'  # Simple pluralization by appending 's'
        output_file_name = plural_schema_base_name + '.' + file_format  # Construct output file name
        return output_file_name
    

