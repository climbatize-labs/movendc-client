from schema import SchemaError
import function_pattern_matching as fpm


class ModuleEx(Exception):
    pass


class Module:
    def __init__(self, state):
        self.state = state
        self.schema = None
        self.params = None
        self.init_schema()

    def validate(self, data):
        try:
            self.schema.validate(data)
        except SchemaError as e:
            raise ModuleEx(e)

    def deps_available(self, deps):
        for d in deps:
            if d not in self.state.modules:
                return False
        return True

    async def run(self, data):
        self.validate(data)
        self.params = data
        if not self.deps_available(data["deps"]):
            return
        if data["active"]:
            await self.fire(self, data, "1")

    def get_module(self, mod):
        if mod in self.state.modules:
            return self.state.modules[mod]
        else:
            return None

    @fpm.case
    @fpm.guard
    async def fire(self: fpm._, data: fpm._, version: fpm.eq("1")):
        raise ModuleEx("Not implemented")

    def init_schema(self):
        raise ModuleEx("Not implemented")
