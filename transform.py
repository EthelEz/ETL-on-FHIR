from datetime import datetime
import re

# Function to transform data (for simplicity, we assume no transformation here)
def transform_data(data):
    return data

def calculate_age(date_of_birth):   
    dob = datetime.strptime(date_of_birth, '%Y-%m-%d')
    current_date = datetime.now()
    age = current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))
    return age

def clean_text(string_input):
    new_text = re.sub("['\"\[\]_()*$\d+/]", "", string_input)
    return new_text