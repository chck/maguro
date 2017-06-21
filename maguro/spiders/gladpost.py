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

    def __init__(self, area_id=None, uid=UID, *args, **kwargs):
        super(GladpostSpider, self).__init__(*args, **kwargs)
        self.area_id = area_id
        self.uid = uid

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'TelNo': TEL, 'Pass_x': PW},
            callback=self.pass_index_after_login
        )

    def pass_index_after_login(self, response):
        return scrapy.Request(
            '{}?UID={}'.format(self._url('mbmenu.php'), self.uid),
            callback=self.pass_image_page
        )

    def pass_image_page(self, response):
        return scrapy.Request(
            '{}?UID={}'.format(self._url('srchpic.php'), self.uid),
            callback=self.parse_images
        )

    def parse_images(self, response):
        def _pass_to_parse_pages(area_id):
            return scrapy.FormRequest.from_response(
                response,
                formdata={
                    'SelArea': area_id,
                    'UID': self.uid,
                    'Pg': 'LST',
                },
                callback=self.parse_pages,
                method='POST',
                url=self._url('srchpic.php')
            )

        if self.area_id:
            yield _pass_to_parse_pages(self.area_id)
        else:
            soup = BeautifulSoup(response.body, 'lxml')
            for option in soup.find('select').find_all('option'):
                yield _pass_to_parse_pages(area_id=option['value'])

    def parse_pages(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        for profile in soup.find('div', align='center').table.find_all('a'):
            yield scrapy.Request(self._url(profile['href']), callback=self.parse_profiles)

        maybe_next_page = [tag for tag in soup.find_all('center') if '次へ>>'.decode('utf-8') in tag.text]
        if not maybe_next_page:
            yield
        else:
            maybe_next_page = [a for a in maybe_next_page[0].find_all('a') if a.text == '>>']
            yield scrapy.Request(self._url(maybe_next_page[0]['href']),
                                 callback=self.parse_pages)

    def parse_profiles(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        profile = [p for p in soup.find_all('td', align='left')[-1].text.split('\n') if p]
        profile[6] = profile[6].split('3ｻｲｽﾞ'.decode('utf-8'))
        profile = list(self._flatten(profile))[:-1]
        profile = list(self._flatten([p.split(':')[1:] for p in profile]))
        return GladpostItem(url=response.url,
                            image_url=soup.find('img', style='max-width:300px;')['src'],
                            age=profile[0],
                            height=profile[1],
                            style=profile[2],
                            looks=profile[3],
                            job=profile[4],
                            area=profile[5],
                            device=profile[6],
                            bwhc=profile[7],
                            ideal_age=profile[8],
                            ideal_style=profile[9],
                            relationship=profile[10],
                            has_kids=profile[11],
                            cigar=profile[12],
                            alcohol=profile[13],
                            has_cars=profile[14],
                            blood_type=profile[15],
                            constellation=profile[16])

    def _url(self, path):
        return self.start_urls[0] + path

    def _flatten(self, container):
        """string friendly flatten
        https://stackoverflow.com/questions/10823877/what-is-the-fastest-way-to-flatten-arbitrarily-nested-lists-in-python
        https://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists
        """
        for i in container:
            if isinstance(i, (list, tuple)):
                for j in self._flatten(i):
                    yield j
            else:
                yield i
