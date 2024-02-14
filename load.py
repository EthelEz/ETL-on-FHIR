import os
from psycopg2 import sql
from transform import calculate_age, clean_text
from fhirpy import AsyncFHIRClient
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

api_url = os.environ["api_url"]

from access_token import get_access_token

# Function to load data into PostgreSQL
async def load_into_postgres(data, table_name, connection):
    token = await get_access_token()

    client = AsyncFHIRClient(
        api_url,
        authorization=f'Bearer {token}'
    )
    with connection.cursor() as cursor:
        # Creating the table if not exists
        create_table_query = sql.SQL("""
            CREATE TABLE IF NOT EXISTS {} (
                id SERIAL PRIMARY KEY,                                     
                date_reported DATE,
                date_authorised DATE,
                report_summary VARCHAR(255), 
                dob DATE, 
                age VARCHAR(10),
                gender VARCHAR(10), 
                race VARCHAR(15), 
                ethnicity VARCHAR(50), 
                blood_leukocytes_volume FLOAT,
                reason_code VARCHAR(10),  
                hospitalization_status VARCHAR(10), 
                blood_erythrocyte_volume FLOAT,
                blood_hemoglobin_volume FLOAT,
                blood_hematocrit_volume FLOAT,
                mcv_count FLOAT,
                mch_count FLOAT,
                mchc_count FLOAT,
                erythrocyte_distribution_width_count FLOAT,
                platelets_volume_count FLOAT,
                platelet_distribution_width FLOAT,
                platelet_mean_volume_count FLOAT
            )
        """).format(sql.Identifier(table_name))
        cursor.execute(create_table_query)

        # Inserting data into the table
        insert_query = sql.SQL("""
            INSERT INTO {} (date_reported, date_authorised, report_summary, dob, age, gender, race, ethnicity, blood_leukocytes_volume, reason_code, hospitalization_status, blood_erythrocyte_volume, blood_hemoglobin_volume, blood_hematocrit_volume, mcv_count, mch_count, mchc_count, erythrocyte_distribution_width_count, platelets_volume_count, platelet_distribution_width, platelet_mean_volume_count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """).format(sql.Identifier(table_name))

        for rep_data in data:

            blood_leukocytes_volume = None
            reason_code = None
            hospitalization_status = None
            blood_erythrocyte_volume = None
            blood_hemoglobin_volume = None
            blood_hematocrit_volume = None
            mcv_count = None
            mch_count = None
            mchc_count = None
            erythrocyte_distribution_width_count = None
            platelets_volume_count = None
            platelet_distribution_width = None
            platelet_mean_volume_count = None

            if rep_data is not None:
                date_reported = rep_data.get('effectiveDateTime')
                date_authorised = rep_data.get('issued')
                report_summary = rep_data.get('conclusion')

                patient_data = rep_data.get_by_path('subject.reference')
                if patient_data is not None and '/' in patient_data:
                    patient_id = patient_data.split('/')[1]
                    patients = await client.resources('Patient').search(_id=patient_id).fetch_all()
                    for patient in patients:
                        dob = patient.get('birthDate')
                        age = calculate_age(dob)
                        gender = patient.get('gender')
                        race = patient.get_by_path("extension.0.extension.0.valueCoding.code")
                        ethnicity = patient.get_by_path("extension.1.extension.0.valueCoding.code")
                        
                for observation in rep_data.get('result', []):
                    reference = observation.get('reference')
                    if reference:
                        obs_id = reference.split('/')[1]
                        blood = await client.resources('Observation').search(_id=obs_id).fetch_all()
                        if blood:
                            code = blood[0].get_by_path('code.coding.0.code')
                            value = blood[0].get_by_path('valueQuantity.value') 
                            # print(code, value)

                            # Extracting values based on observation codes
                            if code == "6690-2":  # Leukocytes
                                blood_leukocytes_volume = value
                            elif code == "789-8":  # Erythrocytes
                                blood_erythrocyte_volume = value
                            elif code == "718-7":  # Hemoglobin
                                blood_hemoglobin_volume = value
                            elif code == "4544-3":  # Hematocrit
                                blood_hematocrit_volume = value
                            elif code == "787-2":  # MCV
                                mcv_count = value
                            elif code == "785-6":  # MCH
                                mch_count = value
                            elif code == "786-4":  # MCHC
                                mchc_count = value
                            elif code == "21000-5":  # Erythrocyte distribution width
                                erythrocyte_distribution_width_count = value
                            elif code == "32207-3":  # Platelets
                                platelets_volume_count = value
                            elif code == "32207-3":  # Platelet distribution width
                                platelet_distribution_width = value
                            elif code == "32623-1":  # Platelet mean volume
                                platelet_mean_volume_count = value 

                            # Extracting encounter-related information
                            encounter_id = blood[0].get('encounter.reference')
                            if encounter_id is not None and '/' in encounter_id:
                                enc_id = encounter_id.split('/')[1]
                                encounters = await client.resources('Encounter').search(_id=enc_id).fetch_all()
                                for encounter in encounters:
                                    if encounter is not None and encounter.get_by_path("type.0.coding.0.code") == "50849002":
                                        reason_code = encounter.get_by_path("reasonCode.0.coding.0.code")
                                        hospitalization_status = encounter.get_by_path("hospitalization.dischargeDisposition.coding.0.code") 
                
                cursor.execute( insert_query, (date_reported, date_authorised, report_summary, dob, age, gender, race, ethnicity, blood_leukocytes_volume,
                            reason_code,  hospitalization_status, blood_erythrocyte_volume, blood_hemoglobin_volume, blood_hematocrit_volume,
                            mcv_count, mch_count, mchc_count, erythrocyte_distribution_width_count, platelets_volume_count, platelet_distribution_width, 
                            platelet_mean_volume_count))
                
    connection.commit()
























# for rep_data in data:
#     if rep_data is not None:
#         date_reported = rep_data.get('effectiveDateTime')
#         date_authorised = rep_data.get('issued')
#         report_summary = clean_text(rep_data.get('conclusion'))

#         patient_data = rep_data.get_by_path('subject.reference').split('/')[1]
#         patients = await client.resources('Patient').search(active=True, _id=patient_data).fetch_all()

#         for patient in patients:
#             dob = patient.get('birthDate')
#             age = calculate_age(dob)
#             gender = patient.get('gender')
#             race = patient.get_by_path("extension.0.0.valueCoding.code")
#             ethnicity = patient.get_by_path("extension.0.1.valueCoding.code")

#         leukocytes_id = rep_data.get_by_path('result.0.0')
#         blood_leukocytes = await client.resources('Observation').search(_id=leukocytes_id).fetch_all()
#         for blood in blood_leukocytes:
#             if blood is not None and blood.get_by_path('code.coding.0.code') == "6690-2":
#                 blood_leukocytes_volume = blood.get("valueQuantity.value")
#                 encounter_id = blood.get('encounter.reference')
#                 encounters = await client.resources('Encounter').search(_id=encounter_id).fetch_all()
#                 for encounter in encounters:
#                     if encounter is not None and encounter.get_by_path("type.0.coding.0.code") == "50849002":
#                         reason_code = encounter.get_by_path("reasonCode.0.coding.0.code")
#                         hospitalization_status = encounter.get_by_path("hospitalization.dischargeDisposition.coding.0.code")
        
#         erythrocyte_id = rep_data.get_by_path('result.0.1')
#         blood_erythrocytes = await client.resources('Observation').search(_id=erythrocyte_id).fetch_all()
#         for blood in blood_erythrocytes:
#             if blood is not None and blood.get_by_path('code.coding.0.code') == "789-8":
#                 blood_erythrocyte_volume = blood.get("valueQuantity.value")

#         hemoglobin_id = rep_data.get_by_path('result.0.2')
#         blood_hemoglobins = await client.resources('Observation').search(_id=hemoglobin_id).fetch_all()
#         for blood in blood_hemoglobins:
#             if blood is not None and blood.get_by_path('code.coding.0.code') == "718-7":
#                 blood_hemoglobin_volume = blood.get("valueQuantity.value")
        
#         hematocrit_id = rep_data.get_by_path('result.0.3')
#         blood_hematocrit = await client.resources('Observation').search(_id=hematocrit_id).fetch_all()
#         for blood in blood_hematocrit:
#             if blood is not None and blood.get_by_path('code.coding.0.code') == "4544-3":
#                 blood_hematocrit_volume = blood.get("valueQuantity.value")
        
#         mcv_id = rep_data.get_by_path('result.0.4')
#         mcv_counts = await client.resources('Observation').search(_id=mcv_id).fetch_all()
#         for blood in mcv_counts:
#             if blood is not None and blood.get_by_path('code.coding.0.code') == "787-2":
#                 mcv_count = blood.get("valueQuantity.value")

#         mch_id = rep_data.get_by_path('result.0.5')
#         mch_counts = await client.resources('Observation').search(_id=mch_id).fetch_all()
#         for blood in mch_counts:
#             if blood is not None and blood.get_by_path('code.coding.0.code') == "785-6":
#                 mch_count = blood.get("valueQuantity.value")  

#         mchc_id = rep_data.get_by_path('result.0.6')
#         mchc_counts = await client.resources('Observation').search(_id=mchc_id).fetch_all()
#         for blood in mchc_counts:
#             if blood is not None and blood.get_by_path('code.coding.0.code') == "786-4":
#                 mchc_count = blood.get("valueQuantity.value")     

#         erythrocyte_distribution_width_id = rep_data.get_by_path('result.0.7')
#         erythrocyte_distribution_width_counts = await client.resources('Observation').search(_id=erythrocyte_distribution_width_id).fetch_all()
#         for blood in erythrocyte_distribution_width_counts:
#             if blood is not None and blood.get_by_path('code.coding.0.code') == "21000-5":
#                 erythrocyte_distribution_width_count = blood.get("valueQuantity.value") 

#         platelets_volume_id = rep_data.get_by_path('result.0.8')
#         platelets_volume_counts = await client.resources('Observation').search(_id=platelets_volume_id).fetch_all()
#         for blood in platelets_volume_counts:
#             if blood is not None and blood.get_by_path('code.coding.0.code') == "32207-3":
#                 platelets_volume_count = blood.get("valueQuantity.value")
        
#         platelet_distribution_id = rep_data.get_by_path('result.0.9')
#         platelet_distribution_widths = await client.resources('Observation').search(_id=platelet_distribution_id).fetch_all()
#         for blood in platelet_distribution_widths:
#             if blood is not None and blood.get_by_path('code.coding.0.code') == "32207-3":
#                 platelet_distribution_width = blood.get("valueQuantity.value")

#         platelet_mean_volume_id = rep_data.get_by_path('result.0.10')
#         platelet_mean_volume_counts = await client.resources('Observation').search(_id=platelet_mean_volume_id).fetch_all()
#         for blood in platelet_mean_volume_counts:
#             if blood is not None and blood.get_by_path('code.coding.0.code') == "32623-1":
#                 platelet_mean_volume_count = blood.get("valueQuantity.value")



            

    
