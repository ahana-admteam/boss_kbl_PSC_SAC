"""Tests for boss_v1/boss_log.py."""
import logging


class TestBossLog:
    def test_registers_logger_exists(self):
        import boss_v1.boss_log  # noqa: F401

        logger = logging.getLogger("registers")
        assert logger is not None
        # Has at least one handler
        assert len(logger.handlers) >= 1

    def test_screeningcommittee_logger_exists(self):
        import boss_v1.boss_log  # noqa: F401

        logger = logging.getLogger("screeningcommittee")
        assert logger is not None
        # Has both file and console handlers
        assert len(logger.handlers) >= 2

    def test_screeningcommittee_level(self):
        import boss_v1.boss_log  # noqa: F401

        logger = logging.getLogger("screeningcommittee")
        # Final level after re-set is DEBUG
        assert logger.level == logging.DEBUG
