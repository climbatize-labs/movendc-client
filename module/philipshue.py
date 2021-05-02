import asyncio
import function_pattern_matching as fpm
from schema import Schema
import json
import requests

from module import Module


class ModulePhilipshue(Module):
    def __init__(self, state):
        super().__init__(state)

    def init_schema(self):
        self.schema = Schema({
            "name": "Philipshue",
            "active": bool,
            "deps": list,
            "url": str,
            "update_interval": int,
        })

    async def loop(self, wsclient, data):
        sensors = self.get_sensors(data)
        for sensor in sensors:
            s = {
                "event": "data",
                "type": "PH_sensors",
                "value": sensor
            }

            if wsclient.ws:
                await wsclient.ws.send(json.dumps(s))

        await asyncio.sleep(data["update_interval"])
        asyncio.ensure_future(self.loop(wsclient, data))

    def get_sensors(self, data):
        try:
            resp = requests.get(data["url"])
            loaded = json.loads(resp.text)
            sensors = []
            if "sensors" in loaded:
                for s in loaded["sensors"]:
                    if "state" in loaded["sensors"][s]:
                        if "temperature" in loaded["sensors"][s]["state"]:
                            sensors.append({
                                "name" : loaded["sensors"][s]["name"],
                                "temp" : loaded["sensors"][s]["state"]["temperature"]
                            })
                        elif "lightlevel" in loaded["sensors"][s]["state"]:
                            sensors.append({
                                "name" : loaded["sensors"][s]["name"],
                                "lightlevel" : loaded["sensors"][s]["state"]["lightlevel"]
                            })
                        elif "presence" in loaded["sensors"][s]["state"]:
                            sensors.append({
                                "name" : loaded["sensors"][s]["name"],
                                "presence" : loaded["sensors"][s]["state"]["presence"]
                            })

            if "lights" in loaded:
                for s in loaded["lights"]:
                    if "state" in loaded["lights"][s]:
                        if "on" in loaded["lights"][s]["state"]:
                            sensors.append({
                                "name" : loaded["lights"][s]["name"],
                                "on" : loaded["lights"][s]["state"]["on"]
                            })

            return sensors
        except:
            return []

    @fpm.case
    @fpm.guard
    async def fire(self: fpm._, data: fpm._,  version: fpm.eq("1")):
        wsclient = self.get_module(data["deps"][0])
        await self.loop(wsclient, data)
