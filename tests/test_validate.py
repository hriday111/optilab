from optilab.model import load_design
from optilab.validate import has_errors, validate_design


def test_demo_ring_passes():
    d = load_design("designs/demo-ring.yaml")
    f = validate_design(d)
    assert not has_errors(f)


def test_span_loss_formula():
    d = load_design("designs/demo-ring.yaml")
    l1 = next(l for l in d.links if l.id == "L1")
    # 85 * 0.22 + 1.0 = 19.7
    assert abs(l1.span_loss_db() - 19.7) < 1e-6


def test_bad_dup_lambda_fails():
    d = load_design("designs/bad-dup-lambda.yaml")
    f = validate_design(d)
    assert has_errors(f)
    assert any(x.code == "DUP_WAVELENGTH" for x in f)
