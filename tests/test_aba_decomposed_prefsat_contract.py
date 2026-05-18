from __future__ import annotations

from pathlib import Path


DECOMPOSED_PREFSAT_PAGE_IMAGES = (
    "papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-008.png",
    "papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-009.png",
    "papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-010.png",
    "papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-002.png",
    "papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-003.png",
    "../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-001.png",
    "../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-002.png",
    "../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-003.png",
    "papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-005.png",
    "papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-006.png",
    "papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-012.png",
    "papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/pngs/page-019.png",
    "papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/pngs/page-020.png",
)


def test_decomposed_prefsat_page_image_contract() -> None:
    assert len(DECOMPOSED_PREFSAT_PAGE_IMAGES) == 13
    for path in DECOMPOSED_PREFSAT_PAGE_IMAGES:
        assert path.endswith(".png")
        assert Path(path).exists(), path
