from app.citations.markers import check_markers, find_markers


def test_finds_ranges_single_lines_and_skips_repeats() -> None:
    text = (
        "O carrinho fica em [[src/cart.py:L10-L20]] e a rota em [[./src/routes.py:L5]]. "
        "De novo: [[src/cart.py:L10-L20]]. Espaços: [[src/a.py:L1 - L2]]. "
        "Não é marcador: [[sem linhas]] nem [src/b.py:L1]."
    )

    markers = find_markers(text)

    assert [(m.path, m.line_start, m.line_end) for m in markers] == [
        ("src/cart.py", 10, 20),
        ("src/routes.py", 5, 5),
        ("src/a.py", 1, 2),
    ]
    assert markers[1].text == "[[./src/routes.py:L5]]"


def test_marker_is_valid_only_when_file_and_lines_exist() -> None:
    markers = find_markers(
        "[[src/cart.py:L1-L30]] [[src/cart.py:L29-L31]] "
        "[[src/inventado.py:L1]] [[src/cart.py:L9-L3]]"
    )

    citations = check_markers(markers, {"src/cart.py": 30})

    assert [(c.valid, c.problem) for c in citations] == [
        (True, None),
        (False, "lines_out_of_range"),
        (False, "file_not_found"),
        (False, "lines_out_of_range"),
    ]
