# OVERVIEW

This system generates data according to specifications in a listof Scenarios.
Each Scenario is a dictionary that contains metadata about the scenario and an array of input schemas to generate data for.
You can specify the number of iterations to generate data for each input schema as well as the percentage of data to be missing.
Data for each input schema is generated recursively, so the schemas can be nested and quite complex and even reference other schemas.
The actual data generation uses a library of special values and '_generator_tags' that trigger corresponding methods.
Finally, generated data is saved to specific directories in the `../test_data` directory.
TODO: Update when generated data is saved to a database.
TODO: Link to demo video here
<!-- <video width="320" height="240" controls>
  <source src="URL_TO_VIDEO" type="video/mp4">
  Your browser does not support the video tag.
</video> -->

***

## GETTING STARTED

Ensure your environment is `python 3.10.5`
From the project `root`, run `pip install -r requirements.txt` to install the required packages.

***

## SETTING UP TEST CASES

All Test Cases are located in the `../data/test_data/test_cases.yaml` file.
Here is the structure of a test case:

```yaml
- name: # Will be the name of the output directory in ../test_data/
  description: # A brief description of the test case
  functionality_to_test: # The expected functionality to be developed and tested for the test case
  coda_link: # A link to the CODA page for the test case if available
  input_schemas: # A list of input schemas to generate test data for
    - path: # The path to the input schema from ../schemas
      iterations: # The number of iterations to generate test data for
      data_gap: # (0-100) Percentage of data to be missing for select params in that schema
```

**NOTE:** New test case files can be created, but you will need to update the `../data/generators/generate_data.py` file to include the new test case.

***

## GENERATING TEST DATA

To generate test data for all test cases...

- navigate to `../data/generators.py`
- then in your terminal run: `python generate_data.py`

To generate test data for a specific schemas, update the `specific_test_case_names` variable at the bottom of the `generate_data.py` file.
For example, if you want to generate test data for the `test_1` and `test_2` test cases, you would update the variable to:

```python
specific_test_case_names = ['test_1', 'test_2']
```

***

## SCHEMA PARAMETERS

**NOTE:** Throughout the schemas, "!" indicates that a data_gap % will introduced to that field, if data_gap is indicated in the test_case metadata.

### Special Keys

The following keys in schemas have special methods to generate corresponding data:

```yaml
first_name: < "*" or "!" > # Generates a random first name.
last_name: < "*" or "!" > # Generates a random last name.
callsign: < "*" or "!" > # Generates a random callsign.
dateTime: < "*" or "!" > # Generates a random datetime.
date: < "*" or "!" > # Generates a random date.
time: < "*" or "!" > # Generates a random time.
```

`"*"` - forces a value to be generated regardless of data_gap
`"!"` - if data_gap is set in the test_case schema, the value may sometimes be None.

<br>

### Tuple Ranges

If you want to specify a range for key, you can use tuples, like:
`(min, max)` - A random value from the range will be generated, data_gap is ignored.
`(min, max)!` - A random value from the range will be generated, but if data_gap is set, the value may sometimes be None.

<br>

### Select Lists

For simple lists, you can use the following syntax:

```yaml
list_of_options:
  selection_type: <single!, multiple!, unique!> # The type of selection to perform. NOTE: ommitting the ! will ignore data_gap and force a value to be generated.
  options: # The list of options to select from.
    - option1
    - option2
    - option3
```

**NOTE:** For more complex options, use `_generate_list`: (see below)

<br>

### How to Generate IDs

To generate UUIDs, use the following syntax:

```yaml
#schema_A.yaml
some_id:
  _generate_uuid:

#output schema_A.yaml
some_id: 2d3e4f5g-6h7i-8j9k-0l1m-2n3o4p5q6r7s
```  

<br>

It is also possible to reference generated UUIDs in other schemas, via the following syntax:

```yaml
# In example schema_A.yaml, set a UUID identifier, for example:
user_id: # The key to assign the UUID to.
  _generate_uuid: "user_id" # The identifier to assign the UUID to.

#In the output it will still look like this:
user_id: 2d3e4f5g-6h7i-8j9k-0l1m-2n3o4p5q6r7s
```

```yaml
# Then in example schema_B.yaml, use _get_id to reference the key UUID you want:
user_id:
  _get_id: "user_id"

#output schema_B.yaml
user_id: 2d3e4f5g-6h7i-8j9k-0l1m-2n3o4p5q6r7s
```

**NOTE:** to use this technique, the schema getting the ids should be referenced after the schema generating the ids, and both should have the same number of iterations.
For example if schema_A has 10 iterations, schema_B should also have 10 iterations and be referenced after schema_A in test_cases.yaml.

<br>

To generate simple sequential or random IDs, use the following syntax:**

```yaml
_generate_id:
  type: <'sequential' or 'random'> # The type of ID generation.
  start: <int> # The starting value of the ID.
  increment: <int> # The increment value of the ID.
  min_length: <int> # The minimum length of the ID.
```

### How to Generate Complex Lists

To generate a list from a single schema, use the following syntax:

```yaml
_generate_list:
  schema: <path>  # The path to the schema to generate a list from.
  count: <tuple>  # The number of items to generate.
  unique_instances: <bool>  # If True, ensure uniqueness of items in the list
  # append: <path>  # The path to another schema to append to list items, like a timestamp schema
  # type: <timestamp>  # The type of list to generate.  Currently only supports timestamp.
  # timedelta(min): <tuple>  # The minimum and maximum time delta between timestamps in minutes, if type: 'timestamp'
```

TODO: Add support for appending to list items.
TODO: Add support for generating a list from multiple schemas like _generate_timestamps.
TODO: Refactor and combine listGenerator.py and timestampGenerator.py so that type: 'timestamp' can be bassed into listGenerator.py.

### How to Generate Complex Timestamps

```yaml
_generate_timestamps:
  schema: <path> # The path to the schema to generate a list from.
  count: <tuple> # The number of items to generate.
  timedelta(min): <tuple>} #  The minimum and maximum time delta between timestamps in minutes.
```

```yaml
_generate_timestamps:
  schemas:
    - schema: <path> # The path to a schema to generate a list from.
      max_count: <tuple>  # Optional: The maximum number of items to generate.
    - schema: <path> # The path to another schema to generate a list from.
  count: <tuple> # The number of items to generate.
  timedelta(min): <tuple>} #  The minimum and maximum time delta between timestamps in minutes.
```
