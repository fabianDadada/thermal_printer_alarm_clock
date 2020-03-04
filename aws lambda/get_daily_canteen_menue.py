"""This is the AWS lambda handler to parse the university cafeteria's XML feed.

The handler is run each day, the corresponding data is written to a file in AWS S3.
"""

import datetime
import time
import os
import xml.etree.ElementTree as ET
from urllib.request import urlopen
import boto3
import re

URL = "http://xxx/speiseplan.xml"

def lambda_handler(event, context):
    menu = ""
    try:
        # get timestamp for today
        td = datetime.date.today()
        tdt = td.timetuple()
        os.environ["TZ"] = "Europe/Berlin"
        time.tzset()
        timestamp = int(time.mktime(tdt))

        # download and parse xml
        response = urlopen(URL)
        xml = response.read()
        root = ET.fromstring(xml)
        dishes = root.find("tag[@timestamp='{}']".format(timestamp))
    
        # iterate over dishes - if dishes not None; save dishes in variable menu
        if dishes is not None:
            # menu = "#start#\n"
            for dish in dishes:
                category = dish.find("category").text
                title = dish.find("title").text
                # remove text in parentheses
                title = re.sub("\(.*\)", "", title)

                menu += "#" + category + ":\n" + title + "\n"
    except:
        # if anything goes wrong just clear menu
        menu = ""

    # write menu to s3
    s3 = boto3.resource("s3")
    s3object = s3.Object("xxx", "xxx")
    s3object.put(Body=menu.encode("cp437"))

    return menu