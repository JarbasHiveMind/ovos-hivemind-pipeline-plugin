"""Shared fixtures for the ovos-hivemind-pipeline-plugin test suite."""
from typing import List, Optional

import pytest
from ovos_utils.fakebus import FakeBus

from ovos_hivemind_pipeline import HiveMindPipeline


class HiveMindStub:
    """Stand-in for ``hivemind_bus_client.HiveMessageBusClient``.

    The real ``HiveMessageBusClient`` is built from a NodeIdentity file and
    opens a websocket to a HiveMind master. For unit tests we don't want a
    socket; this stub records what the pipeline forwards via ``emit_mycroft``
    and lets ``on_speak`` be driven by hand.

    ``emit_mycroft`` may be redirected to a hivescope satellite (see the e2e
    tests) so the very same plugin code path drives a real master.
    """

    def __init__(self, forward=None):
        self.emitted: List = []
        self._forward = forward
        self.mycroft_handlers = {}

    def emit_mycroft(self, message) -> None:
        self.emitted.append(message)
        if self._forward is not None:
            self._forward(message)

    def on_mycroft(self, event_name: str, func) -> None:
        self.mycroft_handlers[event_name] = func


def build_pipeline(config: Optional[dict] = None,
                   hm=None,
                   bus: Optional[FakeBus] = None) -> HiveMindPipeline:
    """Construct a ``HiveMindPipeline`` without running its real ``__init__``.

    The production ``__init__`` constructs a real ``HiveMessageBusClient`` from
    a NodeIdentity file and calls ``run_in_thread`` (which opens a websocket),
    so we build the instance bare and wire only the attributes the ``match`` /
    ``ask_hivemind`` / ``on_speak`` code paths actually touch. This keeps the
    real plugin logic under test while swapping the transport.
    """
    pipe = HiveMindPipeline.__new__(HiveMindPipeline)
    pipe.config = config or {}
    pipe.bus = bus or FakeBus()
    pipe.hm = hm if hm is not None else HiveMindStub()
    pipe.skill_id = "ovos-hivemind-pipeline-plugin"

    pipe.spoken = []
    pipe.spoken_dialogs = []
    pipe.speak = lambda utt, *a, **k: pipe.spoken.append(utt)
    pipe.speak_dialog = lambda key, *a, **k: pipe.spoken_dialogs.append(key)
    return pipe


@pytest.fixture
def pipeline():
    """A HiveMindPipeline wired to a recording HiveMindStub (no confirmation)."""
    return build_pipeline(config={"confirmation": False})
