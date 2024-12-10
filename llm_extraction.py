# import pandas as pd
# import openai
# import json
# from tqdm import tqdm
# import time


# # Set your OpenAI API key
# openai.api_key = 'your api key'


# def extract_attributes(post_content):
#     system_message = "You are a helpful assistant that extracts specific information from job postings."
#     user_prompt = f'''Please extract the following details from the provided post content and return them as a JSON object:

# - Experience Required
# - Salary
# - Location
# - Skills Required
# - Summary
# - Email
# - Phone Number
# - Position
# - Company Name
# - Job Type
# - Shift Details
# - Job Responsibilities
# - Application Deadline
# - Benefits
# - Required Qualifications

# **Instructions:**

# - Only include the specified information; do not add extra details.
# - Provide a summary of the post without repeating information covered by other attributes.
# - If a piece of information is not provided in the post content, assign `"Null"` to that attribute.

# **Post Content:**
# {post_content}

# **Return the details in the following JSON format:**

# {{
#     "Experience Required": <Experience_Required OR Null>,
#     "Salary": <Salary OR Null>,
#     "Location": <Location OR Null>,
#     "Skills Required": [
#         <Skill1>, <Skill2>, ...
#     ],
#     "Summary": <Summary OR Null>,
#     "Email": <Email OR Null>,
#     "Phone Number": <Phone_Number OR Null>,
#     "Position": <Position OR Null>,
#     "Company Name": <Company Name OR Null>,
#     "Job Type": <Job_Type OR Null>,
#     "Shift Details": <Shift_Details OR Null>,
#     "Job Responsibilities": <Job_Responsibilities OR Null>,
#     "Application Deadline": <Application_Deadline OR Null>,
#     "Benefits": <Benefits OR Null>,
#     "Required Qualifications": <Required_Qualifications OR Null>
# }}
# '''

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4o-mini-2024-07-18", 
#         messages=[
#             {"role": "system", "content": system_message},
#             {"role": "user", "content": user_prompt}
#         ],
#         temperature=0,
#         top_p = 0
#         )

#         # Extract the response
#         attributes_json = response['choices'][0]['message']['content'].strip()
#         return attributes_json 

#     except Exception as e:
#         print(f"Error processing post content: {e}")
#         return None

# def process_attributes_response(attributes_json):
#     try:
#         # Clean the response to ensure it's valid JSON
#         # Remove any markdown code blocks or extra formatting
#         if attributes_json.startswith("```json"):
#             attributes_json = attributes_json.strip("```json").strip()
#         elif attributes_json.startswith("```"):
#             attributes_json = attributes_json.strip("```").strip()

#         # Attempt to parse the JSON
#         attributes = json.loads(attributes_json)
#         return attributes

#     except json.JSONDecodeError as e:
#         print(f"JSON parsing error: {e}")
#         print(f"Response received:\n{attributes_json}\n")
#         return None
#     except Exception as e:
#         print(f"Error processing response: {e}")
#         return None
    
# # Load your data (assuming a CSV file format)
# data = pd.read_csv('D:\Learning\linkedin job post data extrackter\cleaned_linkedin_posts_with_links_v1.csv')

# # Initialize lists to store extracted data
# extracted_data = []

# # List of attribute keys
# attribute_keys = [
#     "Experience Required",
#     "Salary",
#     "Location",
#     "Skills Required",
#     "Summary",
#     "Email",
#     "Phone Number",
#     "Position",
#     "Company Name",
#     "Job Type",
#     "Shift Details",
#     "Job Responsibilities",
#     "Application Deadline",
#     "Benefits",
#     "Required Qualifications",
#     "Response"
# ]

# for index, row in tqdm(data.iterrows(), total=data.shape[0], desc="Processing posts"):
#     post_content = row['Post_Content']
#     attributes_json = extract_attributes(post_content)  # Get the raw response

#     attributes = process_attributes_response(attributes_json)  # Process the response

#     if attributes is not None:
#         attributes['Response'] = attributes_json  # Original model response if needed
#     else:
#         # If processing failed, set all attributes to None
#         attributes = {key: None for key in attribute_keys}
#         attributes['Response'] = attributes_json  # Include the raw response for debugging

#     extracted_data.append(attributes)

#     # Optional: Sleep to respect rate limits (adjust as needed)
#     time.sleep(1)  # Add a delay between requests

# # Convert the list of dictionaries to a DataFrame
# extracted_df = pd.DataFrame(extracted_data)

# # Merge the original data with the extracted attributes
# final_df = pd.concat([data.reset_index(drop=True), extracted_df], axis=1)

# # Save the final DataFrame to a new CSV file
# final_df.to_csv('extracted_job_data_llm_v1.csv', index=False)

# print("Extraction complete! The results have been saved to 'extracted_job_data_llm.csv'.")

import os
import time
import json
from tqdm import tqdm
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

# -------------------------------
# CONFIGURATIONS
# -------------------------------

OUTPUT_DIR = "data"
CLEANED_DATA_FILE = os.path.join(OUTPUT_DIR, "cleaned_linkedin_posts.csv")
FINAL_DATA_FILE = os.path.join(OUTPUT_DIR, "extracted_job_data_llm.csv")

def extract_attributes(post_content):
    system_message = "You are a helpful assistant that extracts specific information from job postings."
    user_prompt = f'''Please extract the following details from the provided post content and return them as a JSON object:

- Experience Required [ Number of years ]
- Location [ Location Name]
- Job Type  [Onsite or Remote or Hybrid]
- Email 
- Phone Number
- Position 
- Company Name

**Instructions:**
- Only include the specified information; do not add extra details.
- Provide a summary of the post without repeating information covered by other attributes.
- If a piece of information is not provided in the post content, assign "Null" to that attribute.

**Post Content:**
{post_content}

**Return the details in the following JSON format:**

{{
    "Experience Required": <Number_of_years OR Null>,
    "Location": <Location OR Null>,
    "Job Type" : <Onsite or Remote or Hybrid>,
    "Email": <Email OR Null>,
    "Phone Number": <Phone_Number OR Null>,
    "Position": <Position OR Null>,
    "Company Name": <Company Name OR Null>
}}
'''

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
        )
        attributes_json = response.choices[0].message.content.strip()
        return attributes_json
    except Exception as e:
        print(f"Groq API Error: {e}")
        return None

def process_attributes_response(attributes_json):
    if not attributes_json:
        return None
    # Clean up JSON markers if present
    attributes_json = attributes_json.strip("```json").strip("```").strip()
    try:
        return json.loads(attributes_json)
    except json.JSONDecodeError:
        return None

if __name__ == "__main__":
    # Load cleaned data
    data = pd.read_csv(CLEANED_DATA_FILE)
    extracted_data = []
    attribute_keys = [
        "Experience Required", "Location","Job Type", "Email", "Phone Number", "Position", "Company Name","Response"
    ]

    print("Running LLM extraction...")
    for _, row in tqdm(data.iterrows(), total=data.shape[0], desc="Processing posts"):
        post_content = row['Post_Content']
        attributes_json = extract_attributes(post_content)
        attributes = process_attributes_response(attributes_json)
        if attributes is not None:
            attributes['Response'] = attributes_json
        else:
            attributes = {key: None for key in attribute_keys}
            attributes['Response'] = attributes_json
        extracted_data.append(attributes)

        # Adjust delay if needed to respect API rate limits
        time.sleep(1)

    extracted_df = pd.DataFrame(extracted_data)
    final_df = pd.concat([data.reset_index(drop=True), extracted_df], axis=1)
    final_df.to_csv(FINAL_DATA_FILE, index=False)

    print(f"LLM extraction completed. Final data saved to {FINAL_DATA_FILE}.")
