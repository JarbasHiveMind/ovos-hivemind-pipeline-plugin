"""Regression test for the hivemind_error dialog placeholder.

Both lines of hivemind_error.dialog carry the {name} placeholder in every
shipped locale. ask_hivemind's except branch (__init__.py:114) must call
self.speak_dialog("hivemind_error", data={"name": self.ai_name}), the same
shape the "asking" call one line above it already passes, or the renderer
raises KeyError('name') instead of speaking anything.

This drives the real HiveMindPipeline.ask_hivemind code path on the plugin's
own resources_dir (real OVOSAbstractApplication dialog renderer) against a
FakeBus, forces the transport to fail, and asserts the literal rendered
string that reaches the bus -- not merely the absence of an exception.
"""
from os.path import dirname

from ovos_bus_client.message import Message
from ovos_utils.fakebus import FakeBus
from ovos_workshop.app import OVOSAbstractApplication

import ovos_hivemind_pipeline
from ovos_hivemind_pipeline import HiveMindPipeline


class BoomHiveMindClient:
    """Stand-in transport whose emit_mycroft always fails, driving
    ask_hivemind into its except branch (the speak_dialog("hivemind_error")
    call under test)."""

    def emit_mycroft(self, message):
        raise RuntimeError("transport down")


def _build_pipeline_with_real_dialogs(bus, name="Hive Mind"):
    """Build a HiveMindPipeline with the real OVOSAbstractApplication dialog
    renderer wired up (skipping the real __init__, which would open a
    HiveMessageBusClient websocket)."""
    pipe = HiveMindPipeline.__new__(HiveMindPipeline)
    OVOSAbstractApplication.__init__(
        pipe, bus=bus, skill_id="ovos-hivemind-pipeline-plugin",
        resources_dir=dirname(ovos_hivemind_pipeline.__file__),
    )
    pipe.config = {"confirmation": False, "name": name}
    pipe.hm = BoomHiveMindClient()
    return pipe


def _captured_speaks(bus):
    spoken = []
    bus.on("speak", lambda m: spoken.append(m.data["utterance"]))
    return spoken


def test_ask_hivemind_speaks_rendered_error_dialog_on_transport_failure():
    """When the HiveMind transport raises, ask_hivemind's except branch must
    speak one of the two hivemind_error dialog lines with {name} filled in,
    not raise KeyError('name')."""
    bus = FakeBus()
    pipe = _build_pipeline_with_real_dialogs(bus, name="Hive Mind")
    spoken = _captured_speaks(bus)

    pipe.ask_hivemind(Message("hivemind:ask",
                              {"utterance": "hi", "lang": "en-US"}))

    expected = {
        "I was not able to get an answer from Hive Mind",
        "Sorry but something went wrong with the Hive Mind request.",
    }
    assert len(spoken) == 1
    assert spoken[0] in expected
