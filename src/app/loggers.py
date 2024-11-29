import os
import sys
import logging
import logging.handlers
from io import StringIO
from ansimarkup import parse
from typing import Tuple

class ColoredFormatter(logging.Formatter):
    """ Formatter para saída colorida no standard output """
    
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    MAPPING = {
        'DEBUG'   : {'prefix': grey, 'suffix': reset},
        'INFO'    : {'prefix': '', 'suffix': ''},
        'WARNING' : {'prefix': yellow, 'suffix': reset},
        'ERROR'   : {'prefix': red, 'suffix': reset},
        'CRITICAL': {'prefix': bold_red, 'suffix': reset},
    }

    def format(self, record: logging.LogRecord) -> str:
        """ Formata mensagem """
        mapping = self.MAPPING.get(record.levelname)
        prefix = mapping['prefix']
        suffix = mapping['suffix']
        s = super().format(record)
        return parse(f'{prefix}{s}{suffix}')

class AppLogger:
    """ Classe que representa o logger da aplicação """
    _logger = None

    @classmethod
    def setup(cls, 
              log_filename: str = None, 
              file_mode: str = 'w', 
              file_fmt: str = u'%(asctime)s | %(levelname)s | %(message)s', 
              file_datefmt: str = '%H:%M:%S',
              file_level: str = 'INFO',
              stream_fmt: str = u'%(message)s', 
              stream_datefmt: str = None,
              stream_level: str = 'DEBUG',
              colored: bool = False) -> Tuple[logging.Logger, StringIO]:
        """
        Retorna instância do logger

        :param log_filename: nome do arquivo de log
        """
        logging.basicConfig()
        logger_name = cls.__module__ + '.' + cls.__name__
        cls._logger = logging.getLogger(logger_name)

        cls._logger.setLevel('DEBUG')
        cls._logger.root.handlers.clear()
        cls._logger.handlers.clear()
        cls._logger.propagate = False

        # configurando o logger para saída em stdout
        stream_handler = logging.StreamHandler(sys.stdout)
        formatter_class = ColoredFormatter if colored else logging.Formatter
        stream_handler.setFormatter(formatter_class(fmt=stream_fmt, datefmt=stream_datefmt))
        stream_handler.setLevel(stream_level.upper())
        cls._logger.addHandler(stream_handler)

        # configurando o logger para saída em string
        logger_output = StringIO()
        string_handler = logging.StreamHandler(logger_output)
        string_handler.setFormatter(logging.Formatter(fmt=stream_fmt, datefmt=stream_datefmt))
        string_handler.setLevel(stream_level.upper())
        cls._logger.addHandler(string_handler)

        # configurando o logger para saída em arquivo
        if log_filename is not None:
            dirname = os.path.dirname(log_filename)
            if dirname != '' and not os.path.exists(dirname):
                os.makedirs(dirname, exist_ok=True)

            file_handler = logging.FileHandler(log_filename, mode=file_mode, encoding='utf-8')
            file_handler.setFormatter(logging.Formatter(fmt=file_fmt, datefmt=file_datefmt))
            file_handler.setLevel(file_level.upper())
            cls._logger.addHandler(file_handler)

        return cls._logger, logger_output

