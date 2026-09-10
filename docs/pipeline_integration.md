# Pipeline Integration

## OVOS intent pipeline overview

OVOS processes spoken utterances through a list of pipeline stages. Each stage is a
plugin that attempts to match and handle the utterance. If a stage returns `None`, the
next stage is tried. This plugin is a pipeline stage that forwards utterances to a
remote HiveMind hub.

## Where to place this plugin

Place `"ovos-hivemind-pipeline-plugin"` toward the end of the pipeline, after all
local intent engines:

```json
{
  "intents": {
    "pipeline": [
      "ovos-padatious-pipeline-plugin-high",
      "ovos-adapt-pipeline-plugin",
      "ovos-padatious-pipeline-plugin-medium",
      "ovos-commonqa-pipeline-plugin",
      "ovos-hivemind-pipeline-plugin"
    ]
  }
}
```

## Match behaviour

`HiveMindPipeline.match()` always returns an `IntentHandlerMatch` — it acts as a
catch-all. This means it handles **every** utterance that reaches it. If you want to
limit which utterances reach HiveMind, ensure earlier pipeline stages handle the cases
you want to keep local.

## Request flow

```
OVOS pipeline runner
    |
    | utterances = ["what is the capital of France?"]
    v
HiveMindPipeline.match()
    |
    | returns IntentHandlerMatch(match_type="hivemind:ask", ...)
    v
HiveMindPipeline.ask_hivemind()
    |
    | optionally: speak_dialog("asking", name="Hive Mind")
    | hm.emit_mycroft(recognizer_loop:utterance, ...)
    v
HiveMind hub (hivemind-core)
    |
    | processes with its agent (OVOS bus, persona, ...)
    | returns speak messages
    v
on_speak() re-emits locally (slave_mode=False)
OR hub speaks directly (slave_mode=True)
```

## Error handling

If `hm.emit_mycroft` raises, `ask_hivemind` catches the exception and speaks
`hivemind_error.dialog`. The pipeline runner sees no exception; OVOS continues
normally.

## Locales

Confirmation and error dialogs are bundled for:
- `en-us`
- `fr-fr`
- `nl-nl`
- `pt-pt`

Additional locales can be added under `ovos_hivemind_pipeline/locale/<lang>/`.
