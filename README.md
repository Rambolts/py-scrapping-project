
# **Capitals of Brazilian States - RPA Automation**

This repository contains an automation script developed in Python 3.12.7 that integrates data about Brazilian states, capitals, and regions. The script collects, processes, and stores the data in a SQLite database and generates reports in Excel and CSV formats.

## **Features**
- Fetches data from the web and files.
- Merges and uploads data into a SQLite database.
- Generates reports for:
  - **Top three most populated regions**.
  - **Number of capitals in each region**.
  - **Most populated states and their capitals**.
- Logs all operations for transparency and debugging.

---

## **Installation**

### **Prerequisites**
- Python 3.12.7
- The following Python libraries:
  - `pandas`
  - `selenium`
  - `pyexcel`
  - `sqlite3`

### **Setup**
1. Clone this repository:
   ```bash
   git clone https://github.com/Rambolts/py-scrapping-project.git
   cd py-scrapping-project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure the `app_config.yml` file is properly configured.

---

## **Usage**

Run the script using the following commands:

### **Populate the Database**
Fetch data from the web and a local file, merge the data, and insert it into the SQLite database.
```bash
python main.py --populate
```

### **Read and Process Existing Data**
Generate reports based on the data stored in the database.
```bash
python main.py --read_and_process
```

### **Both Populate and Process**
Execute both operations:
```bash
python main.py --populate --read_and_process
```

---

## **Reports**

The following reports are generated in the `output` directory:

1. **Most Populated States**:
   - File: `estados_mais_populosos.xls`
   - Contains the top two states with the most populated capitals.

2. **Regions and Capitals**:
   - File: `regioes_n_capitais.xls`
   - Shows the number of capitals per region.

3. **Top Three Populated Regions**:
   - File: `top3_regioes_populosas.csv`
   - Highlights the top three regions with the highest total population.

---

## **Code Structure**

- `main.py`: Entry point for the script.
- `data_access/sqlite_estados.py`: Handles state database interactions specifically.
- `functions/extraction.py`: Contains functions for data extraction.
- `functions/file_saving.py`: Manages report generation and file saving.
- `app`: Configuration and logger management.

### **Plugins**

- `plugins/selenium/selenium.py`: A custom Selenium wrapper class with advanced configurations for browser automation. Features include:
  - Integration with CapSolver for CAPTCHA solving.
  - Configurable browser options for better automation control.
  - Utilities for handling alerts, waits, and actions within Selenium.
  
- `plugins/sqlite/table.py`: A reusable SQLite table abstraction with the following features:
  - Bulk execution of SQL commands (`executemany`).
  - Query execution and result retrieval as pandas DataFrames.
  - Transaction handling with `commit` and `rollback`.
  - Context manager support (`__enter__` and `__exit__`).

### **Additional Notes**
The plugins directory contains reusable components that enhance functionality and modularity, allowing for easy integration and customization for various tasks.

---

## **Logging**

Logs are automatically generated during execution and can be configured in the `app_config.yml` file. Logs include detailed information about:
- Data fetching.
- Database operations.
- Report generation.

---

## **License**
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## **Contact**

For any questions or contributions, feel free to open an issue or submit a pull request.
