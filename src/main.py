import os; os.chdir(source_dir := os.path.dirname(os.path.abspath(__file__)))

from plugins.selenium.selenium import Selenium
from selenium.webdriver.common.by import By
from data_access.sqlite_estados import SQLiteEstados
from time import time
from typing import Callable

import pyexcel
import argparse
import traceback
import app
import pandas as pd
import string

def main(populate: bool, read_and_process: bool):
    app.logger.info("Starting Automation")
    start_time = time()
    
    if not any([populate, read_and_process]):
        app.logger.info("Nothing to do.")
        return
    
    if populate:
        app.logger.info("")
        app.logger.info("POPULATING/UPDATING TABLE")
        
        app.logger.info("Getting data from web")
        df_web  = get_web_dataframe()
        
        app.logger.info("Getting data from file")
        df_file = get_file_dataframe()

        app.logger.info("Merging both")
        df_inner = pd.merge(df_web, df_file, on="capital", how="inner") 
        
        app.logger.info("Uploading dataframe")
        db_path = os.path.join(".", "data_source", "estados_brasil.db")
        
        with SQLiteEstados(db_path) as table_estados:
            table_estados.upsert_df(df_inner)
            
    if read_and_process:
        app.logger.info("")
        app.logger.info("PROCESSING ITEMS")
        
        with SQLiteEstados(db_path) as table_estados:
            df = table_estados.read_all()
        
        app.logger.info("--------------------------------------------")
        app.logger.info("Generating top three populated regions")
        generate_top_3_populated_regions(df)
        
        app.logger.info("--------------------------------------------")
        app.logger.info("Generate regions n captals")
        generate_regions_n_captals(df)
        
        app.logger.info("--------------------------------------------")
        app.logger.info("generate_most_populated_state")
        generate_most_populated_state(df)
    
    
    app.logger.info("===================================================")
    app.logger.info("RESUME")
    app.logger.info(f"\tExecution time: {round(time()-start_time, 1)}s")
    app.logger.info("===================================================")
        
def generate_report(df: pd.DataFrame, transform: Callable[[pd.DataFrame], pd.DataFrame], output_path: str):
    """
    Generic function to generate a report.

    :param df: Input DataFrame.
    :param transform: A function that transforms the DataFrame for the report.
    :param output_path: The file path where the report will be saved.
    """
    transformed_df = transform(df)
    data_dict = transformed_df.to_dict(orient="records")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pyexcel.save_as(records=data_dict, dest_file_name=output_path)
    
def generate_most_populated_state(df:pd.DataFrame):
    try:
        df = df.nlargest(2, "populacao")[["estado", "capital", "populacao"]]
        file_path = os.path.join("..", "output", "estados_mais_populosos.xls")
        
        data_dict = df.to_dict(orient="records")
        pyexcel.save_as(records=data_dict, dest_file_name=file_path)
        
        app.logger.debug("\tSuccess")
    except Exception as e:
        app.logger.error(f"\tError: {e}")
    finally:
        app.logger.info("")
    
def generate_regions_n_captals(df:pd.DataFrame):
    try:
        df = df.groupby("regiao").size().reset_index(name="n_capitais")
        file_path = os.path.join("..", "output", "regioes_n_capitais.xls")

        data_dict = df.to_dict(orient="records")
        pyexcel.save_as(records=data_dict, dest_file_name=file_path)
        
        app.logger.info("\tSuccess")
    except Exception as e:
        app.logger.error(f"\tError: {e}")
    finally:
        app.logger.info("")
    
def generate_top_3_populated_regions(df:pd.DataFrame):
    try:
        df = df.groupby("regiao")["populacao"].sum().nlargest(3).reset_index()
        file_path = os.path.join("..", "output", "top3_regioes_populosas.csv")
        #top3_regioes.to_csv(os.path.join("..", "output", "top3_regioes_populosas.csv"), index=False)
        
        data_dict = df.to_dict(orient="records")
        pyexcel.save_as(records=data_dict, dest_file_name=file_path)
        
        app.logger.info("\tSuccess")
    except Exception as e:
        app.logger.error(f"\tError: {e}")
    finally:
        app.logger.info("")

def get_web_dataframe():
    try:
        with Selenium() as webdriver:
            webdriver.start()
            webdriver.go_to_url(app.config.source_url)
            
            app.logger.warning("Beware of the shark!!")
            
            driver = webdriver.get_driver()
            
            # Getting table element
            table   = driver.find_element(By.XPATH, "//table[@bgcolor='#ffffff']")
            columns = [header.text for header in table.find_elements(By.XPATH, "//th/span")]
            rows    = [row.find_elements(By.XPATH, "./td/span") for row in table.find_elements(By.XPATH, "//tbody/tr")]
            values  = [[cell.text for cell in row] for row in rows if row]
        
        # Treating DataFrame
        df = pd.DataFrame(values, columns=columns)[["Estado", "Capital", "Região"]]
        df.columns = ["estado", "capital", "regiao"]
        df = df.map(lambda x: x.title() if isinstance(x, str) else x)
        
        return df
    
    except Exception as e:
        app.logger.error(f"\n{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}\n")
        traceback.print_exc()
        raise e

def get_file_dataframe():
    try:
        file_path = os.path.join("..", "input", "PopulaçãoxCapital.xlsx")
        
        df = pd.read_excel(file_path)
        df.drop_duplicates(inplace=True)
        df[["capital", "populacao"]] = df["Capital/populacao"].str.split(":", expand=True)
        df.drop(columns=["Capital/populacao"], inplace=True)
        df["populacao"] = df["populacao"].str.replace(f"[{string.punctuation}]", "", regex=True).astype(int)
        
        return df
    
    except Exception as e:
        app.logger.error(f"\n{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}\n")
        traceback.print_exc()
        raise e

if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description="Capitals of Brazilian states")
    parser.add_argument("-P", "--populate", action="store_true", default=False, help="Insert new values ​​into the database")
    parser.add_argument("-R", "--read_and_process", action="store_true", default=False, help="Process items already existing in the database")
    args = parser.parse_args()
    
    app.redefine_config("app_config.yml")
    app.redefine_logger(app.get_logger_filename(app.config.bot_id))
    main(args.populate, args.read_and_process)
        

    