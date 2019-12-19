#!/usr/bin/env python3

"""
Generate a schedule for turning APs in a building on and off
"""

from argparse import ArgumentParser

def schedule_building(name, data):
    floors = list(data.keys())

    complete_floors = set()
    even = True
    last = []
    while len(floors) != len(complete_floors):
        if even:
            floors_to_schedule = floors[::2]
        else:
            floors_to_schedule = floors[1::2]
        aps = []
        for floor in floors_to_schedule:
            if not data[floor]:
                complete_floors.add(floor)
            else:
                aps.append(data[floor].pop())
        if aps:
            print({"on": last, "off" : aps})
            last = aps
        even = not even
    print({"on": last, "off" : []})

def main():
    # Parse arguments
    arg_parser = ArgumentParser(description='Generate on/off schedule')
    arg_parser.add_argument('-a', '--aps', action='store', required=True, 
            help='File containing AP dictionary')
    settings = arg_parser.parse_args()

    with open(settings.aps, 'r') as aps_file:
        buildings = eval(aps_file.read())

    for name, data in buildings.items():
        schedule_building(name, data)

if __name__ == '__main__':
    main()
