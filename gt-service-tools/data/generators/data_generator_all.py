import json
import yaml
from datetime import datetime, timedelta
import os
from utils import Utils
from dataProcessor import Process
from randomizer import Random

# Instantiations
process = Process()


def generate_all_test_data(format, test_cases, specific_test_case_names=None):
    
    
    num_test_cases = len(test_cases)
    if specific_test_case_names:
        num_test_cases = len(specific_test_case_names)
    print(f"Generating {num_test_cases} test cases...")
    
    for test_case in test_cases:
        test_name = test_case['name']

        # If specific test case names are provided, skip the ones not in the list
        if specific_test_case_names and test_name not in specific_test_case_names:
            continue

        output_path = f'../test_data/{test_name}'  # Construct the output directory path using the test case name

        Utils.ensure_directory_exists(output_path)  # Ensure the output directory exists
        print(f"{test_name}: {test_case['description']}")
        # print(f"Outputting test data to {output_path}... ")
        # Iterate through each input schema in the test case
        for input_schema in test_case['input_schemas']:
            schema_path = input_schema['path']
            num_iterations = input_schema['iterations']
            data_gap = 0 # (0-100) Percentage of data to be missing for select params

            # Check if missing_data_factor is specified in the input schema
            if 'data_gap' in input_schema:
                data_gap = input_schema['data_gap']
            
            # Set the missing data factor for various classes
            Random.set_data_gap_factor(data_gap)
            
            all_iterations_output = []  # Initialize an empty list to hold all iterations

            # Iterate through the number of iterations
            for iteration in range(num_iterations):
                schema = Utils.load_schema(schema_path)

                processed_schema = process.process_node(schema)
                all_iterations_output.append(processed_schema)  # Append the processed schema to the list
               
            # Write the list of all processed schemas to a single output file
            output_file_name = Utils.set_output_file_name(schema_path, format)
            output_file_path = os.path.join(output_path, output_file_name)

            if format == 'yaml':
                with open(output_file_path, 'w') as outfile:
                    yaml.dump(all_iterations_output, outfile, Dumper=CustomDumper, allow_unicode=True, default_flow_style=False, indent=4, sort_keys=False)
            elif format == 'json':
                with open(output_file_path, 'w') as outfile:
                    json.dump(all_iterations_output, outfile, indent=4)
            
            schema_base_name = os.path.basename(schema_path)
            
            print(f"- `{schema_base_name}`: {num_iterations} instances generated {f'with {data_gap}% missing data ' if data_gap  else ''}")
        print(f"DONE: All test case data generated and saved to {output_path}")
        print("  ")

class CustomDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(CustomDumper, self).increase_indent(flow, False)


if __name__ == "__main__":
    format = 'yaml'
    test_cases = Utils.load_schema('../test_cases/test_cases.yaml')
    specific_test_case_names = []  # Optional: Specify specific test cases here

    generate_all_test_data(format, test_cases, specific_test_case_names)
