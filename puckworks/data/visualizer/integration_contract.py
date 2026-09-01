"""Frozen Visualizer integration recovery contract (EWP-RWB-001)."""

EXPLICIT_PATHS = ("integration_source", "integration", "parser", "brewdata.parser")
PARSER_FAMILIES = {
    "Parsers::DecentJson": "VISUALIZER_DECENT_JSON",
    "Parsers::DecentTcl": "VISUALIZER_DECENT_TCL",
    "Parsers::Beanconqueror": "VISUALIZER_BEANCONQUEROR",
    "Parsers::Gaggiuino": "VISUALIZER_GAGGIUINO",
    "Parsers::Gaggimate": "VISUALIZER_GAGGIMATE",
    "Parsers::Meticulous": "VISUALIZER_METICULOUS",
    "Parsers::SepCsv": "VISUALIZER_SEP_CSV",
}


def parser_family(value):
    """Map an exact public parser class; deliberately performs no fuzzy matching."""
    return PARSER_FAMILIES.get(value.strip()) if isinstance(value, str) and value.strip() else None


def recover_integration(raw):
    """Recover explicit provenance first, then uniquely proven structural signatures."""
    bd = raw.get("brewdata") if isinstance(raw.get("brewdata"), dict) else {}
    values = [raw.get("integration_source"), raw.get("integration"), raw.get("parser"),
              bd.get("parser")]
    present = [v.strip() for v in values if isinstance(v, str) and v.strip()]
    families = [parser_family(v) for v in present]
    known = {f for f in families if f}
    if present:
        if len(known) == 1 and all(f in known for f in families):
            provenance = ("CONSISTENT_MULTIPLE_EXPLICIT_FIELDS" if len(present) > 1
                          else "EXPLICIT_SOURCE_FIELD")
            return next(iter(known)), present[0], provenance, "EWP_RWB_001_INTEGRATION_RECOVERY_RULE_V1"
        return ("CONFLICTED" if len(known) > 1 else "UNRESOLVED", None,
                "EXPLICIT_SOURCE_CONFLICT" if len(known) > 1 else "UNKNOWN_EXPLICIT_SOURCE",
                "EWP_RWB_001_INTEGRATION_RECOVERY_RULE_V1")
    signatures = []
    if "mill" in bd or "brewFlow" in bd:
        signatures.append("VISUALIZER_BEANCONQUEROR")
    if "datapoints" in bd:
        signatures.append("VISUALIZER_GAGGIUINO")
    if "samples" in bd:
        signatures.append("VISUALIZER_GAGGIMATE")
    if "profile_name" in bd and "data" in bd:
        signatures.append("VISUALIZER_METICULOUS")
    if len(signatures) == 1:
        return signatures[0], None, "UNIQUE_STRUCTURAL_SIGNATURE", "EWP_RWB_001_INTEGRATION_RECOVERY_RULE_V1"
    if len(signatures) > 1:
        return "AMBIGUOUS", None, "AMBIGUOUS_STRUCTURAL_SIGNATURE", "EWP_RWB_001_INTEGRATION_RECOVERY_RULE_V1"
    return "UNRESOLVED", None, "NO_TRANSFER_AUTHORITY", "EWP_RWB_001_INTEGRATION_RECOVERY_RULE_V1"
