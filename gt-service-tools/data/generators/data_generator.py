import yaml
import json
from datetime import datetime, timedelta
import os
from utils import Utils
from dataProcessor import Process


# Instantiations
process = Process()

# Variables for input schema path, output path, and number of iterations
input_schema_path = '../schemas/isop_state.yaml'  # Update this path as needed
output_path = '../test_data/test_1'  # Update this path as needed
num_iterations = 10  # Specify the number of iterations



if __name__ == "__main__":
    all_iterations_output = []  # Initialize an empty list to hold all iterations

    Utils.ensure_directory_exists(output_path)  # Ensure the output directory exists
    # id_counters = {}    
    for iteration in range(num_iterations):
        with open(input_schema_path, 'r') as file:
            schema = yaml.safe_load(file)
        
        # processed_schema = process_node(schema, id_counters)
        processed_schema = process.process_node(schema)
        all_iterations_output.append(processed_schema)  # Append the processed schema to the list

    # Write the list of all processed schemas to a single output file
    output_file_name = Utils.set_output_file_name(input_schema_path)
    output_file_path = os.path.join(output_path, output_file_name)
    with open(output_file_path, 'w') as outfile:
        json.dump(all_iterations_output, outfile, indent=4)

    print(f"All iterations processed and saved to {output_file_path}")