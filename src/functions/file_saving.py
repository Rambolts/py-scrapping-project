from functools import wraps
from typing import Callable
import pandas as pd
import os, app, pyexcel, traceback

def log_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            app.logger.info(f"\tStarting")
            result = func(*args, **kwargs)
            app.logger.info(f"\tSuccess")
            return result
        except Exception as e:
            app.logger.error(f"\tError: {e}")
            app.logger.error(f"\t{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}\n")
            raise
        finally:
            app.logger.info(f"")
    return wrapper

@log_execution
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
    
# Specific transformations for each report
def most_populated_state_transform(df: pd.DataFrame) -> pd.DataFrame:
    return df.nlargest(2, "populacao")[["estado", "capital", "populacao"]]

def regions_and_capitals_transform(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("regiao").size().reset_index(name="n_capitais")

def top_3_populated_regions_transform(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("regiao")["populacao"].sum().nlargest(3).reset_index()