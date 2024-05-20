# HiveMind Fallback Skill

When in doubt, ask a smarter OVOS install, powered by [HiveMind Solver](https://github.com/JarbasHiveMind/ovos-solver-hivemind-plugin).

> NOTE: this repository eventually will be converted from a FallbackSkill into a pipeline plugin

## Configuration

Under skill settings (`.config/mycroft/skills/skill-ovos-fallback-hivemind.openvoiceos/settings.json`) you can tweak some parameters for HiveMind Skill.

```json
{
  "name": "HiveMind",
  "confirmation": true,
  "slave_mode": false,
  "allow_selfsigned": false
}
```

| Option             | Value      | Description                                                                                                                                    |
|--------------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| `name`             | `HiveMind` | Name to give to the HiveMind AI assistant                                                                                                      |
| `confirmation`     | `true`     | Spoken confirmation will be triggered when a request is sent HiveMind                                                                          |
| `allow_selfsigned` | `false`    | Allow self signed SSL certificates ofr HiveMind connection                                                                                     |
| `slave_mode`       | `false`    | In slave mode HiveMind master receives all bus messages for passive monitoring and will be able to inject arbitrary messages into the OVOS bus |


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

And then set the identity file in the satellite device (where the skill will run)
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

If this step fails, your skill will also fail to connect to HiveMind

