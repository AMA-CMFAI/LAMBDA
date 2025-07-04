import logging
import os


def setup_logger(level=None):

    if level is None:
        if int(os.getenv('LAMBDA_DEBUG', '0').strip()):
            level = logging.DEBUG
        else:
            level = logging.INFO

    logger = logging.getLogger('lambda_logger')
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = setup_logger()