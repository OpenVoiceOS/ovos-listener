from ovos_config.config import Configuration
from ovos_plugin_manager.wakewords import OVOSWakeWordFactory


class HotWordFactory(OVOSWakeWordFactory):
    @classmethod
    def create_hotword(cls, hotword="hey mycroft", config=None,
                       lang="en-us", loop=None):
        if not config:
            config = Configuration()['hotwords']
        return OVOSWakeWordFactory.create_hotword(hotword, config, lang, loop)
