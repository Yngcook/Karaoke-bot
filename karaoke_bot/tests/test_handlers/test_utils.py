import pytest
from karaoke_bot.handlers.utils import format_subscribers_count


test_data = [
    (100, "100"),
    (999, "999"),
    (1000, "1K"),
    (1896, "1.89K"),
    (2586, "2.58K"),
    (8800, "8.8K"),
    (9999, "9.99K"),
    (10_000, "10K"),
    (12_345, "12.3K"),
    (20_000, "20K"),
    (58_300, "58.3K"),
    (99_999, "99.9K"),
    (100_000, "100K"),
    (155_888, "155K"),
    (999_999, "999K"),
    (1_000_000, "1M"),
    (1_567_800, "1.56M"),
    (5_500_361, "5.5M"),
    (9_999_999, "9.99M"),
    (12_345_678, "12.34M"),
    (15_300_000, "15.3M"),
    (100_000_000, "100M")
]


@pytest.mark.parametrize("input_value, expected_output", test_data)
def test_format_subcribers_count(input_value, expected_output):
    assert format_subscribers_count(input_value) == expected_output
