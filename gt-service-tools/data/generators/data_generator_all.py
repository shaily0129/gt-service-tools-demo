import json
import yaml
from datetime import datetime, timedelta
import os
from utils import Utils
from dataProcessor import Process
from randomizer import Random

# Instantiations
process = Process()

# def process_isop_state(self, schema):
#     if 'isop_state.yaml' in schema.get('source', ''):
#         # Assuming 'insults' is a key in the schema that contains a list of insult objects
#         for insult in schema.get('insults', []):
#             insult_id = insult.get('insult_id')
#             # Assuming each insult object has a 'records' key with a list of record objects
#             for record in insult.get('records', []):
#                 # Copying the insult_id to each of the insult's record objects
#                 record['insult_id'] = insult_id
#             # Assuming there's a 'patient_records' list in the schema to copy all insult records to
#             if 'patient_records' not in schema:
#                 schema['patient_records'] = []
#             schema['patient_records'].extend(insult.get('records', []))
#     return schema

def generate_all_test_data(test_cases, format):
    for test_case in test_cases:
        test_name = test_case['name']
        output_path = f'../test_data/{test_name}'  # Construct the output directory path using the test case name

        Utils.ensure_directory_exists(output_path)  # Ensure the output directory exists

        for input_schema in test_case['input_schemas']:
            schema_path = input_schema['path']
            num_iterations = input_schema['iterations']
            all_iterations_output = []  # Initialize an empty list to hold all iterations

            for iteration in range(num_iterations):
                schema = Utils.load_schema(schema_path)

                processed_schema = process.process_node(schema)
                # print(f"processed_schema: {schema.get('source', '')}")
                all_iterations_output.append(processed_schema)  # Append the processed schema to the list
                # print(f"schema: {schema}")
            # Write the list of all processed schemas to a single output file
            output_file_name = Utils.set_output_file_name(schema_path, format)
            output_file_path = os.path.join(output_path, output_file_name)

            if format == 'yaml':
                with open(output_file_path, 'w') as outfile:
                    yaml.dump(all_iterations_output, outfile, allow_unicode=True, default_flow_style=False, indent=4, sort_keys=False)
            elif format == 'json':
                with open(output_file_path, 'w') as outfile:
                    json.dump(all_iterations_output, outfile, indent=4)
            
            schema_base_name = os.path.basename(schema_path)

            print(f"{num_iterations} iterations processed for {schema_base_name} and saved to {output_file_path}")



if __name__ == "__main__":
    format = 'yaml'
    test_cases = Utils.load_schema('../test_cases/test_cases.yaml')
    missing_data_factor = 100 # (0-100) Percentage of data to be missing for select params

    # Set the missing data factor for various classes
    Random.set_missing_data_factor(missing_data_factor)

    generate_all_test_data(test_cases, format)
