#  AUTHOR: Brad Atkinson
#    DATE: 7/29/2021
# PURPOSE: Configuration file info containing username, password, and IPs

# CONNECTIVITY CONFIGURATIONS
# Update the panorama_ip section with the primary and secondary Panorama 
# IP addresses.

paloalto = {
    'username': '<USERNAME>',
    'password': '<PASSWORD>',
    'key': '<API_KEY>',
    'panorama_ip': ['<IP_ADDRESS1>', '<IP_ADDRESS2>']
    }

# CSV FILENAME AND PATH
# Update with the path and filename for the CSV file

filename = '<PATH_AND_FILENAME>.csv'