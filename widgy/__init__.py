class Registry(dict):
    def register(self, content, config):
        self[content] = config

registry = Registry()
