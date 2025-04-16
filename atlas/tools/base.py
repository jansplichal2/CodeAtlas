class BaseTool:
    name: str

    def run(self, **kwargs):
        raise NotImplementedError("Tool must implement a `run` method.")