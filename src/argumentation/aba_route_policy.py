from __future__ import annotations


NATIVE_CNF_PREFSAT_MIN_ASSUMPTIONS = 150
NATIVE_CNF_PREFSAT_MIN_RULE_DENSITY = 25.0


def native_cnf_prefsat_dense_shape(
    *,
    is_flat: bool,
    assumptions: int,
    rule_density: float,
) -> bool:
    return (
        is_flat
        and assumptions > NATIVE_CNF_PREFSAT_MIN_ASSUMPTIONS
        and rule_density > NATIVE_CNF_PREFSAT_MIN_RULE_DENSITY
    )
