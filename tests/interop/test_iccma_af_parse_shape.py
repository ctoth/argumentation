"""Dense AF input must reuse vertex IDs rather than allocate strings per edge."""

from argumentation.interop import iccma


def test_dense_numeric_af_validates_ids_once_and_reuses_canonical_objects(monkeypatch):
    count = 120
    text = f"p af {count}\n" + "".join(
        f"{a} {b}\n" for a in range(1, count + 1) for b in range(1, count + 1)
    )
    calls = []
    original = iccma._validate_attack_id

    def validate(value, *args):
        calls.append(value)
        return original(value, *args)

    monkeypatch.setattr(iccma, "_validate_attack_id", validate)
    framework = iccma.parse_af(text)
    assert len(framework.defeats) == count * count
    assert len(calls) <= count
    canonical = {a: a for a in framework.arguments}
    assert all(a is canonical[a] and b is canonical[b] for a, b in framework.defeats)
