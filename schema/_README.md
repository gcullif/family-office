# schema/ — canonical record templates

The master shapes every record follows. `AAPL_holding_record.json` is the canonical holding
template: each field carries a `value`, a `plain_language` explanation, and a `source_ref` for
provenance (provenance + narrative + time depth, baked into the data model).

New record types get their template here first, then records are built to match.
