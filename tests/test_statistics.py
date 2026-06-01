# statistics

from src.statistics import Statistics


def test_report():
    stats = Statistics()
    stats.add_file()
    stats.add_success("Входящие")
    stats.register_read_error()

    report = stats.get_report()

    assert "файлов: 1" in report
    assert "Входящие - 1" in report
    assert stats.read_errors == 1
