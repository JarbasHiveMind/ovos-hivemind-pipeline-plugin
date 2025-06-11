[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/JarbasHiveMind/ovos-hivemind-pipeline-plugin)

# HiveMind Pipeline Plugin

When in doubt, ask a smarter OVOS install

## Install

`pip install ovos-hivemind-pipeline-plugin`

## Configuration

Under `mycroft.conf` you can tweak some parameters for HiveMind Pipeline.

> 💡 Learn more about intent pipelines and how to configure them in the [ovos-technical-manual](https://openvoiceos.github.io/ovos-technical-manual/pipelines_overview/)

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

| Option             | Value       | Description                                                                                                                                    |
|--------------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| `name`             | `Hive Mind` | Name to give to the HiveMind AI assistant in the confirmation dialog                                                                           |
| `confirmation`     | `true`      | Spoken confirmation will be triggered when a request is sentto  HiveMind                                                                          |
| `allow_selfsigned` | `false`     | Allow self signed SSL certificates for HiveMind connection                                                                                     |
| `slave_mode`       | `false`     | In slave mode HiveMind server receives all bus messages for passive monitoring and will be able to inject arbitrary messages into the OVOS bus |


## HiveMind Setup

You need to register the skill in the HiveMind server
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

And then set the identity file in the satellite device (where the ovos-core is running)
```bash
$ hivemind-client set-identity --key 5a9e580a2773a262cbb23fe9759881ff --password 9b247ca66c7cd2b6388ad49ca504279d --host 0.0.0.0 --port 5678 --siteid test
identity saved: /home/miro/.config/hivemind/_identity.json
```

check the created identity file if you like
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

test that a connection is possible using the identity file
```bash
$ hivemind-client test-identity
(...)
2024-05-20 21:22:28.003 - OVOS - hivemind_bus_client.client:__init__:112 - INFO - Session ID: 34d75c93-4e65-4ea9-b5f4-87169dcfda01
(...)
== Identity successfully connected to HiveMind!
```

> ⚠️ If this step fails, ovos-core will also fail to connect to HiveMind


## Slave Mode

If running in **slave** mode skills can emit serialized [HiveMessages](https://github.com/JarbasHiveMind/hivemind-websocket-client/blob/dev/hivemind_bus_client/message.py) via the regular bus

This can be used to inject bus messages from one device messagebus to the other

from **slave** -> **master**: (might be rejected by `hivemind-core`)
- emit `"hive.send.upstream"` with message.data, `{"msg_type": "bus", "payload": message.serialize()}`

from **master** -> **slave**:
- emit `"hive.send.downstream"` with message.data, `{"msg_type": "bus", "payload": message.serialize()}`

see the [hivemind protocol](https://jarbashivemind.github.io/HiveMind-community-docs/04_protocol) for more details on valid payloads

> 💡 this is what enables [nested hives](https://jarbashivemind.github.io/HiveMind-community-docs/15_nested/), a device can be both a **master** (by running `hivemind-core`) and a **slave** (by running this repo)
