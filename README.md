[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/JarbasHiveMind/ovos-hivemind-pipeline-plugin)

# HiveMind Pipeline Plugin

This plugin is an intent pipeline for [OVOS](https://github.com/OpenVoiceOS) (Open Voice OS). When the local skills cannot match an utterance, the plugin sends the utterance to a HiveMind server for processing.

## Install

`pip install ovos-hivemind-pipeline-plugin`

## Configuration

Under `mycroft.conf` you can set the parameters for the HiveMind Pipeline.

> Learn more about intent pipelines and how to configure them in the [ovos-technical-manual](https://openvoiceos.github.io/ovos-technical-manual/pipelines_overview/)

```json
{
  "intents": {
    "pipeline": [
      "...",
      "ovos-hivemind-pipeline-plugin",
      "..."
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

| Option             | Value       | Description                                                                                                              |
|--------------------|-------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| `name`             | `Hive Mind` | Name of the HiveMind AI assistant in the confirmation dialog                                                             |
| `confirmation`     | `true`      | Play a spoken confirmation when the plugin sends a request to HiveMind                                                   |
| `allow_selfsigned` | `false`     | Allow self-signed SSL certificates for the HiveMind connection                                                           |
| `slave_mode`       | `false`     | In slave mode, the HiveMind server receives all bus messages for passive monitoring, and can inject arbitrary messages into the OVOS bus |

## HiveMind Setup

Register the client in the HiveMind server.
```bash
$ hivemind-core add-client
Credentials added to database!

Node ID: 2
Friendly Name: HiveMind-Node-2
Access Key: 5a9e580a2773a262cbb23fe9759881ff
Password: 9b247ca66c7cd2b6388ad49ca504279d
Encryption Key: 4185240103de0770
WARNING: Encryption Key is deprecated, only use if your client does not support password
```

Set the identity file on the satellite device, where ovos-core runs.
```bash
$ hivemind-client set-identity --key 5a9e580a2773a262cbb23fe9759881ff --password 9b247ca66c7cd2b6388ad49ca504279d --host 0.0.0.0 --port 5678 --siteid test
identity saved: /home/miro/.config/hivemind/_identity.json
```

Check the identity file.
```bash
$ cat ~/.config/hivemind/_identity.json
{
    "password": "9b247ca66c7cd2b6388ad49ca504279d",
    "access_key": "5a9e580a2773a262cbb23fe9759881ff",
    "site_id": "test",
    "default_port": 5678,
    "default_master": "ws://0.0.0.0"
}
```

Test that a connection is possible with the identity file.
```bash
$ hivemind-client test-identity
(...)
2024-05-20 21:22:28.003 - OVOS - hivemind_bus_client.client:__init__:112 - INFO - Session ID: 34d75c93-4e65-4ea9-b5f4-87169dcfda01
(...)
== Identity successfully connected to HiveMind!
```

> If this step fails, ovos-core also fails to connect to HiveMind.

## Slave Mode

In **slave** mode, skills can emit serialized [HiveMessages](https://github.com/JarbasHiveMind/hivemind-websocket-client/blob/dev/hivemind_bus_client/message.py) over the regular bus. This lets you inject bus messages from one device messagebus into another.

From **slave** to **master** (the message might be rejected by `hivemind-core`):
- Emit `"hive.send.upstream"` with `message.data`, `{"msg_type": "bus", "payload": message.serialize()}`

From **master** to **slave**:
- Emit `"hive.send.downstream"` with `message.data`, `{"msg_type": "bus", "payload": message.serialize()}`

See the [HiveMind protocol](https://jarbashivemind.github.io/HiveMind-community-docs/04_protocol) for details on valid payloads.

This mechanism enables [nested hives](https://jarbashivemind.github.io/HiveMind-community-docs/15_nested/): a device can be both a **master** (by running [hivemind-core](https://github.com/JarbasHiveMind/HiveMind-core)) and a **slave** (by running this plugin).

## Related projects

- [hivemind-core](https://github.com/JarbasHiveMind/HiveMind-core) — the HiveMind server
- [hivemind_bus_client](https://github.com/JarbasHiveMind/hivemind-websocket-client) — the client library used to connect to a HiveMind server
- [HiveMind-community-docs](https://github.com/JarbasHiveMind/HiveMind-community-docs) — the HiveMind protocol documentation
