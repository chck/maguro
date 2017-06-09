# -*- coding: utf-8 -*-

import scrapy
from bs4 import BeautifulSoup
from maguro.items import GladpostItem

UID = 'YOUR_UID'
TEL = 'YOUR_TEL_NUMBER'
PW = 'YOUR_PASSWORD'


class GladpostSpider(scrapy.Spider):
    name = 'gladpost'
    allowed_domains = ['happymail.co.jp']
    start_urls = ['http://happymail.co.jp/']

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'TelNo': TEL, 'Pass_x': PW},
            callback=self.pass_index_after_login
        )

    def pass_index_after_login(self, response):
        return scrapy.Request(
            '{}?UID={}'.format(self._url('mbmenu.php'), UID),
            callback=self.pass_image_page
        )

    def pass_image_page(self, response):
        return scrapy.Request(
            '{}?UID={}'.format(self._url('srchpic.php'), UID),
            callback=self.parse_images
        )

    def parse_images(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={
                'SelArea': '14',  # in Tokyo only
                'UID': UID,
                'Pg': 'LST',

            },
            callback=self.parse_pages,
            method='POST',
            url=self._url('srchpic.php')
        )

    def parse_pages(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        for profile in soup.find('div', align='center').table.find_all('a'):
            yield scrapy.Request(self._url(profile['href']), callback=self.parse_profiles)

        maybe_next_page = [tag for tag in soup.find_all('center') if '次へ>>' in tag.text]
        if not maybe_next_page:
            yield
        else:
            yield scrapy.Request(self._url(maybe_next_page[0].a['href']),
                                 callback=self.parse_pages)

    def parse_profiles(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        return GladpostItem(
            image_url=soup.find('img', style='max-width:300px;')['src']
        )

    def _url(self, path):
        return self.start_urls[0] + path