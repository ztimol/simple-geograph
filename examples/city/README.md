

### Steps to run this example:

1. Install docker and docker compose

2. `./devops/scripts/setup.sh`

3. Load `nyc_subway_sql_2025-07-25.backup` into the postgres user and database 

4. Initialise your python environment and install the requirements in 'app/requirements.txt'

5. `pip install -e [path to simple-geograph diretory]`

6. run `main.py` in the app directory


### The geospatial query

As part of running the script it's important to understand the query in `nyc_subway.sql`. The query generates the data required for the transform algorithm to work.




Source for subway data: https://www.crunchydata.com/blog/postgis-for-newbies
