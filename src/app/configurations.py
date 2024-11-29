from dotmap import DotMap
import yaml
import warnings

class AppConfigNotLoadedWarning(UserWarning):
    pass

class AppConfig:
    @classmethod
    def setup(cls, config_filename: str = './app_config.yml'):
        """
        Configura configurações a partir de um arquivo YAML

        :param config_filename: caminho do arquivo yaml que contém as configurações
        :returns: objeto do tipo DotMap com as configurações carregadas
        """
        try:
            with open(config_filename, encoding='utf-8') as f:
                content = yaml.safe_load(f)
            return DotMap(content, _dynamic=False)
        except FileNotFoundError:
            warnings.warn('Arquivo de configuração não encontrado.', AppConfigNotLoadedWarning)
            return DotMap(_dynamic=False)
