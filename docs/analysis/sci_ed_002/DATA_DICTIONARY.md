# Data dictionary

Version 1.0.0 schemas and header-only CSV templates cover the 20 required entities under `schemas/1.0.0/` and `templates/1.0.0/`. Every field is required in a populated row; explicit status tokens replace unknown values. Empty numeric cells never mean zero. Units, basis, estimand, analyte, method, lab, batch, preparation, injection, QC, quantification, uncertainty, quality, provenance, rights, and role are explicit. Raw native files are immutable and hashed with SHA-256 in `file_manifest`.
