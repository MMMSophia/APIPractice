# OECD-Analysis--Extraction_and_Database
Code to extract data from OECD API, parse files, and create a relational database

* Software
  * Python 3.7.x
    * https://www.python.org/downloads/
  * MySQL Community Server
    * https://dev.mysql.com/downloads/mysql/

## Use OECD data to extract data via Python and load into a database for processing.
* OECD data API references
  * https://data.oecd.org/api/
  * https://data.oecd.org/api/sdmx-json-documentation/#d.en.330346
* Use Gender equality in entrepreneurship (GENDER_ENT1)
  * https://www.oecd-ilibrary.org/social-issues-migration-health/data/gender-equality/gender-equality-in-entrepreneurship_data-00723-en
  * https://stats.oecd.org/viewhtml.aspx?datasetcode=GENDER_ENT1&lang=en
  * Read JSON data from OECD Gender equality in entrepreneurship (GENDER_ENT1) API
    * https://stats.oecd.org/SDMX-JSON/data/GENDER_ENT1
* Load JSON data into MySQL database using Python
