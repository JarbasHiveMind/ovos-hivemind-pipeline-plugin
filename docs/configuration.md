# Configuration

## Plugin config block

All keys live under `"ovos-hivemind-pipeline-plugin"` in `~/.config/mycroft/mycroft.conf`.

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

## Key reference

| Key               | Type   | Default       | Description |
|-------------------|--------|---------------|-------------|
| `name`            | string | `"Hive Mind"` | Name used in the confirmation spoken dialog (`"Asking Hive Mind…"`). |
| `confirmation`    | bool   | `true`        | Speak a confirmation dialog before forwarding the utterance. Set to `false` to forward silently. |
| `slave_mode`      | bool   | `false`       | Share the local OVOS bus with the HiveMind hub. The hub receives all bus messages and can inject messages back. Required for bidirectional bus bridging. |
| `allow_selfsigned`| bool   | `false`       | Accept self-signed TLS certificates. Useful in development setups with a local `hivemind-core` using a self-signed cert. |

## Connection identity

The HiveMind connection credentials (host, port, access key, password, site ID) are
read from the identity file written by `hivemind-client set-identity`. The plugin does
not accept inline credential config; set the identity file first:

```bash
hivemind-client set-identity \
  --key <access_key> \
  --password <password> \
  --host <hub_ip> --port 5678 --siteid my-satellite
```

The identity file is stored at `~/.config/hivemind/_identity.json`.

## Entry point

```
group: opm.pipeline
name:  ovos-hivemind-pipeline-plugin
class: ovos_hivemind_pipeline.HiveMindPipeline
```
