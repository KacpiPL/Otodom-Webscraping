# Webscraping otodom.pl with selenium and beautifulsoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup as BS
from selenium.webdriver.common.keys import Keys
import time
from urllib import request
import pandas as pd

# Boolean variable to take 100 advs or all advs
# is defined in the main function at the and of the code

# Unfortunately the page occured to be dynamic, so we had to use selenium
# to scroll down the page to the bottom to load all the data
# and then use beautifulsoup to parse the data.

################################################################################
#  This part prepares preliminary links - links for lists of links
################################################################################

# initiate_driver
## function to initiate driver
## argument - path to geckodriver
## returns - driver object

def initiate_driver(gecko_path):
    ser = Service(gecko_path)
    options = webdriver.firefox.options.Options()
    options.headless = False
    driver = webdriver.Firefox(options = options, service=ser)
    return driver

# take_adv_links 
## function to take links to the single adv pages
## takes all links from the page with results

## arguments:
### driver - driver object
### url - url to the page with list of links (with lists of advs)

## returns:
### link_temp_list - list of links to the single adv pages from one page with results

# There are 2 divs with 2 ul lists:
## search.listing.promoted - for promoted adv
## search.listing.organic - for "usual" adv
## we decided to take only "usual" adv ("Wszytskie ogłoszenia")

def take_adv_links(driver, url):
    link_temp_list = []

    driver.get(url)

    body = driver.find_element(By.TAG_NAME, 'body')
    tags = []

    while True:
        body.send_keys(Keys.PAGE_DOWN)          # Scroll down the page to the bottom.  
        time.sleep(2)                           # Adjust sleep time as needed to allow the page to load.

        new_content = driver.page_source
        new_bs = BS(new_content, features = 'html.parser')
        new_tags = new_bs.find('h2', text="Wszystkie ogłoszenia").find_next('ul').find_all('li', {'data-cy': 'listing-item'})

        if len(new_tags) > len(tags):
            tags = new_tags
        else:
            break

    for tag in tags:
        a_tag = tag.find_next('a')
        if a_tag is not None:
            url = 'https://www.otodom.pl' + a_tag['href']
            link_temp_list.append(url)
    
    return link_temp_list

# take_all_adv_links
## function to take all links to the single adv pages
## iterates over the result pages
## i set in range(1, n_pages+1) to take exactly n_pages
## returns n links to the single adv pages

## arguments:
### n_pages - number of pages with results
### n - number of links to the single adv pages that we want to take

## returns:
### list of all links to the single adv pages

# In the url we provide link with selected "Mokotów" as district
# We changed the number of shown results at one page to the max number (72) (parameter limit=72) to reduce the number of iterations
# In case of not changing the number we should iterate over the result pages more times to obtain required number of results

def take_all_adv_links(n_pages, n):
    gecko_path = '/opt/homebrew/bin/geckodriver'
    links = []
    driver = initiate_driver(gecko_path)
    
    for i in range(1, n_pages + 1):
        link_temp_list = []
        url = 'https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa/mokotow?distanceRadius=0&locations=%5Bdistricts_6-39%5D&viewType=listing&page=' + str(i) + '&limit=24'
        link_temp_list = take_adv_links(driver, url)
        links.extend(link_temp_list)
        
    driver.quit()
    return links[:n]

################################################################################
# This part scraps data from single adv page
################################################################################

# find_property_one_attribute_1
## 3 attributes has very similiar structure to find it
## the difference is in name of string and tag which to find
## function to find them

## arguments:
### bs - BeautifulSoup object of html
### tag - tag which to find

## returns:
### text of the tag

def find_property_one_attribute_1(bs, tag, search_dict):
    try:
        return bs.find(tag, search_dict).text
    except:
        return ''

# find_property_one_attribute_2
## 8 attributes has the same structure to find it, the difference is in name of string
## function to find them

## arguments:
### bs - BeautifulSoup object of html
### attribute_name - name of the attribute that we want to find

## returns:
### text of the tag

def find_property_one_attribute_2(bs, attribute_name):
    try:
        return bs.find('div', string = attribute_name).find_next('div').find_next('div').text
    except:
        return ''

# find_property_all_attributes
## function to find all attributes that we need from single page

## arguments:
### url - url to the page that we want to scrape

## returns:
### property_attributes - dict with all attributes that we need

def find_property_all_attributes(url, attributes_1, attributes_2):
    html = request.urlopen(url)
    bs = BS(html.read(), 'html.parser')

    # names of teh property/info that has the same path to find and its map to english names which will be used
    property_attributes = {}

    # find the first 3 attributes and assign them to property_attributes dict
    for attribute, (tag, search_dict) in attributes_1.items():
        property_attributes[attribute] = find_property_one_attribute_1(bs, tag, search_dict)

    # find the reamining 8 attributes and assign them to property_attributes dict
    for english_name, original_name in attributes_2.items():
        property_attributes[english_name] = find_property_one_attribute_2(bs, original_name)

    return property_attributes

# find_all_properties_all_attributes
## function to find all attributes of all properties
## and append them to a all_properties_all_attributes dataframe

## arguments:
### links - list of links to the webpage with adv which we want to scrape

## returns:
### df - dataframe with all attributes of all properties

def find_all_properties_all_attributes(links):
    df = pd.DataFrame({'price': [],
                        'location':[],
                        'price_m2':[],
                        'area':[], 
                        'property_from':[], 
                        'room_no':[], 
                        'finish_condition':[],
                        'balcony_garden_terrace':[], 
                        'rent':[], 
                        'parking_place':[], 
                        'heating':[], })
    
    # define the first 3 attributes and their location on the page
    # for the purpose of function find_property_one_attribute_1
    attributes_1 = {
    'price': ('strong', {'aria-label': 'Cena'}),
    'location': ('a', {'aria-label': 'Adres'}),
    'price_m2': ('div', {'aria-label': 'Cena za metr kwadratowy'})
    }

    # define the remaining 8 attributes
    # for the purpose of function find_property_one_attribute_2
    attributes_2 = {
        'area': 'Powierzchnia',
        'property_from': 'Forma własności',
        'room_no': 'Liczba pokoi',
        'finish_condition': 'Stan wykończenia',
        'balcony_garden_terrace': 'Balkon / ogród / taras',
        'rent': 'Czynsz',
        'parking_place': 'Miejsce parkingowe',
        'heating': 'Ogrzewanie'
    }

    for link in links:
        property_attributes = find_property_all_attributes(link, attributes_1, attributes_2)
        df = df._append(property_attributes, ignore_index = True)

    return df

# set_parameters
## function to set parameters of the scraping

## arguments:
### max_100 - boolean value, 
#       if True we want to take 100 results, 
#       if False we want to take other value of results (then the parameters should be adjusted !!!)

# returns:
### n_pages - number of pages to iterate over
### n - number of results to take

def set_parameters(max_100):
    if max_100:
        n_pages = 2         # number of pages to iterate over, 2 because we want to take 100 results
        n = 100             # number of results to take
    else:
        n_pages = 1       # some big number of pages to iterate over
        n = 24            # max number of results from that number of pages (100 * 72)
    return n_pages, n

def main():
    start_time = time.time()
    
    max_100 = True          # if False please adjust parameters in the function set_parameters !!!
    n_pages, n = set_parameters(max_100)
    links = take_all_adv_links(n_pages, n)
    df = find_all_properties_all_attributes(links)
    df.to_csv('data.csv', index = False, encoding = 'utf-8-sig')

    end_time = time.time()
    execution_time = end_time - start_time 
    print(f"Script execution time: {execution_time} seconds")
main()