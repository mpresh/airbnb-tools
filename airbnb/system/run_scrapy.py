from tempfile import NamedTemporaryFile
from shell_utils import run_command
import sys
import os
import json
import re

def run_airbnb_spider(**kwargs):
    results = run_spider("scrapers/bnbdata/spiders/airbnb.py", **kwargs)
    clean_results = []
    for result in results:
        mo = re.search("rooms[/](.*)[?]", result)
        if mo:
            clean_results.append(mo.group(1))
        else:
            print("result", result)
    return clean_results


def run_spider(path_to_spider, **kwargs):
    spider_path = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), ".."),
                                               path_to_spider))

    f = NamedTemporaryFile(suffix=".json", delete=False)
    cmd = "/usr/bin/env scrapy runspider {} -o {}".format(spider_path, f.name)

    for key, value in kwargs.iteritems():
        if value is not None:
            cmd += " -a {}={}".format(key, value)

    run_command(cmd, shell=True)
    f.seek(0)
    out = f.read()
    #os.unlink(f.name)
    return [url["url"] for url in json.loads(out)]
    
if __name__ == "__main__":
    #result = run_spider("scrapers/bnbdata/spiders/airbnb.py",
    #                    start_url="https://www.airbnb.com/s/Cape-Cod--Barnstable-County--MA--United-States")
    result = run_airbnb_spider(start_url="https://www.airbnb.com/s/Cape-Cod--Barnstable-County--MA--United-States")
    print(result, type(result))
