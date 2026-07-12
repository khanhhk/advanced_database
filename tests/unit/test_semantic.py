from src.semantic.query_parser import expand_query, parse_filters


def test_parse_vietnamese_semantic_filters():
    assert parse_filters("phim khoa học viễn tưởng rating trên 7") == ("Science Fiction", 7.0)


def test_parse_genre_without_rating():
    assert parse_filters("tìm phim kinh dị về ngôi nhà bỏ hoang") == ("Horror", None)


def test_expand_cross_lingual_movie_concepts():
    expanded = expand_query("người máy từ tương lai trên sao Hỏa")
    assert "robot" in expanded and "future" in expanded and "Mars" in expanded
