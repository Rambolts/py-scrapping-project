from plugins.selenium.selenium import Selenium
from selenium.webdriver.common.by import By

import pandas as pd
import traceback, app, os, string

def get_web_dataframe() -> pd.DataFrame:
    try:
        with Selenium() as webdriver:
            webdriver.go_to_url(app.config.source_url)
            
            app.logger.warning("\tBeware of the shark!!")
            
            driver = webdriver.get_driver()
            
            # Getting table element
            app.logger.info("\tGetting table element...")
            table   = driver.find_element(By.XPATH, "//table[@bgcolor='#ffffff']")
            columns = [header.text for header in table.find_elements(By.XPATH, "//th/span")]
            rows    = [row.find_elements(By.XPATH, "./td/span") for row in table.find_elements(By.XPATH, "//tbody/tr")]
            values  = [[cell.text for cell in row] for row in rows if row]
            
        # Treating DataFrame
        app.logger.info("\tTreating DataFrame")
        df = pd.DataFrame(values, columns=columns)[["Estado", "Capital", "Região"]]
        df.columns = ["estado", "capital", "regiao"]
        df = df.map(lambda x: x.title() if isinstance(x, str) else x)
        
        app.logger.info("\tSuccessful")
        app.logger.info("")
        return df
    
    except Exception as e:
        app.logger.error(f"\n{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}\n")
        traceback.print_exc()
        raise e

def get_file_dataframe() -> pd.DataFrame:
    try:
        file_path = os.path.join("..", "input", "PopulaçãoxCapital.xlsx")
        
        app.logger.info(f"\tReading: {os.path.abspath(file_path)}")
        df = pd.read_excel(file_path)
        
        app.logger.info("\tTreating DataFrame")
        df.drop_duplicates(inplace=True)
        df[["capital", "populacao"]] = df["Capital/populacao"].str.split(":", expand=True)
        df.drop(columns=["Capital/populacao"], inplace=True)
        df["populacao"] = df["populacao"].str.replace(f"[{string.punctuation}]", "", regex=True).astype(int)
        
        app.logger.info("\tSuccessful")
        app.logger.info("")
        return df
    
    except Exception as e:
        app.logger.error(f"\n{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}\n")
        traceback.print_exc()
        raise e