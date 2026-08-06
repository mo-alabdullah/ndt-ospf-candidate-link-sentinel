# Artifact Integrity

The release distinguishes frozen historical artifacts, corrected validation
artifacts, and the untouched holdout artifacts.

The first holdout sample exposed a parser incompatibility with a three-value
BusyBox ping summary. The measurement was retained; only the parser was
changed to accept both three- and four-value summaries. No SLA, schedule,
policy parameter, margin, or holdout observation was changed.

`frozen_hash_resolution.json` documents why two immutable-manifest filenames
resolve to preserved `_original` files. The manifest itself is unchanged.
