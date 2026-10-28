from answer import extract_citations

NOTES = [{"source": "url-A"}, {"source": "url-B"}, {"source": "url-A"}]


def test_no_markers_gives_no_citations():
    assert extract_citations("no markers here", NOTES) == []


def test_markers_map_to_sources_in_order():
    assert extract_citations("X [2]. Y [1].", NOTES) == ["url-B", "url-A"]


def test_repeated_marker_is_listed_once():
    assert extract_citations("X [1]. Y [1].", NOTES) == ["url-A"]


def test_different_chunks_from_same_page_listed_once():
    assert extract_citations("X [1]. Y [3].", NOTES) == ["url-A"]


def test_out_of_range_numbers_are_ignored():
    assert extract_citations("X [0]. Y [4]. Z [99].", NOTES) == []


def test_multi_digit_numbers_are_read_whole():
    notes = [{"source": f"url-{n}"} for n in range(1, 13)]
    assert extract_citations("X [12].", notes) == ["url-12"]
