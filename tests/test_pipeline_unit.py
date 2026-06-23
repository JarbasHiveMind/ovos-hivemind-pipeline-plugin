"""Unit tests for HiveMindPipeline: loading, matching, and forwarding.

These exercise the real plugin code paths (``match`` / ``ask_hivemind`` /
``on_speak``) against a recording stub that stands in for the
``HiveMessageBusClient`` transport — no sockets, no NodeIdentity file.
"""
from ovos_bus_client.message import Message

from conftest import HiveMindStub, build_pipeline


def test_plugin_loads_via_entry_point():
    """The plugin is discoverable through its declared opm.pipeline entry point."""
    from importlib.metadata import entry_points

    eps = entry_points(group="opm.pipeline")
    names = [e.name for e in eps]
    assert "ovos-hivemind-pipeline-plugin" in names, names

    ep = next(e for e in eps if e.name == "ovos-hivemind-pipeline-plugin")
    from ovos_hivemind_pipeline import HiveMindPipeline
    assert ep.load() is HiveMindPipeline


def test_match_builds_intent_handler_match(pipeline):
    match = pipeline.match(["what time is it"], "en-US",
                           Message("recognizer_loop:utterance"))
    assert match is not None
    assert match.match_type == "hivemind:ask"
    assert match.skill_id == "ovos-hivemind-pipeline-plugin"
    assert match.match_data["utterance"] == "what time is it"
    # lang is standardized
    assert match.match_data["lang"] == "en-US"
    assert match.utterance == "what time is it"


def test_ask_hivemind_forwards_utterance(pipeline):
    """ask_hivemind forwards the utterance to the HiveMind transport as a
    recognizer_loop:utterance message."""
    msg = Message("hivemind:ask",
                  {"utterance": "tell me a joke", "lang": "en-US"})
    pipeline.ask_hivemind(msg)

    assert len(pipeline.hm.emitted) == 1
    forwarded = pipeline.hm.emitted[0]
    assert forwarded.msg_type == "recognizer_loop:utterance"
    assert forwarded.data["utterances"] == ["tell me a joke"]
    assert forwarded.data["lang"] == "en-US"


def test_confirmation_speaks_asking_dialog():
    pipe = build_pipeline(config={"confirmation": True, "name": "Hive Mind"})
    pipe.ask_hivemind(Message("hivemind:ask",
                              {"utterance": "hi", "lang": "en-US"}))
    assert "asking" in pipe.spoken_dialogs
    assert len(pipe.hm.emitted) == 1


def test_no_confirmation_skips_asking_dialog(pipeline):
    pipeline.ask_hivemind(Message("hivemind:ask",
                                  {"utterance": "hi", "lang": "en-US"}))
    assert "asking" not in pipeline.spoken_dialogs


def test_ask_hivemind_speaks_error_on_transport_failure():
    class BoomHM(HiveMindStub):
        def emit_mycroft(self, message):
            raise RuntimeError("transport down")

    pipe = build_pipeline(config={"confirmation": False}, hm=BoomHM())
    pipe.ask_hivemind(Message("hivemind:ask",
                              {"utterance": "hi", "lang": "en-US"}))
    assert "hivemind_error" in pipe.spoken_dialogs


def test_on_speak_reemits_utterance_locally(pipeline):
    """In non-slave mode the plugin re-emits HiveMind speak messages locally."""
    pipeline.on_speak(Message("speak", {"utterance": "the answer is 42"}))
    assert "the answer is 42" in pipeline.spoken
