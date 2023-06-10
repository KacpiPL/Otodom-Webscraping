# Webscraping otodom.pl with selenium only
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

# Boolean variable to take 100 advs or all advs
# is defined in the main function at the and of the code

# This code is written after the code otodom-soup-selenium which uses both Seleniun and BeautifulSoup (in folder soup)
# so we highly recommend to read the code from the folder soup first to have the full picture
# This code here does not use BeautifulSoup at all, only selenium

# Most of the functions are the same, 
# The whole part with preliminary links is the same, so we have not commented it (see the code in the folder soup)

# However there were some changes, for example:
## In the function take_adv_links we do not need to add 'https://www.otodom.pl' like in the version with BeautifulSoup
## In the function find_all_properties_all_attributes we do not need to define 2 functions for finding one attribute
## so instead of having find_property_one_attribute_1 and find_property_one_attribute_2 
## we have only find_property_one_attribute which takes xpath as an argument
## xpath is defined in the dictionary in the function find_all_properties_all_attributes


################################################################################
#  This part prepares preliminary links - links for lists of links
################################################################################

# initiate_driver (for technical description please see the code in the folder soup)
def initiate_driver(gecko_path):
    ser = Service(gecko_path)
    options = webdriver.firefox.options.Options()
    options.headless = False
    driver = webdriver.Firefox(options = options, service=ser)
    return driver

# take_adv_links (for technical description please see the code in the folder soup)
# here we changed just the line with new_tags
# we used find_elements by xpath instead of find by tag name from the version with BeautifulSoup
def take_adv_links(driver, url):
    link_temp_list = []
    driver.get(url)
    body = driver.find_element(By.TAG_NAME, 'body')
    tags = []

    while True:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)

        new_tags = driver.find_elements(By.XPATH, "//h2[contains(text(),'Wszystkie ogłoszenia')]/following-sibling::ul//li[@data-cy='listing-item']")

        if len(new_tags) > len(tags):
            tags = new_tags
        else:
            break

    for tag in tags:
        a_tag = tag.find_element(By.TAG_NAME, 'a')
        url = a_tag.get_attribute('href')               # in this case we do not need to add ''https://www.otodom.pl' like in the version with BeautifulSoup
        link_temp_list.append(url)

    return link_temp_list

# take_all_adv_links
## function to take all links to the single adv pages
## iterates over the result pages
## i set in range(1, n_pages+1) to take exactly n_pages
## returns n links to the single adv pages

## in this code we added here the driver as an argument
## because we will use it in the next function
## driver will be initiated and closed in the main function

## arguments:
### driver - driver
### n_pages - number of pages with results
### n - number of links to the single adv pages that we want to take

## returns:
### list of all links to the single adv pages

def take_all_adv_links(driver, n_pages, n):
    links = []
    for i in range(1, n_pages + 1):
        link_temp_list = []
        url = 'https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa/mokotow?distanceRadius=0&locations=%5Bdistricts_6-39%5D&viewType=listing&page=' + str(i) + '&limit=24'
        link_temp_list = take_adv_links(driver, url)
        links.extend(link_temp_list)

    # in this case we do not need to quit driver at the end of that function, beacause we will use it in the next function
    return links[:n]

################################################################################
# This part scraps data from single adv page
################################################################################

# find_property_one_attribute
## function to find one attribute of the property
## basing on the xpath

## arguments:
### driver - driver
### xpath - xpath of the attribute

## returns:
### attribute of the property

# In this code we do not need to define 2 functions for finding one attribute
def find_property_one_attribute(driver, xpath):
    try:
        return driver.find_element(By.XPATH, xpath).text
    except:
        return ''

# find_all_properties_all_attributes
## function to find all attributes of all properties
## and append them to a all_properties_all_attributes dataframe

## arguments:
### driver - driver
### links - list of links to the single adv pages

## returns:
### all_properties_all_attributes dataframe

def find_all_properties_all_attributes(driver, links):
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
    
    xpaths = {
    'price': "//strong[@aria-label='Cena']",
    'location': "//a[@aria-label='Adres']",
    'price_m2': "//div[@aria-label='Cena za metr kwadratowy']",
    'area': "//div[text()='Powierzchnia']/following::div[1]",
    'property_from': "//div[text()='Forma własności']/following::div[1]",
    'room_no': "//div[text()='Liczba pokoi']/following::div[1]",
    'finish_condition': "//div[text()='Stan wykończenia']/following::div[1]",
    'balcony_garden_terrace': "//div[text()='Balkon / ogród / taras']/following::div[1]",
    'rent': "//div[text()='Czynsz']/following::div[1]",
    'parking_place': "//div[text()='Miejsce parkingowe']/following::div[1]",
    'heating': "//div[text()='Ogrzewanie']/following::div[1]"
    }

    for link in links:
        driver.get(link)
        #time.sleep(1)       # we tested both versions with and without time.sleep() and it seems that it is not necessary to use it
        property_attributes = {attr: find_property_one_attribute(driver, xpath) for attr, xpath in xpaths.items()}
        df = df._append(property_attributes, ignore_index = True)

    return df

# set_parameters (for technical description please see the code in the folder soup)
def set_parameters(max_100):
    if max_100:
        n_pages = 2
        n = 100
    else:
        n_pages = 1
        n = 24
    return n_pages, n

def main():
    start_time = time.time()
    max_100 = False                      # if False please adjust parameters in the function set_parameters !!!
    gecko_path = '/opt/homebrew/bin/geckodriver'

    n_pages, n = set_parameters(max_100)
    driver = initiate_driver(gecko_path)
    links = take_all_adv_links(driver, n_pages, n)
    df = find_all_properties_all_attributes(driver, links)

    driver.quit()
    df.to_csv('data_selenium.csv', index = False, encoding = 'utf-8-sig')
    end_time = time.time()
    execution_time = end_time - start_time 
    print(f"Script execution time: {execution_time} seconds")
main()