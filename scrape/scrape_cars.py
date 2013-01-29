import feedparser
import os
import time
import requests
import glob
import logging
from clint.textui import colored, puts
import md5
from BeautifulSoup import BeautifulSoup, Tag
import exceptions
from dateutil import parser

url = "http://www.gumtree.co.za/f-SearchAdRss?AdType=2&CatId=9077&Location=201"

index = dict()

headers = {}
headers['User-Agent'] = " Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405"

max_sleep = 60 * 10
min_sleep = 60 * 0.5
sleep_secs = min_sleep
upper_sleep_threshold = 0.8
lower_sleep_threshold = 0.5

class ParseException(exceptions.Exception):
    pass

class DuplicateException(exceptions.Exception):
    pass

def clean_price(x):
    try:
        return float(x.replace("R", "").replace(" ", "").replace(",", ""))
    except ValueError:
        return 0

def clean_mileage(x):
    try:
        return int(x)
    except ValueError:
        return 0

def clean_date(x):
    return parser.parse(x)


def parse_page(id, html, pages_path):
    def extract_field(rows, title):
        for row in rows:
            cells = row.findAll("td")
            if cells[0].text == title:
                return cells[1].text
        return ""

    def html2string(tag):
        lst = tag.contents
        text = []
        while len(lst) > 0:
            head = lst[0]
            del lst[0]
            if type(head) == Tag:
                lst = head.contents + lst
            else:
                text.append(head)

        s = " ".join(text).strip()
        s = s.replace("&nbsp;", " ").replace("&amp;", "&")
        return " ".join(s.split())

        
    encoded = html.encode("utf8")
    h = md5.md5(str(id)).hexdigest()
    filename = "%s/%s.txt" % (pages_path, h)
    if os.path.exists(filename):
        raise DuplicateException("%s already exists" % id)

    f = open(filename, "w")
    f.write(encoded)
    f.close()
    
    soup = BeautifulSoup(html)
    table = soup.find(id="attributeTable")
    try:
        rows = table.findAll("tr")

        vals = {
            "hash" : id,
            "title" : soup.find(id="preview-local-title").contents[1],
            "date_listed" : clean_date(extract_field(rows, "Date Listed")),
            "last_edited" : clean_date(extract_field(rows, "Last Edited")),
            "price" : clean_price(extract_field(rows, "Price")),
            "address" : extract_field(rows, "Address").replace("View map", ""),
            "seller_type" : extract_field(rows, "For Sale By"),
            "make" : extract_field(rows, "Make"),
            "model" : extract_field(rows, "Model"),
            "body_type" : extract_field(rows, "Body Type"),
            "year" : extract_field(rows, "Year"),
            "mileage" : clean_mileage(extract_field(rows, "Kilometers")),
            "transmission" : extract_field(rows, "Transmission"),
            "drive_train" : extract_field(rows, "Drivetrain"),
            "air_conditioning" : extract_field(rows, "Air Conditioning"),
            "description" : html2string(soup.find(id="preview-local-desc")),
            "province" : html2string(soup.findAll(itemprop="url")[0]),
            "area" : html2string(soup.findAll(itemprop="url")[1]),
            "suburb" : html2string(soup.findAll(itemprop="url")[2]),
        }
        return vals
    except AttributeError:
        raise ParseException()

def get_detail(url, pages_path):
    r = requests.get(url, headers=headers, timeout=30) 
    if r.status_code == 200:
        html = r.text
        return parse_page(url, html, pages_path)
    else:
        r.raise_for_status()
        

def get_entries(url=url, sleep_secs=sleep_secs, callback=lambda x: None, pages_path="/tmp"):
    """
    function that runs in a loop and scrapes the latest advertisements from gumtree
    """
    possible_misses = 0


    def update_sleep_time(total_entries, processed_entries, current_sleep_secs):
        # if we have too many new entries then increase the polling time
        if processed_entries >= total_entries * upper_sleep_threshold:
            current_sleep_secs = current_sleep_secs = min_sleep
            if current_sleep_secs < min_sleep:
                current_sleep_secs = min_sleep
        # if we have too few new entries then descrease the polling time
        elif processed_entries <= total_entries * lower_sleep_threshold:
            current_sleep_secs = current_sleep_secs + 60
            if current_sleep_secs > max_sleep:
                current_sleep_secs = max_sleep

        return current_sleep_secs
        
    while True:
        d = feedparser.parse(url)
        total_entries = len(d["entries"])
        processed_entries = 0
        for el in d["entries"]:
            link = el["link"]
            if not link in index:
                index[link] = {
                    "published" : el["published_parsed"],
                    "title" :     el["title"],
                    "summary" :   el["summary"],
                }
                try:
                    vals = get_detail(link, pages_path)
                    processed_entries += 1
                    callback(vals)
                except DuplicateException, e:
                    puts(colored.red(e.message))
                except Exception, e: 
                    import traceback; traceback.print_exc()
                    puts(colored.red("%s: %s" % (e.message, link)))

        if len(d["entries"]) == processed_entries:
            possible_misses += 1
            puts(colored.green("Possible misses: %s" % possible_misses))
        sleep_secs = update_sleep_time(total_entries, processed_entries, sleep_secs)
        puts(colored.blue("Current sleep time: %s" % (sleep_secs)))
        time.sleep(sleep_secs)

def get_entries_disk(callback=lambda x: None):
    """
    function used for testing by reading files from disk.
    """
    for filename in glob.glob("pages/*.txt"):
        fp = open(filename)
        vals = parse_page(filename, fp.read().decode("utf8"))
        callback(vals)
	

def callback(vals):
    print vals

def main():
    get_entries_disk(callback=callback)

if __name__ == "__main__":
    main()
