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

From the hub side, push a message to the satellite via `hive.send.downstream`. The hub's [hivemind-ovos-agent-plugin](https://github.com/JarbasHiveMind/hivemind-ovos-agent-plugin) handles this message:

```python
bus.emit(Message("hive.send.downstream", {
    "msg_type": "bus",
    "payload": some_message.serialize(),
    "peer": "<peer id>"
}))
```

The `peer` value is the peer id of one connected satellite (`HiveMindClientConnection.peer` in hivemind-core). The id is `name::session_id`. If two connections share one access key and ask for the same id, hivemind-core adds a `::<8 hex>` suffix to the second id. A `bus` message is sent only when `peer` is set:

- If `peer` is missing, nothing is sent and no error is emitted.
- If `peer` names no connected satellite, the hub emits `"hive.client.send.error"`.
- The hub does not check that `peer` is the satellite you mean. An id can name a different connected satellite. An old id can belong to a new connection with the same `name::session_id`. In both cases the hub sends the message to that connection and emits no error.
- Do not build the peer id. Read it from `message.context["source"]` of a message that the satellite sent. hivemind-core sets `source` and `peer` to the peer id of the sender.
- A `propagate` or `broadcast` message goes to all connected satellites.
- An `escalate` message is dropped and no error is emitted.
- If `msg_type` is missing, the handler raises an error and sends nothing.

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
