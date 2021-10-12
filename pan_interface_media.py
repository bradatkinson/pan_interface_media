#!/usr/bin/env python3
#
#  AUTHOR: Brad Atkinson
#    DATE: 7/29/2021
# PURPOSE: To gather Palo Alto firewall interface media inventory

import re
import sys
from panos import base
import config


def find_active_device():
    """Find Active Device

    Returns:
        pano_ip (str): The IP address of the active Panorama
    """
    print('Finding the active Panorama...')
    pano1_ip = config.paloalto['panorama_ip'][0]
    pano1_conn = connect_device(pano1_ip)
    pano1_results = check_ha_status(pano1_conn)
    pano1_state = process_ha_status(pano1_results)

    pano2_ip = config.paloalto['panorama_ip'][1]
    pano2_conn = connect_device(pano2_ip)
    pano2_results = check_ha_status(pano2_conn)
    pano2_state = process_ha_status(pano2_results)

    active_tuple = ('active', 'active-primary', 'primary-active')
    if pano1_state in active_tuple:
        pano_ip = pano1_ip
        pano_conn = pano1_conn
    elif pano2_state in active_tuple:
        pano_ip = pano2_ip
        pano_conn = pano2_conn
    else:
        print("-- Couldn't find the active Panorama.\n", file=sys.stderr)
        sys.exit(1)

    pano_conn = connect_device(pano_ip)
    results = get_system_info(pano_conn)
    hostname = get_hostname(results)
    print('-- Connected to the active Panorama: {}\n'.format(hostname))
    return pano_conn


def check_ha_status(pano_conn):
    """Check HA Status

    Args:
        pano_conn (PanDevice): A panos object for device

    Returns:
        results (Element): XML results from firewall
    """
    command = ('<show><high-availability><state>'
               '</state></high-availability></show>')
    results = pano_conn.op(cmd=command, cmd_xml=False)
    return results


def process_ha_status(results):
    """Process HA Status

    Args:
        results (Element): XML results from firewall

    Returns:
        ha_status (str): A string containing the HA state
    """
    ha_status = results.find('./result/local-info/state').text
    return ha_status


def connect_device(device_ip):
    """Connect To Device

    Args:
        device_ip (str): A string containing the device IP address

    Returns:
        dev_conn (PanDevice): A panos object for device
    """
    username = config.paloalto['username']
    password = config.paloalto['password']
    try:
        dev_conn = base.PanDevice.create_from_device(
            hostname=device_ip,
            api_username=username,
            api_password=password)
        return dev_conn
    except:
        print('Host was unable to connect to device. Please check '
              'connectivity to {}.\n'.format(device_ip), file=sys.stderr)


def get_system_info(pano_conn):
    """Get Show System Info

    Args:
        pano_conn (PanDevice): A panos object for device

    Returns:
        results (Element): XML results from firewall
    """
    results = pano_conn.op(cmd='show system info')
    return results


def get_hostname(results):
    """Get Hostname

    Args:
        results (Element): XML results from firewall

    Returns:
        hostname (str): A string containing the hostname
    """
    hostname = results.find('./result/system/hostname').text
    return hostname


def get_connected_devices(pano_conn):
    """Get Connected Devices

    Args:
        pano_conn (PanDevice): A panos object for device

    Returns:
        results (Element): XML results from firewall
    """
    command = '<show><devices><connected></connected></devices></show>'
    results = pano_conn.op(cmd=command, cmd_xml=False)
    return results


def process_connected_devices(results):
    """Process Connected Devices

    Args:
        results (Element): XML results from firewall

    Returns:
        devices_dict (dict): A dictionary containing hostnames, IP addresses, and models
    """
    xml_list = results.findall('./result/devices/entry')
    devices_dict = {}
    for device in xml_list:
        hostname = device.find('./hostname').text
        serial = device.find('./serial').text
        ip_address = device.find('./ip-address').text
        model = device.find('./model').text
        devices_dict[serial] = {'hostname': hostname, 'ip_address': ip_address, 'model': model}
    return devices_dict



def gather_media_info(fw_conn, model, hostname):
    """Gather Media Info

    Args:
        fw_conn (PanDevice): A panos object for device
        model (str): A string containing the model number of the device
        hostname (str): A string containing the hostname
    """
    if model == 'PA-7050' or model == 'PA-7080':
        total_ports = 28
    elif model == 'PA-5220' or model == 'PA-5250' or model == 'PA-5260' or model == 'PA-5280':
        total_ports = 24
    elif model == 'PA-3220' or model == 'PA-3250':
        total_ports = 20
    elif model == 'PA-3260':
        total_ports = 24
    elif model == 'PA-820' or model == 'PA-850':
        total_ports = 12
    else:
        total_ports = 8

    port = 1
    while port <= total_ports:
        results = get_interface_info(fw_conn, port)
        process_interface_info(results, hostname, fw_conn)
        port += 1


def get_interface_info(fw_conn, port):
    """Get Interface Info

    Args:
        fw_conn (PanDevice): A panos object for device
        port (int): An integer of the port number of an interface

    Returns:
        results (Element): XML results from firewall
    """
    command = '<show><system><state><filter>sys.s1.p' + str(port) + '.phy</filter></state></system></show>'
    results = fw_conn.op(cmd=command, cmd_xml=False)
    return results


def process_interface_info(results, hostname, fw_conn):
    """Process Interface Info

    Args:
        results (Element): XML results from firewall
        hostname (str): A string containing the hostname
        fw_conn (PanDevice): A panos object for device
    """
    results_info = results.find('./result').text
    print(results_info)
    
    media_info = re.search(r"(sys\.s[0-9]\.p[0-9]*\.phy): { 'link-partner': { }, 'media': ([QSFP|SFP].*), 'sfp': { 'connector': ([A-Z].*), 'en.*'vendor-name': ([A-Z].*), 'vendor-part-number': ([A-Z0-9].*), 'vendor-part.*", results_info)

    if media_info is not None:
        write_data_to_csv_file(media_info, hostname, fw_conn)


def write_data_to_csv_file(media_info, hostname, fw_conn):
    """Write Data To CSV File

    Args:
        media_info (str): A string containing a regex match
        hostname (str): A string containing the hostname
        fw_conn (PanDevice): A panos object for device
    """
    slot_port_info = media_info.group(1)
    media = media_info.group(2)
    slot_port = re.search(r"sys\.s([0-9])\.p([0-9]*)\.phy", slot_port_info)
    media_slot = slot_port.group(1)
    media_port = slot_port.group(2)
    media_connector = media_info.group(3)
    media_vendor = media_info.group(4)
    media_vendor = media_vendor.strip()
    media_part = media_info.group(5)
    media_part = media_part.strip()

    interface_results = get_interface_state(fw_conn, media_port)
    state = process_interface_state(interface_results)

    media_file = open(config.filename, 'a')
    media_file.write('%s,%s,%s,%s,%s,%s,%s,%s\n' %(hostname,media,media_slot,media_port,media_connector,media_vendor,media_part,state))
    media_file.close()



def get_interface_state(fw_conn, port):
    """Get Interface State

    Args:
        fw_conn (PanDevice): A panos object for device
        port (int): An integer of the port number of an interface

    Returns:
        results (Element): XML results from firewall
    """
    command = '<show><interface>ethernet1/' + str(port) + '</interface></show>'
    results = fw_conn.op(cmd=command, cmd_xml=False)
    return results


def process_interface_state(results):
    """Process Interface State

    Args:
        results (Element): XML results from firewall

    Returns:
        state (str): A string containing the interface state
    """
    state = results.find('./result/hw/state').text
    return state 


def write_headers_to_csv_file():
    """Write Headers To CSV File
    """
    media_file = open(config.filename, 'a')
    media_file.write('Hostname,Media,Slot,Port,Connector,Vendor,Part #,State\n')
    media_file.close()


def main():
    """Function Calls
    """
    pano_conn = find_active_device()
    device_results = get_connected_devices(pano_conn)
    devices_dict = process_connected_devices(device_results)
    write_headers_to_csv_file()

    for device_dict in devices_dict.values():
        fw_ip = device_dict.get('ip_address')
        hostname = device_dict.get('hostname')
        model = device_dict.get('model')

        try:
            fw_conn = connect_device(fw_ip)
            print('\nConnected to {}'.format(hostname))
            gather_media_info(fw_conn, model, hostname)
        except:
            continue


if __name__ == '__main__':
    main()
