import csv
import re

# Function to clean and extract the name and main post content
def clean_post_content(post_content):
    # Define regex patterns to extract the name and content
    name_pattern = r'^(.*?)\n'  # Extract the first name from the content
    post_content_pattern = r'Follow\n(.*)'  # Extract content after 'Follow'
    
    # Split post content into lines
    lines = post_content.strip().split('\n')

    # Check if the last line is 'reposts', if so, remove the last 3 lines, otherwise remove the last 2 lines
    if lines[-1].strip().endswith('reposts'):
        cleaned_content_lines = lines[:-3]  # Remove last 3 lines
    else:
        cleaned_content_lines = lines[:-2]  # Remove last 2 lines
    
    cleaned_content = "\n".join(cleaned_content_lines).strip()

    # Apply patterns to extract name and post content
    name = re.search(name_pattern, cleaned_content).group(1) if re.search(name_pattern, cleaned_content) else 'N/A'
    main_content = re.search(post_content_pattern, cleaned_content, re.DOTALL).group(1).strip() if re.search(post_content_pattern, cleaned_content, re.DOTALL) else 'N/A'

    return {
        "Name": name,
        "Post_Content": main_content
    }

# Read the raw data from CSV
input_file = 'D:\Learning\linkedin job post data extrackter\linkedin_posts_with_links_v1.csv'  # Your file with raw post data
output_file = 'cleaned_linkedin_posts_with_links_v1.csv'

with open(input_file, mode='r', encoding='utf-8') as infile, open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)

    # Write headers for cleaned data
    writer.writerow(['Name', 'Post_Content', 'Post_Link'])

    # Process each post and clean it
    for row in reader:
        cleaned_data = clean_post_content(row['Post_Content'])
        writer.writerow([cleaned_data['Name'], cleaned_data['Post_Content'], row['Post_Link']])

print("Data cleaned and saved successfully.")
