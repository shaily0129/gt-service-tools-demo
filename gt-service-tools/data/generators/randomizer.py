import random
import string
import ast
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

class Random:
    def __init__(self):
        self.id_counters = {}
        self.last_for_set_range = {}
    #     already_selected = []
    
    def fake_first_name():
        """Generate a fake first name if the key is 'first_name: "*"'."""
        return fake.first_name()

    def fake_last_name():
        """Generate a fake last name if the key is 'last_name:  "*"'."""
        return fake.last_name()

    def fake_callsign():
        """Generate a fake callsign if the key is 'callsign:  "*"'."""
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        numbers = ''.join(random.choices(string.digits, k=3))
        return f"{letters}{numbers}"
    
    def fake_datetime():
        """Generate a fake datetime within the past 8 hours if the key is 'dateTime: "*"'.."""
        now = datetime.now()
        # Generate a random number of seconds within the past 8 hours
        seconds_past = random.randint(0, 8 * 60 * 60)
        # Subtract the random number of seconds from the current time
        past_datetime = now - timedelta(seconds=seconds_past)
        # Convert to ISO format string
        date_time_str = past_datetime.isoformat()
        return date_time_str

    def date_today():
        """Generate a date object for today if the key is 'date: "*"'."""
        date = datetime.now()
        date = date.strftime("%Y-%m-%d")
        print(f"date: {date}")
        return date
    
    def fake_time():
        """Generate a fake time in the past on today's date if the key is 'time: "*"'."""
        now = datetime.now()
        # Generate a random number of seconds to subtract, up to the current time of the day
        seconds_past = random.randint(0, now.hour * 3600 + now.minute * 60 + now.second)
        # Subtract the random number of seconds from the current time
        past_time = now - timedelta(seconds=seconds_past)
        # Format the time
        time_str = past_time.strftime("%H:%M:%S")
        print(f"time: {time_str}")
        return time_str
    
    def military_alphabet_phrase(length=5):
        military_alphabet = {
            'A': 'Alpha', 'B': 'Bravo', 'C': 'Charlie', 'D': 'Delta', 'E': 'Echo',
            'F': 'Foxtrot', 'G': 'Golf', 'H': 'Hotel', 'I': 'India', 'J': 'Juliett',
            'K': 'Kilo', 'L': 'Lima', 'M': 'Mike', 'N': 'November', 'O': 'Oscar',
            'P': 'Papa', 'Q': 'Quebec', 'R': 'Romeo', 'S': 'Sierra', 'T': 'Tango',
            'U': 'Uniform', 'V': 'Victor', 'W': 'Whiskey', 'X': 'X-ray', 'Y': 'Yankee', 'Z': 'Zulu'
        }
        phrase = ' '.join(military_alphabet[random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')] for _ in range(length))
        return phrase
    
    
    @staticmethod
    def random_from_tuple(value):
        """Generate a random value within the range specified by a tuple string."""

        # Convert value from string to tuple if it's a string
        if isinstance(value, str):
            try:
                value = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                raise ValueError("value is string and not a valid tuple representation")
        elif not isinstance(value, tuple):
            raise ValueError("value must be a tuple or a string that represents a tuple")

        
        min_val, max_val = value  # Use the tuple directly

        # Check if the values are integer or floating-point
        if isinstance(min_val, int) and isinstance(max_val, int):
            # Generate a random integer if both min and max are integers
            random_number = random.randint(min_val, max_val)
            return random_number
        else:
            # Generate a random floating-point number if either min or max is a float
            min_val, max_val = float(min_val), float(max_val)
            random_float = random.uniform(min_val, max_val)
            return random_float
    



    def parse_count(count):
        """Parse the "count" value from the metadata definitions."""
        if isinstance(count, tuple):
            return Random.random_from_tuple('count', count)
        elif isinstance(count, str) and count.startswith('(') and count.endswith(')'):
            count_tuple = ast.literal_eval(count)
            return Random.random_from_tuple('count', count_tuple)
        else:
            return int(count)

    def select_from_options(options, selection_type, already_selected=[]):
        """Select items from options based on selection_type, excluding already selected if unique."""
        options = [option for option in options if option not in already_selected]
        if selection_type == "single" or selection_type == "unique":
            return random.choice(options) if options else None
        elif selection_type == "multiple":
            num_choices = random.randint(1, len(options))
            return random.sample(options, k=num_choices) if options else []
        else:
            raise ValueError(f"Invalid selection_type: {selection_type}")