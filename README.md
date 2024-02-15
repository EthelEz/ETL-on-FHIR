# Project description
Fast Healthcare Interoperability Resources (FHIR) revolutionizes data exchange in healthcare, enhancing interoperability across systems. One of the reasons for performing ETL by moving data from an FHIR API to a Postgres database is to enable better data management, analysis, and utilization, ultimately improving healthcare workflows and patient care.

# Getting started
To demonstrate the extraction, transformation, and loading of data from an Azure FHIR API to a PostgresDB. It is advisable to understand why you want to perform the ETL. Secondly, it's good to know the following:
1. FHIR Standards:
Familiarize yourself with the Fast Healthcare Interoperability Resources (FHIR) standard using the [FHIR Documentation](https://fhir-ru.github.io/documentation.html). However, a good knowledge of [FHIR resources RESTful APIs, searching and the principles](https://fhir-ru.github.io/search.html) of data exchange in healthcare is important.

2. Knowledge of Postgres Database and queries:
Understanding [postgres](https://www.postgresql.org/docs/) is very important such you can [interact and connect](https://www.psycopg.org/docs/sql.html) using `Python`.
3. Choose or set up a FHIR server to interact with FHIR resources. You can use public servers like [HAPI FHIR](http://hapi.fhir.org/baseR4), or [set up your own](https://github.com/gosh-dre/ucl-fhir-hack/blob/master/docker-compose.yml). In our case, we are going to use [Azure API for FHIR](https://learn.microsoft.com/en-us/azure/healthcare-apis/fhir/) provided by GOSH.
4. Choose a FHIR Client framework:
Utilize FHIR client libraries in [Python](https://docs.smarthealthit.org/client-py/) in your chosen programming language. These libraries simplify the process of working with FHIR data management. In our case, we are using [fhirpy](https://github.com/beda-software/fhir-py#readme)

# Setting the ETL process
1. To be able to perform this, set up your FHIR server as discussed above.
2. Download your synthetic data from [synthea](https://mitre.box.com/shared/static/ydmcj2kpwzoyt6zndx4yfz163hfvyhd0.zip)
3. If you are using Azure API for FHIR use [FhirLoader](https://github.com/hansenms/FhirLoader) as recommended by Microsoft Azure to upload it to the API.
4. Else, if you are using your own Hapi FHIR, [upload](https://rajvansia.com/synthea-hapi-fhir.html) your data as described by the author.
     Here the process of ETL will change with some variations, which is to be updated later.
5. Download and set Postgres in your system.
     ```
     This can be done by creating a database and the equivalent user profile.
     ```
7. Download this repository `git clone https://github.com/EthelEz/ETL-on-FHIR.git` in your preferred directory.
8. Install necessary packages by running `python -r requirements.txt`
9. Create `.env` file and add
     ```
     api_url="add-your-azure-fhir-url-here"
     client_id="add-client-id-here"
     client_secret="add-client-secret-here"
     tenant_id="add-client-tenant_id-here"
     database="add-your-database-name-here"
     user="add-your-user-here"
     ```
10. If the setup and every other thing is installed correctly, then run `python execute.py` to perform the ETL.
    
      **Please Note** This process takes about 15 to 20 minutes to run. This is due to the size of the dataset we're extracting from the API and loading to Postgres.
