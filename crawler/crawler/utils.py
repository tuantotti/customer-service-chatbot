from functools import wraps


def check_spider_pipeline(process_item_method):
    @wraps(process_item_method)
    def wrapper(self, item, spider):

        # message template for debugging
        msg = "%%s %s pipeline step" % (self.__class__.__name__,)
        msg = f"{self.__class__.__name__} pipeline step"

        # if class is in the spider's pipeline, then use the
        # process_item method normally.
        if self.__class__ in spider.pipeline:
            spider.logger.info(f"{msg} executing")
            return process_item_method(self, item, spider)

        # otherwise, just return the untouched item (skip this step in
        # the pipeline)
        else:
            spider.logger.info(f"{msg} executing")
            return item

    return wrapper
