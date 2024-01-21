class CiscoConfig:
    def __init__(self):
        self.configurations = {}

    def save_config(self, device_name, config):
        self.configurations[device_name] = config

    def get_config(self, device_name):
        return self.configurations.get(device_name, None)
