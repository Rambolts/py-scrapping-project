import os
from datetime import datetime
from dotmap import DotMap
from typing import Any

from . import configurations, loggers

def get_logger_filename(bot_id: str, root: str = './__logs__', log_filename: str = None, date_fmt: str = r'%Y-%m-%d_%H-%M-%S'):
    """
    Compõe o caminho completo do arquivo de log definido pela AG.

    :param bot_id: id do bot configurado no botcity
    :param job_id: id da automação
    :param root: caminho raiz de onde ficarã os logs
    :param log_filename: nome do arquivo log (por padrão, o mesmo do id da automação)
    :param date_fmt: formato de conversão do timestamp
    :returns: caminho completo do arquivo de log 
    """
    if log_filename is None or log_filename=='':
        log_filename = bot_id

    filename = os.path.basename(log_filename).lower().split(os.path.extsep)[0]

    if date_fmt is None or date_fmt=='':
        datepart = ''
    else:
        datepart = datetime.now().strftime(date_fmt) + '_'

    extension = 'log'
    return os.path.join(root, str(datetime.now().year), f'{datepart}{filename}.{extension}')

def update_dotmap_values(left: Any, right: Any) -> DotMap:
    if isinstance(right, DotMap):
        for k in right:
            if k in left:
                left[k] = update_dotmap_values(left[k], right[k])
        return left
    else:
        return right

def redefine_logger(*args, **kwargs):
    """
    Redefine o logger. Parâmetros serão os mesmos do construtor do app.loggers.AppLogger.
    """
    global logger
    global logger_output
    logger, logger_output = loggers.AppLogger.setup(*args, **kwargs)

def redefine_config(*args, **kwargs):
    """
    Redefine o arquivo de configuração. Parâmetros serão os mesmos do construtor do app.configuration.AppConfig.
    """
    global config
    config = configurations.AppConfig.setup(*args, **kwargs)

def update_config(*args, **kwargs):
    """
    Atualiza arquivo de configuração com chaves provenientes de outro arquivo
    """
    global config
    config = update_dotmap_values(config, configurations.AppConfig.setup(*args, **kwargs))

config = configurations.AppConfig.setup()
logger, logger_output = loggers.AppLogger.setup()


