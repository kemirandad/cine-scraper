import scrapy

# Links = //div[starts-with(@class, "TPost")]/a/@href
# Next page = //div[@class="nav-links"]/a[starts-with(@class, "next")]/@href
# Titles = //h1[@class="Title"]/text()
# Summary = //div[@class="Description"]/p/text()
# Director = //span[@class="color-w"]/text()
# Genre = //li[@class="AAIco-adjust"]/a/text()
# Portrait = //div[@class="Image"]/figure/img/@data-src

class CineSpider(scrapy.Spider):
    name = 'cine'
    start_urls = [
        'https://cuevana3.io/peliculas'
    ]
    count = 1

    custom_settings = {
        'FEED_URI' : 'cine.json',
        'FEED_FORMAT' : 'json',
        'FEED_EXPORT_ENCODING': 'utf-8'
    }

    def parse(self, response):
        links = response.xpath(
            '//div[starts-with(@class, "TPost")]/a/@href').getall()

        next_page_button = response.xpath(
            '//div[@class="nav-links"]/a[starts-with(@class, "next")]/@href').get()

        top = getattr(self, 'top', None)

        if top:
            top = int(top)

        if next_page_button:
            yield response.follow(next_page_button, 
                                    callback=self.parse_whole_links,
                                    cb_kwargs={
                                        'links': links,
                                        'top': top
                                    })
        
    
    def parse_whole_links(self, response, **kwargs):

        if kwargs:
            links = kwargs['links']
            top = kwargs['top']

        links.extend(response.xpath(
            '//div[starts-with(@class, "TPost")]/a/@href'
        ).getall())

        next_page_button = response.xpath(
            '//div[@class="nav-links"]/a[starts-with(@class, "next")]/@href').get()

        if next_page_button and (self.count < 5):
            self.count += 1
            yield response.follow(next_page_button, 
                                    callback=self.parse_whole_links,
                                    cb_kwargs={
                                        'links': links,
                                        'top': top
                                    })
        
        else:
            for movie in links:
                yield response.follow(movie, 
                                        callback=self.get_director,
                                        cb_kwargs={'url': response.urljoin(movie)})

        
    def get_director(self, response, **kwargs):
        if kwargs:
            link = kwargs['url']

        title = response.xpath('//h1[@class="Title"]/text()').get()
        summary = response.xpath('//div[@class="Description"]/p/text()').get()
        director = response.xpath('//span[@class="color-w"]/text()').get()
        genre = response.xpath('//li[@class="AAIco-adjust"]/a/text()').getall()
        img = response.xpath('//div[@class="Image"]/figure/img/@data-src').get()

        return {
            'title': title,
            'url': link,
            'portrait' : img,
            'summary' : summary,
            'director': director,
            'genre' : genre
        }