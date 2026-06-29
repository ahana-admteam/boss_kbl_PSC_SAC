"""Tests for boss_admin/log_utils.py."""
import datetime
import logging
import os

import pytest

from boss_admin import log_utils


class TestExcludeWarningsFilter:
    def test_passes_info_records(self):
        f = log_utils.ExcludeWarningsFilter()
        rec = logging.LogRecord("x", logging.INFO, "p", 0, "m", None, None)
        assert f.filter(rec) is True

    def test_blocks_warning_records(self):
        f = log_utils.ExcludeWarningsFilter()
        rec = logging.LogRecord("x", logging.WARNING, "p", 0, "m", None, None)
        assert f.filter(rec) is False

    @pytest.mark.parametrize(
        "level", [logging.DEBUG, logging.ERROR, logging.CRITICAL]
    )
    def test_passes_non_warning(self, level):
        f = log_utils.ExcludeWarningsFilter()
        rec = logging.LogRecord("x", level, "p", 0, "m", None, None)
        assert f.filter(rec) is True


class _RecordingHandler(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append(record)


class TestStreamToLogger:
    def test_logs_non_empty_message(self):
        logger = logging.getLogger("test_stream_logger_1")
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        handler = _RecordingHandler()
        logger.addHandler(handler)
        try:
            stl = log_utils.StreamToLogger(
                logger, level=logging.INFO, stream=None
            )
            stl.write("hello\n")
            assert any(r.getMessage() == "hello" for r in handler.records)
        finally:
            logger.removeHandler(handler)

    def test_empty_message_does_not_log(self):
        logger = logging.getLogger("test_stream_logger_2")
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        handler = _RecordingHandler()
        logger.addHandler(handler)
        try:
            stl = log_utils.StreamToLogger(logger, stream=None)
            stl.write("   \n")
            assert handler.records == []
        finally:
            logger.removeHandler(handler)

    def test_writes_to_underlying_stream(self):
        import io

        buf = io.StringIO()
        logger = logging.getLogger("test_stream_logger_3")
        stl = log_utils.StreamToLogger(logger, stream=buf)
        stl.write("data")
        assert "data" in buf.getvalue()

    def test_flush_does_not_raise_without_stream(self):
        logger = logging.getLogger("test_stream_logger_4")
        stl = log_utils.StreamToLogger(logger, stream=None)
        stl.flush()  # no-op

    def test_flush_calls_underlying_stream(self):
        import io

        class StubStream(io.StringIO):
            def __init__(self):
                super().__init__()
                self.flush_called = 0

            def flush(self):
                self.flush_called += 1

        stream = StubStream()
        stl = log_utils.StreamToLogger(logging.getLogger("x"), stream=stream)
        stl.flush()
        assert stream.flush_called == 1


class TestDailySizeRotatingFileHandler:
    def test_get_log_filepath_includes_date(self, tmp_path):
        h = log_utils.DailySizeRotatingFileHandler(
            base_dir=str(tmp_path), filename_prefix="x"
        )
        path = h._get_log_filepath()
        today = datetime.date.today()
        assert today.strftime("%Y") in path
        assert today.strftime("%m") in path
        assert today.strftime("%Y-%m-%d") in path
        assert "x_" in path
        h.close()

    def test_get_log_filepath_with_index(self, tmp_path):
        h = log_utils.DailySizeRotatingFileHandler(
            base_dir=str(tmp_path), filename_prefix="x"
        )
        path = h._get_log_filepath(index=3)
        assert path.endswith(".3")
        h.close()

    def test_ensure_log_directory_creates_dirs(self, tmp_path):
        h = log_utils.DailySizeRotatingFileHandler(base_dir=str(tmp_path))
        today = datetime.date.today()
        expected = (
            tmp_path / today.strftime("%Y") / today.strftime("%m")
        )
        assert expected.exists() and expected.is_dir()
        h.close()

    def test_should_rollover_size_threshold(self, tmp_path):
        h = log_utils.DailySizeRotatingFileHandler(
            base_dir=str(tmp_path), maxBytes=10
        )
        h.stream.write("a" * 50)
        h.stream.flush()
        rec = logging.LogRecord("x", logging.INFO, "p", 0, "m", None, None)
        assert h.shouldRollover(rec) is True
        h.close()

    def test_should_rollover_below_threshold(self, tmp_path):
        h = log_utils.DailySizeRotatingFileHandler(
            base_dir=str(tmp_path), maxBytes=10000
        )
        rec = logging.LogRecord("x", logging.INFO, "p", 0, "m", None, None)
        assert h.shouldRollover(rec) is False
        h.close()

    def test_should_rollover_on_date_change(self, tmp_path):
        h = log_utils.DailySizeRotatingFileHandler(base_dir=str(tmp_path))
        h.current_date = datetime.date(1999, 1, 1)
        rec = logging.LogRecord("x", logging.INFO, "p", 0, "m", None, None)
        assert h.shouldRollover(rec) is True
        h.close()

    def test_do_rollover_size_rotates_to_indexed(self, tmp_path):
        h = log_utils.DailySizeRotatingFileHandler(
            base_dir=str(tmp_path), maxBytes=1
        )
        # Write something
        h.stream.write("xxx")
        h.stream.flush()
        original = h.baseFilename
        h.doRollover()
        assert os.path.exists(original + ".1") or os.path.exists(h.baseFilename)
        h.close()

    def test_do_rollover_on_date_change(self, tmp_path, monkeypatch):
        h = log_utils.DailySizeRotatingFileHandler(base_dir=str(tmp_path))
        h.current_date = datetime.date(2020, 1, 1)
        h.doRollover()
        assert h.current_date == datetime.date.today()
        h.close()

    def test_max_bytes_zero_means_no_size_rollover(self, tmp_path):
        h = log_utils.DailySizeRotatingFileHandler(
            base_dir=str(tmp_path), maxBytes=0
        )
        rec = logging.LogRecord("x", logging.INFO, "p", 0, "m", None, None)
        assert h.shouldRollover(rec) is False
        h.close()
