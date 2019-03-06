# -*- coding: utf-8 -*-
from scrapy import Spider, Selector, Request
from itunes.items import ItunesItem
import re


def get_id_from_url(url):
    """
    extract the itunes id from an url
    """
    g = re.search("id(\\d+)", url)
    return g.group(1)


class ItunesspiderSpider(Spider):
    name = "itunesSpider"
    allowed_domains = ["itunes.apple.com"]
    start_urls = (
      "https://itunes.apple.com/us/genre/podcasts-religion-spirituality/id1314?mt=2",
        # "https://itunes.apple.com/us/genre/podcasts-buddhism/id1438?mt=2",
        # "https://itunes.apple.com/us/genre/podcasts-christianity/id1439?mt=2",
        # "https://itunes.apple.com/us/genre/podcasts-hinduism/id1463?mt=2",
        # "https://itunes.apple.com/us/genre/podcasts-judaism/id1441?mt=2",
        # "https://itunes.apple.com/us/genre/podcasts-other/id1464?mt=2",
        # "https://itunes.apple.com/us/genre/podcasts-spirituality/id1444?mt=2",
    )

    def parse(self, response):
        """ Extract the sub genres"""
        print("parse")
        sel = Selector(response)
        selector = "div#genre-nav div ul li ul li ::attr(href)"
        urls = sel.css(selector).extract()
        for url in urls:
            yield Request(url, callback=self.parse_popular, dont_filter=True)

    def parse_alpha(self, response):
        """ extract the alpha letters links"""
        sel = Selector(response)
        urls = sel.css("ul.alpha li a::attr(href)").extract()

        for url in urls:
            print(url)
            #yield Request(url, callback=self.parse_page)

    def parse_popular(self, response):
        """ extract the popular link"""
        sel = Selector(response)
        urls = sel.css("div#selectedgenre div.alpha a::attr(href)").extract()
        for url in urls:
            print("parse_popular: "+url)
            yield Request(url, callback=self.parse_page, dont_filter=True)

    def parse_page(self, response):
        """ Extract the paginate numbers links """
        print("parse_page")
        
        sel = Selector(response)
        selector = ("ul.paginate li a:not(a.paginate-more)"
                    ":not(a.paginate-previous)"
                    "::attr(href)")
        urls = sel.css(selector).extract()
        if len(urls) > 0:
            for url in urls:
                yield Request(url, callback=self.parse_podcastlist, dont_filter=True)
        else:
          print("parsing single page:" + response.url)
          yield Request(response.url, callback=self.parse_podcastlist)

    def parse_podcastlist(self, response):
        """Extract podcast name and url from the list of podcasts"""
        print("parse_podcastlist")
        sel = Selector(response)
        urls = sel.css("div#selectedcontent div ul li a::attr(href)").extract()
        names = sel.css("div#selectedcontent div ul li a::text").extract()
        for url, name in zip(urls, names):
            _id = get_id_from_url(url)
            item = ItunesItem(name=name, url=url, itunesId=_id)
            yield item
