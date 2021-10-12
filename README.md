# pan_interface_media
A script to gather Palo Alto firewall interface media inventory

## Built With
 
[Palo Alto Networks PAN-OS SDK for Python](https://github.com/PaloAltoNetworks/pan-os-python)

## Deployment

All files within the folder should be deployed in the same directory for proper file execution.

## Prerequisites

Update `config.py` file with correct values before operating.

```
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
```

## Operating

From the CLI, change directory into the folder containing the files.  The following command will execute the script:

```bash
python pan_interface_media.py
```

## Example Output

```
Hostname,Media,Slot,Port,Connector,Vendor,Part #,State
fw1,SFP-Plus-Fiber,1,1,LC,FINISAR CORP.,FTLX1475D3BCL,up
fw1,SFP-Plus-Fiber,1,2,LC,FINISAR CORP.,FTLX1475D3BCL,up
fw2,SFP-Plus-Fiber,1,1,LC,FINISAR CORP.,FTLX1475D3BCL,up
fw2,SFP-Plus-Fiber,1,2,LC,FINISAR CORP.,FTLX1475D3BCL,up
```

See the [example_csv_file](example_palo_interface_media.csv) for an example of the output from the script.

## Changelog

See the [CHANGELOG](CHANGELOG) file for details