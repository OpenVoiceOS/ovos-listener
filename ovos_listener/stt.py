from ovos_config.config import Configuration
from ovos_plugin_manager.stt import OVOSSTTFactory
from ovos_utils.log import LOG


class STTFactory(OVOSSTTFactory):
    @staticmethod
    def create(config=None):
        config = config or Configuration().get("stt", {})
        module = config.get("module", "ovos-stt-plugin-selene")
        LOG.info(f"Creating STT engine: {module}")
        return OVOSSTTFactory.create(config)
