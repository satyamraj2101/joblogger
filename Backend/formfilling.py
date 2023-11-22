import requests
from faker import Faker

# URL of the form submission website
url = "http://127.0.0.1:5000/add_job"

# Number of forms to fill
num_forms = 20

# Create a Faker instance for generating random data
fake = Faker()

# Loop to fill out the form multiple times
for _ in range(num_forms):
    # Generate random data for the form
    form_data = {
        'company_name': fake.company(),
        'position': fake.job(),
        'stage': fake.random_element(['wishlist', 'applied', 'interviewing', 'offer', 'rejected']),
        'salary': str(fake.random_number(4)),
        'job_type': fake.random_element(['remote', 'hybrid', 'onsite']),
        'url': fake.url(),
        'applied_on': fake.date_this_decade(),
        'description': fake.text(),
        'location': fake.city(),
        'application_type': fake.random_element(['part-time', 'full-time', 'internship']),
    }

    # Make a POST request to submit the form
    response = requests.post(url, data=form_data)

    # Check if the form submission was successful
    if response.status_code == 200:
        print(f"Form submitted successfully with data: {form_data}")
    else:
        print(f"Error submitting form with data: {form_data}")
