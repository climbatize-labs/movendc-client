import ssl
import config
import sys

from module import (
    ModuleWSClient,
    ModuleImage,
    ModulePhilipshue,
)


class State:
    def __init__(self):
        self.closed = False
        self.logged = False
        self.cfg_path = None
        self.cfg = None
        self.modules = {}

    async def init(self, cfgpath):
        self.sslcontext = ssl.SSLContext()
        self.cfg_path = cfgpath

        self.get_config()
        await self.init_modules()

    def get_config(self):
        if self.cfg_path:
            filename = self.cfg_path
        else:
            filename = "config/zoycam.cfg"
        with open(filename, "r") as f:
            raw = f.read()
            self.cfg = config.Config(raw).init()

    async def init_modules(self):
        for mod_cfg in self.cfg.modules:
            c = getattr(sys.modules[__name__], "Module" + mod_cfg["name"])
            if c:
                instance = c(self)
                self.modules[mod_cfg["name"]] = instance
                await instance.run(mod_cfg)
            else:
                raise Exception(f"Module {mod['name']} doesn't exist")
