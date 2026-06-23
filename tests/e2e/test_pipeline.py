"""End-to-end: drive an utterance through the real HiveMindPipeline code path
to a real HiveMind master, asserting the utterance is routed onto the master's
agent bus.

Uses hivescope's in-process topology simulator — no sockets, no running
servers. The pipeline plugin's ``match`` + ``ask_hivemind`` run unchanged; only
the ``HiveMessageBusClient`` transport (``self.hm``) is redirected onto a
hivescope satellite so the BUS message it emits flows through the genuine
HiveMind protocol (handshake, crypto, ACL, session) to the master.
"""
import pytest
from ovos_bus_client.message import Message

from conftest import HiveMindStub, build_pipeline

# Hard dependency: these are installed via the `test` extra; never importorskip.
from hivescope.scenarios import single_satellite
from hivescope.assertions import assert_bus_message_routed
from hivemind_bus_client.message import HiveMessageType

# The pipeline forwards utterances as recognizer_loop:utterance BUS messages;
# the satellite must be whitelisted for that OVOS message type.
_ALLOWED = ["recognizer_loop:utterance"]


@pytest.fixture
def topology():
    builder = single_satellite(allowed_types=_ALLOWED)
    builder.start_all()
    try:
        yield builder
    finally:
        builder.stop_all()


def _pipeline_on(satellite):
    """Build a HiveMindPipeline whose transport forwards onto a hivescope
    satellite (so emit_mycroft -> satellite.send -> master)."""
    hm = HiveMindStub(forward=satellite.send)
    return build_pipeline(config={"confirmation": False}, hm=hm)


def test_utterance_routed_to_master(topology):
    master = topology.get_master("M0")
    satellite = topology.get_satellite("S0")
    pipe = _pipeline_on(satellite)

    # 1) the pipeline matches the utterance into a hivemind:ask intent
    match = pipe.match(["what is the weather"], "en-US",
                       Message("recognizer_loop:utterance"))
    assert match.match_type == "hivemind:ask"

    # 2) handling that intent forwards the utterance through the real
    #    HiveMind protocol to the master's agent bus
    pipe.ask_hivemind(Message("hivemind:ask", match.match_data))

    # 3) the master received exactly one BUS message
    assert_bus_message_routed(master, count=1)

    # and it carries the utterance, as a recognizer_loop:utterance payload
    routed = [r for r in master.recorder.records
              if r.msg_type == HiveMessageType.BUS.value and r.direction == "in"]
    assert len(routed) == 1
    payload = routed[0].payload
    data = payload if isinstance(payload, dict) else payload.serialize()
    # payload is the serialized OVOS Message dict
    assert data["type"] == "recognizer_loop:utterance"
    assert data["data"]["utterances"] == ["what is the weather"]
    assert data["data"]["lang"] == "en-US"


def test_two_utterances_routed_to_master(topology):
    master = topology.get_master("M0")
    satellite = topology.get_satellite("S0")
    pipe = _pipeline_on(satellite)

    for utt in ["turn on the lights", "what time is it"]:
        match = pipe.match([utt], "en-US", Message("recognizer_loop:utterance"))
        pipe.ask_hivemind(Message("hivemind:ask", match.match_data))

    assert_bus_message_routed(master, count=2)
