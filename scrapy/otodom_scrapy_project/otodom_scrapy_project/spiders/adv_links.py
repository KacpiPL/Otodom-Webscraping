import scrapy
from scrapy_splash import SplashRequest
import json
import logging

# script to take links to advertisements from otodom.pl

# max_100 = True

class Link(scrapy.Item):
    link = scrapy.Field()

class otodom_links(scrapy.Spider):

    name = 'adv_links'
    allowed_domains = ['www.otodom.pl/']
    download_delay = 3
    max_100 = False

    # lua_script is a script to scroll down the page to load the whole content
    # We need to scroll down the page to load the script with links to the single adv pages
    # Lua script for scrolling taken form the documentation of scrapy-splash
    # https://scrapeops.io/python-scrapy-playbook/scrapy-splash/#3-scrolling-the-page

    # set_parameters (for technical description please see the code in the folder soup)
    def set_parameters(self):
        if self.max_100:
            n_pages = 2
            n = 100
        else:
            n_pages = 1
            n = 24
        return n_pages, n

    def start_requests(self):
        self.n_pages, self.n = self.set_parameters()

        lua_script = """
        function main(splash)
            local num_scrolls = 10
            local scroll_delay = 1.0

            local scroll_to = splash:jsfunc("window.scrollTo")
            local get_body_height = splash:jsfunc(
                "function() {return document.body.scrollHeight;}"
            )
            assert(splash:go(splash.args.url))
            splash:wait(splash.args.wait)

            for _ = 1, num_scrolls do
                scroll_to(0, get_body_height())
                splash:wait(scroll_delay)
            end        
            return splash:html()
        end """
        
        for i in range(1, self.n_pages + 1):
            url = 'https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa/mokotow?distanceRadius=0&locations=%5Bdistricts_6-39%5D&viewType=listing&page=' + str(i) +'&limit=24'
            
            yield SplashRequest(url, 
                                self.parse_links, 
                                endpoint='execute',
                                headers={"User-Agent": " Chrome/58.0.3029.110"},
                                args={'wait': 4, 'lua_source': lua_script}) 

    def parse_links(self, response):

        # create list with all links
        all_links = []

        # take static links to the single adv pages
        new_tags = response.xpath("//h2[contains(text(),'Wszystkie ogłoszenia')]/following-sibling::ul//li[@data-cy='listing-item']")

        new_tags_text = new_tags.getall()

        for tag in new_tags_text:
            link = tag.split('href="')[1].split('"')[0]
            link = 'https://www.otodom.pl' + link
            all_links.append(link)

        # take dynamic links to the single adv pages
        json_string = response.xpath('//meta[@content="noindex, follow"]/following-sibling::script[1]/text()').get()
        if json_string:  # if not None and not empty
            json_data = json.loads(json_string)
        else:
            self.log('No data found for url {}'.format(response.url), level=logging.WARNING)

        # We wrote the json data to the file to analyze the structure of the data
        # and write code to find urls to the single adv pages

        with open('data.json', 'w') as f:         
            json.dump(json_data, f)

        # # Below is the code to find urls to the single adv pages in the json data

        # # Find the Product object
        product_objects = [item for item in json_data['@graph'] if item['@type'] == 'Product']

        # Loop over each Product object
        for product in product_objects:
            # Check if "offers" key exists and it contains an "offers" key itself
            if 'offers' in product and 'offers' in product['offers']:
                # Loop over each Offer
                for offer in product['offers']['offers']:
                    # Check if "url" key exists
                    if 'url' in offer:
                        url = offer['url']
                        l = Link()
                        l['link'] = url
                        all_links.append(url)
        
        # return list with all links
        for link in all_links[:self.n]:
            yield Link(link=link)

# scrapy crawl adv_links -o adv_links.csv