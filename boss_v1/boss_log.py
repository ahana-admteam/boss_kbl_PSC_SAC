import logging as lg
import logging.handlers as handlers
from boss_v1 import settings
import os


# logging configuration
level = lg.ERROR
logging = lg.getLogger('registers')
logging.setLevel(level)
logHandler = handlers.RotatingFileHandler(settings.REGISTERS_LOG, maxBytes=10000, backupCount=2)
logHandler.setLevel(level)
formatter = lg.Formatter(settings.msg_format,datefmt=settings.date_strftime_format)
logHandler.setFormatter(formatter)
logging.addHandler(logHandler)

screeningcommittee_level = lg.ERROR
screeningcommittee_logging = lg.getLogger('screeningcommittee')
screeningcommittee_logging.setLevel(screeningcommittee_level)
# File handler for screeningcommittee
screeningcommittee_logHandler = handlers.RotatingFileHandler(settings.SCREENING_COMMITTEE_LOG, maxBytes=10000, backupCount=5)
screeningcommittee_logHandler.setLevel(screeningcommittee_level)
formatter = lg.Formatter('%(levelname)s - %(asctime)s - %(name)s/%(filename)s/%(funcName)s() : %(message)s', datefmt=settings.date_strftime_format)
screeningcommittee_logHandler.setFormatter(formatter)
screeningcommittee_logging.addHandler(screeningcommittee_logHandler)
# Console handler for screeningcommittee
screeningcommittee_level = lg.DEBUG
screeningcommittee_logging.setLevel(screeningcommittee_level)
screeningcommittee_consoleHandler = lg.StreamHandler()
screeningcommittee_consoleHandler.setLevel(screeningcommittee_level)
formatter = lg.Formatter('%(levelname)s - %(asctime)s - %(name)s/%(filename)s/%(funcName)s() : %(message)s', datefmt=settings.date_strftime_format)
screeningcommittee_consoleHandler.setFormatter(formatter)
screeningcommittee_logging.addHandler(screeningcommittee_consoleHandler)