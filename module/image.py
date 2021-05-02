import function_pattern_matching as fpm
from schema import Schema

from module import Module


class ModuleImage(Module):
    def __init__(self, state):
        super().__init__(state)

    def init_schema(self):
        self.schema = Schema({
            "name": "Image",
            "active": bool,
            "deps": list,
            "camera_id": int,
            "processing": str,
        })

    @fpm.case
    @fpm.guard
    async def fire(self: fpm._, data: fpm._,  version: fpm.eq("1")):
        pass
