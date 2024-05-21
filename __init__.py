from hivemind_bus_client import HiveMessageBusClient
from ovos_bus_client.message import Message
from ovos_utils import classproperty
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.skills.fallback import FallbackSkill


class HiveMindFallbackSkill(FallbackSkill):

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            internet_before_load=True,
            network_before_load=True,
            requires_internet=True,
            requires_network=True,
        )

    def initialize(self):
        # values are taken from the NodeIdentity file
        # set via 'hivemind-client set-identity'
        self.hm = HiveMessageBusClient(
            share_bus=self.slave_mode,
            useragent=f"HiveMindFallbackSkill",
            self_signed=self.settings.get("allow_selfsigned", False),
            internal_bus=self.bus if self.slave_mode else None
        )
        self.hm.run_in_thread()
        if not self.slave_mode:
            self.hm.on_mycroft("speak", self.on_speak)
        self.register_fallback(self.ask_hivemind, 85)

    def on_speak(self, message):
        # master has no direct access to OVOS bus
        # we need to re-emit speak messages sent by master
        utt = message.data["utterance"]
        self.speak(utt)

    @property
    def slave_mode(self):
        return self.settings.get("slave_mode", False)

    @property
    def ai_name(self):
        return self.settings.get("name", "Hive Mind")

    @property
    def confirmation(self):
        return self.settings.get("confirmation", True)

    def ask_hivemind(self, message):
        if self.confirmation:
            self.speak_dialog("asking", data={"name": self.ai_name})

        utterance = message.data["utterance"]
        try:
            self.hm.emit_mycroft(
                Message("recognizer_loop:utterance",
                        {"utterances": [utterance], "lang": self.lang})
            )
            # hivemind will answer async
            return True
        except:
            if self.confirmation:
                # speak an error if we said we were asking hivemind
                # but let next fallback try to answer
                self.speak_dialog("hivemind_error")

        return False
