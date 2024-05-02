import requests
from bs4 import BeautifulSoup
import json
import re  # Import the regular expression module
import html  # Import the HTML module for decoding HTML entities

# URL of the Wikipedia page
url = "https://en.wikipedia.org/wiki/List_of_World_Heritage_Sites_in_India"

# Send a GET request to the URL
response = requests.get(url)

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, 'html.parser')

# Find all tables with class "wikitable sortable plainrowheaders"
tables = soup.find_all('table', {'class': 'wikitable sortable plainrowheaders'})

# List to store all rows from both tables
rows_list = []

# Define a regular expression pattern to match citating brackets
pattern = r'\[\d+\]'

# Define characters to be replaced with a space
characters_to_replace = [r'\u00a0', r'\u00e2', r'\u2013']

# Loop through each table
for table in tables:
    # Find the tbody section within the table
    tbody = table.find('tbody')
    # Find all tr tags within the tbody
    rows = tbody.find_all('tr')
    # Loop through each row and append its content to the list
    for index, row in enumerate(rows):
        if index != 0:  # Skip the first row
            # Extract the title and link from the <th> tag
            th_tag = row.find('th', {'scope': 'row'})
            title = th_tag.get_text(strip=True)
            link = th_tag.find('a')['href'] if th_tag.find('a') else None
            # Modify the link if it's a relative URL
            if link and not link.startswith('http'):
                link = 'https://en.wikipedia.org' + link
            # Extract the alt attribute from the <img> tag within the first <td> tag
            img_tag = row.find('td').find('img')
            alt = img_tag.get('alt') if img_tag else None
            #Extract the src attribute from the <img> tag within the first <td> tag
            src = img_tag.get('src') if img_tag else None
            #Extract the image link
            a_tag = row.find('td').find('a')
            image_link = a_tag['href'] if a_tag else None
            #Check if the image link is a relative URL
            if image_link and not image_link.startswith('http'):
                #Add the appropriate prefix (https://) to the relative URL
                image_link = 'https://en.wikipedia.org' + image_link
            #Extract the state title from the <a> tag within the second <td> tag
            state_tag = row.find_all('td')[1].find('a')
            state = state_tag['title'] if state_tag else None
            # Extract the year from the third <td> tag
            year = row.find_all('td')[2].get_text(strip=True) if row.find_all('td')[2] else None
            # Extract the UNESCO Data from the fourth <td> tag
            unesco_data = row.find_all('td')[3].get_text(strip=True) if row.find_all('td')[3] else None
            # Extract the description from the fifth <td> tag
            description_parts = []
            for elem in row.find_all('td')[4].contents:
                # Exclude text within square brackets with numbers
                if elem.name == 'a':  # If it's a link, extract its text
                    description_parts.append(elem.get_text(strip=True))
                elif isinstance(elem, str):  # If it's a string
                    # Decode HTML entities and remove citating brackets
                    text = re.sub(pattern, '', html.unescape(elem))
                    # Replace non-breaking space with regular space
                    for char in characters_to_replace:
                        text = text.replace(char, ' ')
                    description_parts.append(text.strip())
            # Concatenate the parts with spaces
            description = ' '.join(description_parts)
            # Store the extracted information in a dictionary
            row_dict = {'title': title, 'link': link, 'alt': alt, 'src': src, 'image_link': image_link, 'state': state, 'year': year, 'unesco_data': unesco_data, 'description': description}
            #row_dict = {'title': title, 'alt': alt, 'state': state, 'year': year, 'unesco_data': unesco_data, 'description': description}

            # Append the dictionary to the list
            rows_list.append(row_dict)

# Write the list of dictionaries to a JSON file
with open('world_heritage_sites_final.json', 'w') as json_file:
    json.dump(rows_list, json_file, indent=4)

print("JSON file has been created successfully.")
