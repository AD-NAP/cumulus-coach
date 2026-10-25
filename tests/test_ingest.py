from ingest import chunk_words


def test_empty_text_gives_no_chunks():
    assert chunk_words("", size=4, overlap=1) == []


def test_short_text_gives_one_chunk():
    assert chunk_words("a b", size=4, overlap=1) == ["a b"]


def test_chunks_share_overlap_words():
    chunks = chunk_words("a b c d e f g h i j", size=4, overlap=1)
    assert chunks == ["a b c d", "d e f g", "g h i j"]
    for first, second in zip(chunks, chunks[1:]):
        assert first.split()[-1] == second.split()[0]


def test_no_trailing_chunk_of_only_overlap():
    # 7 words: the second chunk already reaches the end, so there is no third chunk "g"
    assert chunk_words("a b c d e f g", size=4, overlap=1) == ["a b c d", "d e f g"]


def test_extra_whitespace_is_ignored():
    assert chunk_words("a  b\n\tc", size=4, overlap=1) == ["a b c"]


def test_default_size_and_overlap():
    text = " ".join(f"w{i}" for i in range(1000))
    chunks = chunk_words(text)
    assert len(chunks) == 3
    assert [len(c.split()) for c in chunks] == [500, 500, 100]
