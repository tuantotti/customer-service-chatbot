from root (customer-service-chatbot) cd to crawler/ folder
cd crawler
scrapy crawl -o output/promotion.csv promotion_crawler
scrapy crawl -o output/promotion_detail.csv promotion_detail_crawler