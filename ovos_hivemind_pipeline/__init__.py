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
    """
    A pipeline plugin that forwards utterances to a HiveMind client for intent handling.

    NOTE: OVOSAbstractApplication is used to provide self.speak and self.speak_dialog methods
    """

    def __init__(self,
                 bus: Optional[Union[MessageBusClient, FakeBus]] = None,
                 config: Optional[Dict] = None):
        """
        Initialize the HiveMindPipeline.

        Args:
            bus: Optional message bus client (real or fake).
            config: Optional plugin configuration dictionary.
        """
        OVOSAbstractApplication.__init__(
            self, bus=bus, skill_id="ovos-hivemind-pipeline-plugin",
            resources_dir=f"{dirname(__file__)}"
        )
        PipelinePlugin.__init__(self, bus, config)

        self.add_event("hivemind:ask", self.ask_hivemind)

        # values are taken from the NodeIdentity file
        # set via 'hivemind-client set-identity'
        self.hm = HiveMessageBusClient(
            share_bus=self.slave_mode,
            useragent=f"{self.skill_id}-{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}",
            self_signed=self.config.get("allow_selfsigned", False),
            internal_bus=self.bus if self.slave_mode else None
        )
        self.hm.run_in_thread()

        if not self.slave_mode:
            self.hm.on_mycroft("speak", self.on_speak)

    @property
    def slave_mode(self) -> bool:
        """
        Whether the plugin is running in slave mode.

        Returns:
            True if slave mode is enabled, False otherwise.
        """
        return self.config.get("slave_mode", False)

    @property
    def ai_name(self) -> str:
        """
        Name used to refer to the HiveMind AI.

        Returns:
            Name as a string.
        """
        return self.config.get("name", "Hive Mind")

    @property
    def confirmation(self) -> bool:
        """
        Whether to confirm when asking HiveMind.

        Returns:
            True if confirmation is enabled, False otherwise.
        """
        return self.config.get("confirmation", True)

    def on_speak(self, message: Message) -> None:
        """
        Emit a local `speak` message when receiving one from HiveMind.

        Args:
            message: Message containing the utterance to speak.
        """
        # if hivemind server has no direct access to OVOS bus (slave_mode disabled)
        # we need to re-emit speak messages
        utt = message.data["utterance"]
        self.speak(utt)

    def ask_hivemind(self, message: Message):
        """
        Forward the utterance to HiveMind for intent resolution.

        Args:
            message: Message containing the utterance to ask HiveMind.
        """
        if self.confirmation:
            self.speak_dialog("asking", data={"name": self.ai_name})

        try:
            self.hm.emit_mycroft(
                message.reply("recognizer_loop:utterance", {
                    "utterances": [message.data["utterance"]],
                    "lang": message.data["lang"]
                })
            )
            # hivemind will answer async
        except Exception:
            self.speak_dialog("hivemind_error")

    def match(self,
              utterances: List[str],
              lang: str,
              message: Message) -> Optional[IntentHandlerMatch]:
        """
        Match an utterance using the HiveMind plugin.

        Args:
            utterances: List of spoken input strings.
            lang: BCP-47 language tag.
            message: The original message from the pipeline.

        Returns:
            An IntentHandlerMatch if matched, otherwise None.
        """
        return IntentHandlerMatch(
            match_type="hivemind:ask",
            match_data={
                "utterance": utterances[0],
                "lang": standardize_lang_tag(lang)
            },
            skill_id=self.skill_id,
            utterance=utterances[0]
        )

    def shutdown(self) -> None:
        """
        Perform plugin shutdown logic and cleanup events.
        """
        self.default_shutdown() # from OVOSAbstractApplication
