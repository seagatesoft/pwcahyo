import json

from scrapy import Request, Selector, Spider

from pwcahyo.items import TweetItemLoader


class TwitterComSpider(Spider):
    name = 'twitter'
    allowed_domains = ['twitter.com']
    initial_search_url_tmpl = (
        'https://twitter.com/search?f=tweets&vertical=default&q={keywords}&src=typd'
    )
    next_page_url_tmpl = (
        'https://twitter.com/i/search/timeline?f=tweets&vertical=default&q={keywords}&src=typd'
        '&include_available_features=1&include_entities=1&max_position={max_position}'
        '&reset_error_state=false'
    )
    time_initial_search_url_tmpl = (
        'https://twitter.com/search?f=tweets&vertical=default&q={keywords}'
        '&since={since}&until={until}src=typd'
    )
    time_next_page_url_tmpl = (
        'https://twitter.com/i/search/timeline?f=tweets&vertical=default&q={keywords}&src=typd'
        '&include_available_features=1&include_entities=1&max_position={max_position}'
        '&reset_error_state=false&since={since}&until={until}src=typd'
    )

    def start_requests(self):
        if getattr(self, 'since', False) and getattr(self, 'until', False):
            yield Request(
                self.initial_search_url_tmpl.format(
                    keywords=self.keywords,
                    since=self.since,
                    until=self.until,
                ),
                callback=self.parse,
            )
        else:
            yield Request(
                self.initial_search_url_tmpl.format(keywords=self.keywords),
                callback=self.parse,
            )

    def parse(self, response):
        index = response.meta.get('index', 0)
        max_position = response.css(
            "div.stream-container::attr(data-min-position)"
        ).extract_first()

        for tweet in self.parse_tweets(response.selector, index, max_position):
            index += 1
            yield tweet

        if max_position:
            yield self.create_next_page_request(max_position, index)
        else:
            self.logger.info('max_position not found, stopping crawl...')

    def parse_next_page(self, response):
        index = response.meta.get('index', 0)
        data = json.loads(response.body)
        selector = Selector(text=data['items_html'])
        max_position = data['min_position']

        for tweet in self.parse_tweets(selector, index, max_position):
            index += 1
            yield tweet

        yield self.create_next_page_request(max_position, index)
        # if data['has_more_items']:
        #     yield self.create_next_page_request(max_position, index)
        # else:
        #     self.logger.info('no more items after index = %d in %s', index, response.url)

    def parse_tweets(self, selector, index, max_position):
        for tweet_sel in selector.css("li.stream-item"):
            index += 1
            til = TweetItemLoader(selector=tweet_sel)
            til.add_value('index', str(index))
            til.add_css('userid', "div.stream-item-header > a::attr(data-user-id)")
            til.add_css('username', "div.stream-item-header > a > span.username > b::text")
            til.add_css('fullname', "div.stream-item-header > a > strong::text")
            til.add_css('text_tweet', "p.TweetTextSize")
            til.add_css('hash_tags', "p.TweetTextSize > a.twitter-hashtag > b::text")
            til.add_css('lang', "p.TweetTextSize::attr(lang)")
            til.add_css(
                'retweets',
                "div.ProfileTweet-action--retweet span.ProfileTweet-actionCount > span::text",
            )
            til.add_css(
                'favorite',
                "div.ProfileTweet-action--favorite span.ProfileTweet-actionCount > span::text",
            )
            til.add_css(
                'place_id',
                "div.stream-item-header > span.Tweet-geo > a::attr(data-place-id)",
            )
            til.add_css(
                'place',
                "div.stream-item-header > span.Tweet-geo > a > span.u-hiddenVisually::text",
            )

            til.add_value('max_position', max_position)

            yield til.load_item()

    def create_next_page_request(self, max_position, index):
        if getattr(self, 'since', False) and getattr(self, 'until', False):
            next_page_url = self.next_page_url_tmpl.format(
                keywords=self.keywords,
                max_position=max_position,
                since=self.since,
                until=self.until,
            )
        else:
            next_page_url = self.next_page_url_tmpl.format(
                keywords=self.keywords,
                max_position=max_position,
            )

        return Request(
            next_page_url,
            headers={
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'referer': self.initial_search_url_tmpl.format(keywords=self.keywords),
                'x-requested-with': 'XMLHttpRequest',
            },
            meta={'index': index},
            callback=self.parse_next_page,
        )
