# HiveMind Fallback Skill

When in doubt, ask a smarter OVOS install, powered by [HiveMind Solver](https://github.com/JarbasHiveMind/ovos-solver-hivemind-plugin).

## Configuration

Under skill settings (`.config/mycroft/skills/skill-ovos-fallback-hivemind.openvoiceos/settings.json`) you can tweak some parameters for HiveMind.

```json
{
  "key": "123455",
  "password": "Password1!",
  "host": "192.168.1.18",
  "name": "HiveMind",
  "confirmation": true
}
```

| Option         | Value      | Description                                                                                  |
|----------------|------------|----------------------------------------------------------------------------------------------|
| `key`          | `YYYYY`    | Your `access_key` for HiveMind                                                               |
| `password`     | `XXXXX`    | Your 'password' for HiveMind                                                                 |
| `host`         | `0.0.0.0`  | The ip address where HiveMind can be reached                                                 |
| `port`         | '5678'     | The port where HiveMind can be reached                                                       |
| `name`         | `HiveMind` | Name to give to the HiveMind AI assistant                                                    |
| `confirmation` | `true`     | Spoken confirmation will be triggered when a request is sent HiveMind                        |


