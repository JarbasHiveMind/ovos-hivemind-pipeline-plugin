from ovos_hivemind_solver import HiveMindSolver
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
        self.hm = HiveMindSolver(config={"hivemind": self.settings})  # will connect to HM here
        self.register_fallback(self.ask_hivemind, 85)

    @property
    def ai_name(self):
        return self.settings.get("name", "Hive Mind")

    @property
    def confirmation(self):
        return self.settings.get("confirmation", True)

    @property
    def ask_async(self):
        return self.settings.get("async", True)

    def _hivemind_response(self, message):
        utterance = message.data["utterance"]
        self.chat.qa_pairs = self.build_msg_history(message)
        answered = False
        try:
            utt = self.hm.spoken_answer(utterance)
            if utt:
                answered = True
                self.speak(utt)
        except Exception as err:  # speak error on any network issue etc
            self.log.error(err)
        if not answered:
            self.speak_dialog("hivemind_error", data={"name": self.ai_name})
        return answered

    def ask_hivemind(self, message):
        if "key" not in self.settings:
            self.log.error(
                "HiveMind not configured yet, please set your API key in %s",
                self.settings.path,
            )
            return False  # HiveMind not configured yet
        if self.confirmation:
            self.speak_dialog("asking", data={"name": self.ai_name})
        if self.ask_async:
            # ask in a thread so fallback doesnt timeout
            self.bus.once("async.hivemind.fallback", self._hivemind_response)
            self.bus.emit(
                message.forward("async.hivemind.fallback", message.data)
            )
            return True
        return self._hivemind_response(message)
