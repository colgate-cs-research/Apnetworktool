#!/usr/bin/env python3

"""
Run a schedule for turning APs in a building on and off
"""

from argparse import ArgumentParser
import logging
import time
import paramiko

def handle_event(event, auth):
    logging.info("Handling event: %s" % (event))
    client = paramiko.client.SSHClient()
    client.load_system_host_keys()
    client.connect(hostname=auth['hostname'], username=auth['username'], 
            password=auth['password'])
    commands = []
    for group,aps in event.items():
        for ap in aps:
            commands.append('ap-regroup ap-name %s %s' % (ap, group))

    for command in commands:
        logging.info("Executing: %s" % command)
        stdin, stdout, stderr = client.exec_command(command)
        logging.info(stdout.read())
        logging.info(stderr.read())

    client.close()

def main():
    # Parse arguments
    arg_parser = ArgumentParser(description='Generate on/off schedule')
    arg_parser.add_argument('-s', '--schedule', action='store', required=True, 
            help='File containing a schedule')
    arg_parser.add_argument('-g', '--gap', action='store', required=True, 
            help='Gap between events')
    arg_parser.add_argument('-a', '--authentication', action='store', 
            required=True, help='File with authentication data')
    arg_parser.add_argument('-v', '--verbose', action='store_true', 
            help='Verbose output')
    settings = arg_parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(message)s', 
            level=(logging.INFO if settings.verbose else logging.WARNING))
    logging.info(settings)

    with open(settings.authentication, 'r') as auth_file:
        auth = eval(auth_file.read())
    logging.info("Loaded authentication data")

    gap = settings.gap
    if (gap[-1] == 's'):
        gap = int(gap[:-1])
    elif (gap[-1] == 'm'):
        gap = int(gap[:-1]) * 60
    else:
        raise "Gap must be in seconds (e.g., 20s) or minutes (e.g., 20m)"

    with open(settings.schedule, 'r') as schedule:
        for line in schedule:
            handle_event(eval(line), auth)
            time.sleep(gap)


if __name__ == '__main__':
    main()
