# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity
from scrapylib.processors import default_input_processor, default_output_processor


class TweetItem(scrapy.Item):
    index = scrapy.Field()
    userid = scrapy.Field()
    username = scrapy.Field()
    fullname = scrapy.Field()
    text_tweet = scrapy.Field()
    original_text_tweet = scrapy.Field()
    max_position = scrapy.Field()
    hash_tags = scrapy.Field()
    time_tweet = scrapy.Field()
    lang = scrapy.Field()
    retweets = scrapy.Field()
    favorite = scrapy.Field()
    place_id = scrapy.Field()
    place = scrapy.Field()


class TweetItemLoader(ItemLoader):
    default_item_class = TweetItem
    default_input_processor = default_input_processor
    default_output_processor = default_output_processor

    hash_tags_out = Identity()
