import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert 

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service 
from time import sleep
from retry import retry

class Selenium():
    def __init__(self, capsolver_api_token:str=None, relative_download_path:str=None, environment:str="DEV", timeout:int=30, options:Options=None, disable_extensions=False, undetected_chromedriver=False):
        """
            O self._driver procura o webdriver mais atualizado para acompanhar as atualizações do Google Chrome. 

            Caso haja algum erro, busca-se um webdriver já baixado.

            ### Params
            * homolog : ambiente de produção ou desenolvimento  
            * timeout : seta o timeout do wait
        """
        
        self.options = options or Options()
        self.capsolver_api_token = capsolver_api_token
        self.relative_download_path = relative_download_path
        self.environment = environment
        self.timeout = timeout
        self.disable_extensions = disable_extensions
        self.undetected_chromedriver = undetected_chromedriver

    def start(self):        
        self.options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        DesiredCapabilities.CHROME['goog:loggingPrefs'] = {'performance': 'ALL'}
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--no-sandbox")
        self.options.accept_insecure_certs = True
        self.options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
        self.options.add_argument("--disable-blink-features=AutomationControlled")     
        self.options.add_argument("--disable-webrtc")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)

        prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "plugins.plugins_list": [{
                    "enabled": False,
                    "name": "Chrome PDF Viewer"}],
                "plugins.always_open_pdf_externally": True,
                "profile.default_content_settings.popups": 0,
                "logging": {
                    "performance": "ALL"
                },
            }
        self.options.add_experimental_option("prefs", prefs)  
        self._download_path = os.path.abspath(os.path.join('.', self.relative_download_path or ""))
        prefs["download.default_directory"] = self._download_path
        os.makedirs(prefs['download.default_directory'], exist_ok=True)
    
        
        if self.capsolver_api_token is not None:
            print("Including CapSolver Extension...")
            from capsolver_extension_python import Capsolver
            path_capsolver_extension = Capsolver(api_key=self.capsolver_api_token).load().replace("\\", "/")
            self.options.add_argument(path_capsolver_extension)
                
        self._driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install().replace("THIRD_PARTY_NOTICES.", "")), 
            options=self.options)
        
        self._action = ActionChains(self._driver)
        self._alert = Alert(self._driver)
        self._wait = WebDriverWait(self._driver, self.timeout)
        self._long_wait = WebDriverWait(self._driver, self.timeout*3)
        self._short_wait = WebDriverWait(self._driver, self.timeout/3)

    def get_driver(self):
        """
            Retorna o driver do navegador.
        """
        return self._driver
    
    def get_wait(self, long_wait=False, short_wait=False):
        """
            Retorna o wait do navegador.
        """
        return self._long_wait if long_wait else self._short_wait if short_wait else self._wait
    
    def get_action(self):
        """
            Retorna o action do navegador.
        """
        return self._action
    
    def get_alert(self):
        """
            Retorna o módulo de alertas do navegador.
        """
        return self._alert
    
    def get_ambiente(self):
        """
            Retorna o ambiente.
        """
        return self.ambiente
    
    def get_download_path(self):
        """
            Retorna o caminho default de download.
        """
        return self.local_download_path

    def go_to_url(self, url:str):
        """
            Abre o navegador na url desejada.

            ### params
            * url: URL que se deseja acessar.
        """
        self.get_driver().get(url)

    def refresh(self):
        """
            Atualiza navegador
        """
        self._driver.refresh()

    def exist_element(self, selector:tuple[str, str])->bool:
        """
            Verifica se há o elemento na página.

            ### params
            * selector : seletor de elemento, uma tupla que especifique o tipo e a referência

            ### return
            * booleano indicando se existe, ou não o elemento.
        """
        try:
            element = self._driver.find_element(*selector)
            return True, element
        except NoSuchElementException:
            return False
        
    def exist_element_contains_text(self, selector:tuple[str, str], text:str)->bool:
        """
            Verifica se há o texto no elemento indicado.

            ### params
            * selector : seletor de elemento, uma tupla que especifique o tipo e a referência.
            * text : texto que será validado se está ou não incluso no elemento indicado.

            ### return
            * booleano indicando se existe, ou não o elemento.
        """
        try:
            element = self._driver.find_element(*selector)
            if text in element.text:
                return True
            else:
                return False
        except NoSuchElementException:
            return False
        
    def scroll_top(self):
        """
            Move a tela para a posição inicial.
        """
        self._driver.execute_script(f"window.scrollTo(0, 0);")
        
    def scroll_to_element(self, selector:tuple[str, str], expected_condition:bool=True, find_if_error:bool=False):
        """
            Move a tela para o elemento.

            ### params
            * selector : seletor de elemento, uma tupla que especifique o tipo e a referência
            * expected_condition: utiliza o recurso EC para o elemento inserido.
            * find_if_err: em caso de erro, faz um scroll para baixo em 250 como padrão.
        """
        if expected_condition:
            element = self.located(selector)
        else:
            element = self._driver.find_element(*selector)
            
        if find_if_error:
            scroll = 0
            for _ in range(30):
                try:
                    self._action.move_to_element(element).perform()
                    break
                except:
                    scroll += 250
                    self._driver.execute_script(f"window.scrollTo(0, {scroll});")
        else:
            self._action.move_to_element(element).perform()

    def _wait_load_element(self, selector:tuple[str, str], long_wait=False):
        """
            Aguarda um elemento que represente um carregamento desaparecer.

            ### params
            * selector : seletor de elemento, uma tupla que especifique o tipo e a referência
        """
        sleep(2)

        if long_wait:           
            return self._long_wait.until(EC.invisibility_of_element(selector))
        self._wait.until(EC.invisibility_of_element(selector))
    
    def _wait_url_to_be(self, url, long_wait=False, short_wait=False):
        """
            Aguarda até que a url atual seja igual ao texto informado.

            ### params
            * url : endereço web completo
        """
        
        (self._long_wait if long_wait else self._wait).until(lambda d: d.current_url == url)           

    def get_current_url(self):
        """
            Retorna a URL atual do driver.
        """

        return self.get_driver().current_url

    def get_element_value(self, selector:tuple[str, str]):
        """
            Retorna o valor inserido no elemento input.

            ### params
            * selector : seletor de elemento, uma tupla que especifique o tipo e a referência

            ### return
            * valor inserido no elemento input.
        """
        return self._driver.find_element(*selector).get_attribute("value")
    
    @retry(StaleElementReferenceException, tries=5, delay=1, backoff=2)
    def clickable(self, selector:tuple[str, str], long_wait=False, short_wait=False):
        """
            Retorna o elemento indicado pelo seletor caso ele seja clicável, o tempo de espera é indicado no constructor da classe.

            ### params
            * selector : seletor de elemento, uma tupla que especifique o tipo e a referência

            ### return
            * elemento indicado
        """
        wait = self._long_wait if long_wait else self._short_wait if short_wait else self._wait
     
        return wait.until(EC.element_to_be_clickable(selector))
   
    @retry(StaleElementReferenceException, tries=5, delay=1, backoff=2)
    def located(self, selector:tuple[str, str], long_wait=False, short_wait=False):
        """
            Retorna o elemento indicado pelo seletor caso ele seja localizado, o tempo de espera é indicado no constructor da classe.

            ### params
            * selector : seletor de elemento, uma tupla que especifique o tipo e a referência

            ### return
            * elemento indicado
        """

        wait = self._long_wait if long_wait else self._short_wait if short_wait else self._wait

        return wait.until(EC.presence_of_element_located(selector))
    
    def invisibity_located(self, selector:tuple[str, str]):
        """
            Aguarda a invisibilidade do elemento referenciado.

            ### params
            * selector : seletor de elemento, uma tupla que especifique o tipo e a referência
        """
        self._wait.until(EC.invisibility_of_element_located(selector))
    
    def visibility_located(self, selector:tuple[str, str], long_wait=False, short_wait=False):
        """
            Retorna o elemento indicado pelo seletor caso ele seja visível, o tempo de espera é indicado no constructor da classe.

            ### params
            * selector : seletor de elemento, uma tupla que especifique o tipo e a referência

            ### return
            * elemento indicado
        """
        wait = self._long_wait if long_wait else self._short_wait if short_wait else self._wait
        
        return self.wait.until(EC.visibility_of_element_located(selector))
    
    def select_clickable(self, selector, value):
        """
            Retorna o elemento indicado pelo seletor caso ele seja localizado, o tempo de espera é indicado no constructor da classe.

            ### params
            * selector : seletor de elemento, uma tupla que especifique o tipo e a referência

            ### return
            * elemento indicado
        """
        return Select(self._wait.until(EC.element_to_be_clickable(selector))).select_by_value(value)
        
    def is_visible_element(self, selector:tuple[str, str]):
        """
            Avalia se um elemento existe e é visible na página atual.

            ### params
            * selector : seletor de elemento, uma tupla que especifique o tipo e a referência

            ### return
            Booleano elemento está visible
        """

        try:
            el = self.get_driver().find_element(*selector)
            x = el.is_displayed()
            return x
        except:
            return False
        

    def get_element_text(self, selector:tuple[str, str]):
        """
            Retorna o texto de um elemento localizado.

            ### params
            * selector : seletor de elemento, uma tupla que especifique o tipo e a referência

        """

        return self.located(selector).text
        
        
    def __enter__(self):
        self.start()
        return self
    
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._driver.quit()
        except:
            pass
        if exc_type is not None:
            print(f'exc_type : {exc_type}')
        if exc_tb is not None:
            print(f'exc_tb   : {exc_tb}')
        
