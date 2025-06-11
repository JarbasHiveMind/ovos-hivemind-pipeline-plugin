from os.path import dirname
from typing import Dict, Optional, List, Union

from hivemind_bus_client import HiveMessageBusClient
from ovos_bus_client.client import MessageBusClient
from ovos_bus_client.message import Message
from ovos_plugin_manager.templates.pipeline import PipelinePlugin, IntentHandlerMatch
from ovos_utils.fakebus import FakeBus
from ovos_utils.lang import standardize_lang_tag
from ovos_workshop.app import OVOSAbstractApplication

from ovos_hivemind_pipeline.version import VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD


class HiveMindPipeline(PipelinePlugin, OVOSAbstractApplication):
    def __init__(self, bus: Optional[Union[MessageBusClient, FakeBus]] = None,
                 config: Optional[Dict] = None):
        OVOSAbstractApplication.__init__(
            self, bus=bus, skill_id="ovos-hivemind-pipeline-plugin",
            resources_dir=f"{dirname(__file__)}")
        PipelinePlugin.__init__(self, bus, config)

        self.add_event("hivemind:ask", self.ask_hivemind)

        # values are taken from the NodeIdentity file
        # set via 'hivemind-client set-identity'
        self.hm = HiveMessageBusClient(
            share_bus=self.slave_mode,
            useragent=f"{self.skill_id}:{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}",
            self_signed=self.config.get("allow_selfsigned", False),
            internal_bus=self.bus if self.slave_mode else None
        )
        self.hm.run_in_thread()
        if not self.slave_mode:
            self.hm.on_mycroft("speak", self.on_speak)

    @property
    def slave_mode(self):
        return self.config.get("slave_mode", False)

    @property
    def ai_name(self):
        return self.config.get("name", "Hive Mind")

    @property
    def confirmation(self):
        return self.config.get("confirmation", True)

    def on_speak(self, message: Message):
        # if hivemind server has no direct access to OVOS bus
        # we need to re-emit speak messages
        utt = message.data["utterance"]
        self.speak(utt)

    def ask_hivemind(self, message: Message):
        if self.confirmation:
            self.speak_dialog("asking", data={"name": self.ai_name})

        utterance = message.data["utterance"]
        try:
            self.hm.emit_mycroft(
                message.reply("recognizer_loop:utterance",
                        {"utterances": [utterance], "lang": self.lang})
            )
            # hivemind will answer async
            return True
        except:
            self.speak_dialog("hivemind_error")

        return False

    def match(self, utterances: List[str], lang: str, message: Message) -> Optional[IntentHandlerMatch]:
        """
        Send a hivemind request

        Args:
            utterances (list): List of tuples,
                               utterances and normalized version
            lang (str): Language code
            message: Message for session context
        Returns:
            IntentHandlerMatch or None
        """
        return IntentHandlerMatch(
            match_type="hivemind:ask",
            match_data={"utterance": utterances[0],
                        "lang": standardize_lang_tag(lang)},
            skill_id=self.skill_id,
            utterance=utterances[0])

    def shutdown(self):
        self.default_shutdown()  # remove events registered via self.add_event
