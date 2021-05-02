import json
import requests as req

def get(url):
    try:
        resp = req.get(url)
        a = json.loads(resp.text)
        sensors = []
        if "sensors" in a:
            for s in a["sensors"]:
                if "state" in a["sensors"][s] and "temperature" in a["sensors"][s]["state"]:
                    sensors.append({
                        "name" : a["sensors"][s]["name"],
                        "temp" : a["sensors"][s]["state"]["temperature"]
                    })
        return sensors
    except:
        return []
