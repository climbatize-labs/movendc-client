import json


class ConfigEx(Exception):
    pass


class Config:
    def __init__(self, raw):
        self.raw = raw
        self.modules = []

    def init(self):
        try:
            parsed = json.loads(self.raw)
        except json.decoder.JSONDecodeError as e:
            raise ConfigEx(e)

        for mod in parsed["modules"]:
            self.modules.append(mod)

        return self
