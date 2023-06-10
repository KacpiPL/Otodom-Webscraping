# Otodom-Webscraping

Welcome to the Otodom Web Scraper project! 

This project is a simple and efficient web scraping tool built in Python, intended to collect and analyze real estate data from the Polish website Otodom.

# Project Overview

Otodom Web Scraper is designed to fetch details about real estate properties listed on Otodom. These details include property type, location, price, size, number of rooms, and other related attributes. This data can be valuable for various purposes, such as market analysis, predictive modeling, real estate investment decision-making, etc.

# Features

Extract the basic data about properties about real estate ads on the otodom portal by using three main scraping method:
1. BeautifulSoup (with elements of Selenium)
2. Scrapy Splash
3. Selenium

# How to run scrapers

1. Please make sure that you have all the packages that are required at the beginning of each code.
2. Provide the link to the district/city in which you want to search for ads information (default is set to Mokotów, Warsaw).
3. If you want to change the default number of pages scraped change the parameter 'max_100' to False and adjust the number in the 'set_parameters' function
4. In case of soup and selenium the only thing that you need to do is just to run the code and see the results.
5. In case of scrapy code you need to install docker and scrapy splash. We recommend that link: https://scrapeops.io/python-scrapy-playbook/scrapy-splash/#:~:text=Developed%20by%20Zyte%20

# More information

We highly encourage you to visit these two links with more detailed project description and the video about the project.

Project description:
https://docs.google.com/document/d/1heuF9IohXwfP9D7f0DUv-n67t80vqeE-/edit?usp=sharing&ouid=111548730511906688514&rtpof=true&sd=true

Video:
https://drive.google.com/file/d/11-P4BQbYPCB9SbjrHOVmGnj6TKwz3pTF/view?usp=sharing
