#!/usr/bin/env python3

"""
Scrape heatmaps from Airwave
"""

from argparse import ArgumentParser
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time

def scrape(username, password, sites_csv):
    driver = webdriver.Chrome()

    # Allow for page load
    driver.implicitly_wait(10)

    # Open web page
    driver.get("https://airwave.colgate.edu/")
    driver.set_window_size(1851, 1036)

    # Login
    driver.find_element_by_id("login-username-id").send_keys(username)
    driver.find_element_by_id("login-password-id").send_keys(password)
    driver.find_element_by_id("login-password-id").send_keys(Keys.ENTER)
    print("Logged in")
    time.sleep(5)

    with open(sites_csv) as sites:
        for site in sites:
            site_id, building_name, floor_num = site.split(',')
            capture_heatmap(driver, site_id, building_name, int(floor_num))

    driver.quit()

def capture_heatmap(driver, site_id, building_name, floor_num):
    print("Capturing %s %d" % (building_name, floor_num))

    # Load heatmap
    driver.get("https://airwave.colgate.edu/vrf?site_id="+site_id)
    time.sleep(4)

    # Only show 5GHz coverage
    driver.find_element_by_id(
            'overlay_hm_checked').find_element_by_css_selector(
            '.vrf_visibility_arrow').click()
    driver.find_elements_by_css_selector(
            '.goog-checkbox')[1].click()
    time.sleep(8)

    # Save heatmap
    driver.save_screenshot('%s_f%d_5GHz.png' % (building_name, floor_num))

    # Only show 2.4GHz coverage
    driver.find_elements_by_css_selector(
            '.goog-checkbox')[1].click()
    driver.find_elements_by_css_selector(
            '.goog-checkbox')[0].click()
    time.sleep(8)

    # Save heatmap
    driver.save_screenshot('%s_f%d_2GHz.png' % (building_name, floor_num))

def main():
    # Parse arguments
    arg_parser = ArgumentParser(description='Scrape heatmaps from Airwave')
    arg_parser.add_argument('-u', '--username', dest='username', action='store',
            required=True, help='Airwave username')
    arg_parser.add_argument('-p', '--password', dest='password', action='store',
            required=True, help='Airwave password')
    arg_parser.add_argument('-s', '--sites', dest='sites', action='store',
            required=True, 
            help='CSV file of site IDs, building names, and floor numbers')
    settings = arg_parser.parse_args()

    # Scrape heatmaps
    scrape(settings.username, settings.password, settings.sites)

if __name__ == '__main__':
    main()
