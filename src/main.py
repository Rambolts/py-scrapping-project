import os; os.chdir(source_dir := os.path.dirname(os.path.abspath(__file__)))

from data_access.sqlite_estados import SQLiteEstados
from functions.extraction import *
from functions.file_saving import *
from time import time

import argparse
import app
import pandas as pd

def main(populate: bool, read_and_process: bool):
    app.logger.info("Starting Automation")
    start_time = time()
    
    if not any([populate, read_and_process]):
        app.logger.info("Nothing to do.")
        return
    
    if populate:
        app.logger.info("")
        app.logger.info("POPULATING/UPDATING TABLE\n")
        
        app.logger.info("Getting data from web")
        df_web  = get_web_dataframe()
        
        app.logger.info("Getting data from file")
        df_file = get_file_dataframe()

        app.logger.info("Merging both")
        df_inner = pd.merge(df_web, df_file, on="capital", how="inner") 
        app.logger.info("")
        
        app.logger.info("Uploading dataframe")
        db_path = os.path.join(".", "data_source", "estados_brasil.db")
        app.logger.info("")
        
        with SQLiteEstados(db_path) as table_estados:
            table_estados.upsert_df(df_inner)
            
    if read_and_process:
        app.logger.info("")
        app.logger.info("PROCESSING ITEMS\n")
        
        with SQLiteEstados(db_path) as table_estados:
            df = table_estados.read_all()
        
        app.logger.info("--------------------------------------------")
        app.logger.info("Generating top three populated regions")
        generate_report(
            df,
            transform=most_populated_state_transform,
            output_path=os.path.join("..", "output", "estados_mais_populosos.xls")
        )
        
        app.logger.info("--------------------------------------------")
        app.logger.info("Generate regions n captals")
        generate_report(
            df,
            transform=regions_and_capitals_transform,
            output_path=os.path.join("..", "output", "regioes_n_capitais.xls")
        )
        
        app.logger.info("--------------------------------------------")
        app.logger.info("generate_most_populated_state")
        generate_report(
            df,
            transform=top_3_populated_regions_transform,
            output_path=os.path.join("..", "output", "top3_regioes_populosas.csv")
        )
 
    app.logger.info("")
    app.logger.info("===================================================")
    app.logger.info("RESUME")
    app.logger.info(f"\tExecution time: {round(time()-start_time, 1)}s")
    app.logger.info("===================================================")

if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description="Capitals of Brazilian states")
    parser.add_argument("-P", "--populate", action="store_true", default=False, help="Insert new values ​​into the database")
    parser.add_argument("-R", "--read_and_process", action="store_true", default=False, help="Process items already existing in the database")
    args = parser.parse_args()
    
    app.redefine_config("app_config.yml")
    app.redefine_logger(app.get_logger_filename(app.config.bot_id))
    
    main(args.populate, args.read_and_process)