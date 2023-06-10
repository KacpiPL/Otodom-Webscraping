import scrapy

# almost final code to take attributes from pages
# right now it takes just from one link
# add to take from css and to make all attributes

class adv(scrapy.Item):
    price = scrapy.Field()
    location = scrapy.Field()
    price_m2 = scrapy.Field()
    area = scrapy.Field()
    room_no = scrapy.Field()
    finish_condition = scrapy.Field()
    balcony_garden_terrace = scrapy.Field()
    rent = scrapy.Field()
    parking_place = scrapy.Field()
    heating = scrapy.Field()

class advSpider(scrapy.Spider):
    name = 'adv'
    allowed_domains = ['otodom.pl/']

    try:
        with open("adv_links.csv", "rt") as f:
            start_urls = [url.strip() for url in f.readlines()][1:]
    except:
        start_urls = []
   
    # We override request method to customize the headers of the requests. 
    # The "User-Agent" string is added to each request to mimic a request coming from a web browser (in this case, Google Chrome). 
    # This helps avoid blocks put in place by some websites against non-browser traffic.

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers={
                "User-Agent": " Chrome/58.0.3029.110"
                })

    # There is the issue with xpaths. The xpahs used in selenium does not work in scrapy.
    # In the last 8 variables to find there is a problem, beacuse if they are empty the structure of the page is different.
    
    # In normal case (if the variable is on the page) there is a div, but if it is not there is a button.
    # In this case we need to use different xpaths for the same variable.
    # In these cases we need to use longer xpath with or operator to handle both cases.

    # At the beginning we tried to use ".../*[1]..." xpath but it didnt work always.

    def parse(self, response):
        a = adv()

        price_xpath = "//strong[@aria-label='Cena']/text()"
        location_xpath = "//a[@aria-label='Adres']/text()"
        price_m2_xpath = "//div[@aria-label='Cena za metr kwadratowy']/text()"

        area_xpath = "//div[text()='Powierzchnia']/following::div[1]/div[1]/text() | //div[text()='Powierzchnia']/following::div[1]/button[1]/text()"
        room_no_xpath = "//div[text()='Liczba pokoi']/following::div[1]/div[1]/text() | //div[text()='Liczba pokoi']/following::div[1]/button[1]/text()"
        finish_condition_xpath = "//div[text()='Stan wykończenia']/following::div[1]/div[1]/text() | //div[text()='Stan wykończenia']/following::div[1]/button[1]/text()"
        balcony_garden_terrace_xpath = "//div[text()='Balkon / ogród / taras']/following::div[1]/div[1]/text() | //div[text()='Balkon / ogród / taras']/following::div[1]/button[1]/text()"
        rent_xpath = "//div[text()='Czynsz']/following::div[1]/div[1]/text() | //div[text()='Czynsz']/following::div[1]/button[1]/text()"
        parking_place_xpath = "//div[text()='Miejsce parkingowe']/following::div[1]/div[1]/text() | //div[text()='Miejsce parkingowe']/following::div[1]/button[1]/text()"
        heating_xpath = "//div[text()='Ogrzewanie']/following::div[1]/div[1]/text() | //div[text()='Ogrzewanie']/following::div[1]/button[1]/text()"

        a['price'] = response.xpath(price_xpath).get()
        a['location'] = response.xpath(location_xpath).get()
        a['price_m2'] = response.xpath(price_m2_xpath).get()
        a['area'] = response.xpath(area_xpath).get()
        a['room_no'] = response.xpath(room_no_xpath).get()
        a['finish_condition'] = response.xpath(finish_condition_xpath).get()
        a['balcony_garden_terrace'] = response.xpath(balcony_garden_terrace_xpath).get()
        a['rent'] = response.xpath(rent_xpath).get()
        a['parking_place'] = response.xpath(parking_place_xpath).get()
        a['heating'] = response.xpath(heating_xpath).get()

        yield a

# scrapy crawl adv -o adv_attr.csv