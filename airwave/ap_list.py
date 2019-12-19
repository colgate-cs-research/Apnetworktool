#!/usr/bin/env python3

"""
Extract a list of AP names from VisualRF Building XML
"""

from argparse import ArgumentParser
import xml.etree.ElementTree as ET

def process_building(building):
    data = {}
    name = building.attrib['name']
    sites = building.findall("site")
    for site in sites:
        floor, aps = process_site(site)
        data[floor] = aps
    return (name, data)

def process_site(site):
    floor = int(float(site.attrib['floor']))
    aps = site.findall("ap")
    names = [process_ap(ap) for ap in aps]
    names = list(filter(lambda name: name != "NETWORK SWITCHES" 
                and name != "", names))
    return (floor, names)

def process_ap(ap):
    return ap.attrib['name']

def main():
    # Parse arguments
    arg_parser = ArgumentParser(description='Extract AP names')
    arg_parser.add_argument('-x', '--xml', action='store', required=True, 
            help='Path to XML file')
    settings = arg_parser.parse_args()

    tree = ET.parse(settings.xml)
    buildings = tree.findall("./building")
    data = {}
    for building in buildings:
        name, floors = process_building(building)
        data[name] = floors

    print(data)

if __name__ == '__main__':
    main()
