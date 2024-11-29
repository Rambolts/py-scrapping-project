class Frame():
    def __init__(self, driver, selector:tuple[str, str]):
        """
            # Frame
            Icorpora um frame em uma página web, como uma classe. 
            De modo a otimizar e facilitar o manuseio de maneira mais visível e fluida.    
        
            ### Params
            * driver : Objeto WebDriver que estiver em uso no momento
            * selector : Seletor de elemento, uma tupla que especifique o tipo e a referência
        """
        self._selector = selector
        self._driver   = driver
        self._element  = self._driver.find_element(*self._selector)
        assert self._element.tag_name == 'iframe', "O elemento indicado não é um Frame."
        
        self._driver.switch_to.default_content()

    def switch_to(self):
        return self._driver.switch_to.frame(self._element)

    def __enter__(self):
        self.switch_to()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._driver.switch_to.default_content()