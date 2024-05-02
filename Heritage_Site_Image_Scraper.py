import os
import json
import requests
from bs4 import BeautifulSoup

# Step 1: Read the JSON file and extract the image_link from each dictionary
json_file_path = "/Applications/Python 3.11/DLforNLP/working/world_heritage_sites_final.json"

with open(json_file_path, 'r') as file:
    data = json.load(file)

# Create a directory for storing downloaded images if it doesn't exist
download_directory = "Final_heritage_image_downloads"
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Process each item in the JSON file
for item in data:
    image_link = item['image_link']
    title = item['title']

    # Step 2: Fetch the webpage source using Alphabet Soup (BeautifulSoup)
    response = requests.get(image_link)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Step 3: Find the first <meta property="og:image" tag within the <head> tag
    og_image_tag = soup.head.find('meta', attrs={'property': 'og:image'})

    if og_image_tag:
        # Step 4: Extract the content attribute of the first og:image tag
        content_link = og_image_tag.get('content')

        # Image URL
        image_url = content_link

        # Set headers with a user-agent to avoid access errors
        headers = {'User-Agent': 'My Script 1.0'}

        # Send a GET request with streaming enabled
        response = requests.get(image_url, stream=True, headers=headers)

        # Check for successful response
        if response.status_code == 200:
            # Get the filename from the URL
            filename = title + ".jpg"

            # Path for storing the image
            filepath = os.path.join(download_directory, filename)

            # Open the file for writing in binary mode
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    # Write downloaded content chunk by chunk
                    f.write(chunk)

            print(f"Image downloaded successfully: {filename}")
        else:
            print(f"Error downloading image for {title}: {response.status_code}")
    else:
        print(f"No og:image tag found for {title} in the <head> section.")
