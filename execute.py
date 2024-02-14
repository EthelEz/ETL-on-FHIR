from extract import extract_from_fhir_api
from transform import transform_data
import psycopg2
import os
from load import load_into_postgres
from access_token import get_access_token
from dotenv import load_dotenv, find_dotenv
import asyncio

_ = load_dotenv(find_dotenv())

api_url = os.environ["api_url"]
database = os.environ["database-name"]
user = os.environ["user"]

# Main ETL process
async def main():
    token = await get_access_token()

    postgres_connection_params = {
        'host': 'localhost',
        'database': database,
        'user': user,
        'password': '',
        'port': '5432'
    }
    table_name = 'fhir_etl_data'

    # Extract data from FHIR API
    data = await extract_from_fhir_api(api_url, token=token)
    # print(data)

    # Transform data
    transformed_data = transform_data(data)

    # Load data into PostgreSQL
    with psycopg2.connect(**postgres_connection_params) as connection:
        await load_into_postgres(transformed_data, table_name, connection)

if __name__ == '__main__':
    print("[ETL] Start")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print("[ETL] End")
