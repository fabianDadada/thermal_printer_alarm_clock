"""This is the AWS lambda handler to set the alarm time.

The handler accepts JSON in the form of:

    {
        "time": [timestamp],
        "active": boolean
    }

The corresponding data is then written to a file in AWS S3.
"""

import boto3
import re
import json


def lambda_handler(event, context):
    try:
        # Initialize access to s3.
        s3 = boto3.resource("s3")
        s3object = s3.Object("xxx", "xxx")
        
        # Load old data.
        try:
            alarmData = json.load(object.get()["Body"])
            # Keep only the keys "time" and "active".
            alarmData = { key: alarmData[key] for key in ("time", "active") }
        except:
            alarmData = {}
        
        # If necessary, set default values.
        if "time" not in alarmData:
            alarmData["time"] = 0
        if "active" not in alarmData:
            alarmData["active"] = False
        
        
        # Is there the field "time" in the incoming json?
        if "time" in event:
            time = event["time"]
            
            # Is this a unix time stamp?
            timeStampPattern = re.compile("^[0-9]{10}$")
            if not timeStampPattern.match(str(time)):
                return merge_dicts(alarmData, {"success": False})
            
            alarmData["time"] = int(time)
    
        # Is there the field "active" in the incoming json?
        if "active" in event:
            active = event["active"]
            
            # Is this a boolean?
            if not isinstance(active, bool):
                return merge_dicts(alarmData, {"success": False})
                
            alarmData["active"] = active
    
        s3object.put(Body=json.dumps(alarmData))
        return merge_dicts(alarmData, {"success": True})
        
    except:
        return merge_dicts(alarmData, {"success": False})
        
        
def merge_dicts(a, b):
    c = {}
    c.update(a)
    c.update(b)
    return c
