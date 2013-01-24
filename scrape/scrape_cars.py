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

url = "http://www.gumtree.co.za/f-SearchAdRss?CatId=9077&Location=201"
sleep_secs = 60 * 5

index = dict()


def clean_price(x):
    try:
        return float(x.replace("R", "").replace(" ", "").replace(",", ""))
    except ValueError:
        return 0

def clean_mileage(x):
    return int(x)

def clean_date(x):
    return parser.parse(x)

class ParseException(exceptions.Exception):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)

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

        return " ".join(text).strip()

        
    encoded = html.encode("utf8")
    h = md5.md5(str(id)).hexdigest()
    filename = "%s/%s.txt" % (pages_path, h)
    if os.path.exists(filename):
        return None

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
    r = requests.get(url) 
    if r.status_code == 200:
        html = r.text
        return parse_page(url, html, pages_path)
    else:
        r.raise_for_status()
        

def get_entries(url=url, sleep_secs=sleep_secs, callback=lambda x: None, pages_path="/tmp"):
    while True:
        d = feedparser.parse(url)
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
                    callback(vals)
                except Exception, e: 
                    import traceback; traceback.print_exc()
                    puts(colored.red("%s: %s" % (e.message, link)))

        time.sleep(sleep_secs)

def get_entries_disk(callback=lambda x: None):
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
