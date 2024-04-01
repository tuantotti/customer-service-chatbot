from functools import wraps
import re
from typing import Any


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

class   CleanText:
    def __init__(self) -> None:
        self.emoji_pattern = re.compile("["
                                    u"\U0001F600-\U0001F64F"  # emoticons
                                    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                    u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                    u"\U00002500-\U00002BEF"  # chinese char
                                    u"\U00002702-\U000027B0"
                                    u"\U00002702-\U000027B0"
                                    u"\U000024C2-\U0001F251"
                                    u"\U0001f926-\U0001f937"
                                    u"\U00010000-\U0010ffff"
                                    u"\u2640-\u2642"
                                    u"\u2600-\u2B55"
                                    u"\u200d"
                                    u"\u23cf"
                                    u"\u23e9"
                                    u"\u231a"
                                    u"\ufe0f"  # dingbats
                                    u"\u3030"
                                    "]+", flags=re.UNICODE)
        
        self.remove_escape_character_pattern = re.compile(r"([\r|\n|\t|\xa0])+")
    def remove_emoji(self, text):
        return re.sub(self.emoji_pattern, " ", text)
    
    def remove_escape_character(self, text):
        return re.sub(self.remove_escape_character_pattern, " ", text)
    
    def clean_text(self, text):
        text = self.remove_emoji(text)
        text = self.remove_escape_character(text)

        return text

    
    def __call__(self, text, *args: Any, **kwds: Any) -> Any:
        return self.clean_text(text=text)