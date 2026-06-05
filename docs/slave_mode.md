# Slave Mode and Nested Hives

## What is slave mode?

With `slave_mode: false` (default), this plugin sends utterances to the hub and
receives `speak` messages back over the HiveMind WebSocket. The hub and the satellite
are loosely coupled; the hub cannot push arbitrary messages to the local OVOS bus.

With `slave_mode: true`, the plugin passes the local OVOS `MessageBusClient` to
`HiveMessageBusClient(internal_bus=self.bus)`. The hub gains access to the internal
OVOS bus — it receives every bus message for passive monitoring and can inject
messages in both directions.

## Bus message bridging

### Satellite → hub (upstream)

Any OVOS component on the satellite can push a message to the hub by emitting
`hive.send.upstream`:

```python
bus.emit(Message("hive.send.upstream", {
    "msg_type": "bus",
    "payload": some_message.serialize()
}))
```

### Hub → satellite (downstream)

From the hub side, push a message to the satellite via `hive.send.downstream`:

```python
bus.emit(Message("hive.send.downstream", {
    "msg_type": "bus",
    "payload": some_message.serialize()
}))
```

## Nested hives

A device can simultaneously be:

- a **hub** by running `hivemind-core`, serving its own satellites, and
- a **satellite** by running this plugin with `slave_mode: true`, connected
  to a larger hub upstream.

This allows multi-level mesh topologies where a mid-tier device aggregates a cluster
of small satellites and escalates unknown queries to a powerful central hub.

See the
[nested hives documentation](https://jarbashivemind.github.io/HiveMind-community-docs/15_nested/)
for protocol-level details.

## Security considerations

Slave mode gives the hub broad access to the local bus. Only enable it for trusted
hubs. Use TLS (`ssl: true` in `hivemind-core`'s network config) in production
deployments.
