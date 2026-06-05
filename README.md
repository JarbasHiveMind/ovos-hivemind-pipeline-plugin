# ovos-hivemind-pipeline-plugin

When a local OVOS install can't handle an utterance, ask a smarter HiveMind hub.

This is an OVOS [intent pipeline plugin](https://openvoiceos.github.io/ovos-technical-manual/pipelines_overview/)
(`opm.pipeline` entry point). It sits at a configurable position in the OVOS pipeline
and forwards unmatched utterances to a remote [HiveMind-core](https://github.com/JarbasHiveMind/HiveMind-core)
hub. The hub processes the utterance with its own skills/agent and speaks the answer
through the local OVOS TTS or (in slave mode) directly via the shared bus.

Typical use case: a lightweight OVOS satellite (e.g. a Pi Zero) that escalates
anything beyond its local skills to a powerful central hub.

## Install

```bash
pip install ovos-hivemind-pipeline-plugin
```

## Quickstart

### 1. Register a client on the HiveMind hub

On the machine running `hivemind-core`:

```bash
hivemind-core add-client
# note the Access Key and Password
```

### 2. Set the identity on the OVOS satellite

On the satellite (where OVOS and this plugin run):

```bash
hivemind-client set-identity \
  --key <access_key> \
  --password <password> \
  --host <hub_ip> --port 5678 --siteid satellite
```

Verify the connection:

```bash
hivemind-client test-identity
# should print: == Identity successfully connected to HiveMind!
```

### 3. Add the plugin to the OVOS pipeline

Edit `~/.config/mycroft/mycroft.conf`:

```json
{
  "intents": {
    "pipeline": [
      "ovos-padatious-pipeline-plugin-high",
      "ovos-adapt-pipeline-plugin",
      "ovos-padatious-pipeline-plugin-medium",
      "ovos-commonqa-pipeline-plugin",
      "ovos-hivemind-pipeline-plugin"
    ],
    "ovos-hivemind-pipeline-plugin": {
      "name": "Hive Mind",
      "confirmation": true,
      "slave_mode": false,
      "allow_selfsigned": false
    }
  }
}
```

Place `"ovos-hivemind-pipeline-plugin"` near the end of the pipeline so it only
fires when local intent engines have already failed.

## Configuration

All keys are under `"ovos-hivemind-pipeline-plugin"` in `mycroft.conf`.

| Key               | Type    | Default      | Description |
|-------------------|---------|--------------|-------------|
| `name`            | string  | `"Hive Mind"` | Name spoken in the confirmation dialog. |
| `confirmation`    | bool    | `true`       | Speak a confirmation before sending the utterance to HiveMind. |
| `slave_mode`      | bool    | `false`      | Share the local OVOS bus with the hub for passive monitoring and bidirectional message injection. |
| `allow_selfsigned`| bool    | `false`      | Accept self-signed TLS certificates on the HiveMind connection. |

## How it works

When the OVOS pipeline reaches this plugin, `match()` always returns a match — it
acts as a catch-all. The match queues a `hivemind:ask` event. `ask_hivemind()`
optionally speaks a confirmation dialog, then calls `hm.emit_mycroft(utterance)` to
forward the utterance to the hub.

The hub processes the utterance and, depending on `slave_mode`:

- **slave_mode disabled (default)**: the hub's `speak` messages are forwarded back via
  the HiveMind WebSocket and re-emitted on the local OVOS bus by `on_speak`.
- **slave_mode enabled**: the hub has direct bus access and handles TTS itself.

## Slave mode

In slave mode the hub receives all local bus messages for passive monitoring and can
inject arbitrary messages into the local OVOS bus.

To send a message from the satellite to the hub (upstream):

```python
bus.emit(Message("hive.send.upstream", {
    "msg_type": "bus",
    "payload": some_message.serialize()
}))
```

To push a message from the hub to the satellite (downstream):

```python
bus.emit(Message("hive.send.downstream", {
    "msg_type": "bus",
    "payload": some_message.serialize()
}))
```

This also enables [nested hives](https://jarbashivemind.github.io/HiveMind-community-docs/15_nested/):
a device can run both `hivemind-core` (as a hub for its own satellites) and this
plugin (as a satellite to a larger hub).

## Documentation

- [`docs/pipeline_integration.md`](docs/pipeline_integration.md) — how the plugin
  integrates with the OVOS pipeline.
- [`docs/configuration.md`](docs/configuration.md) — full configuration reference.
- [`docs/slave_mode.md`](docs/slave_mode.md) — slave mode and nested hives.

## License

Apache 2.0.
