# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MaguroItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class GladpostItem(scrapy.Item):
    url = scrapy.Field()
    image_url = scrapy.Field()
    age = scrapy.Field()
    height = scrapy.Field()
    style = scrapy.Field()
    looks = scrapy.Field()
    job = scrapy.Field()
    area = scrapy.Field()
    device = scrapy.Field()
    bwhc = scrapy.Field()
    ideal_age = scrapy.Field()
    ideal_style = scrapy.Field()
    relationship = scrapy.Field()
    has_kids = scrapy.Field()
    cigar = scrapy.Field()
    alcohol = scrapy.Field()
    has_cars = scrapy.Field()
    blood_type = scrapy.Field()
    constellation = scrapy.Field()
