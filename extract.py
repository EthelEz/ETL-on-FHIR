from fhirpy import AsyncFHIRClient

async def extract_from_fhir_api(api_url, token):
    """
    Here's what each part of the query does:

    await client.resources('DiagnosticReport'): This specifies that we want to fetch resources of the type DiagnosticReport.

    .include('DiagnosticReport', 'subject', target_resource_type='Patient'): This instructs the FHIR server to include Patient resources related to each DiagnosticReport resource retrieved. The 'subject' field in DiagnosticReport resources typically references the patient associated with the report. By specifying target_resource_type='Patient', we're indicating that we want to include Patient resources specifically.

    .include('DiagnosticReport', 'result', target_resource_type='Observation'): This instructs the FHIR server to include Observation resources related to each DiagnosticReport resource retrieved. The 'result' field in DiagnosticReport resources typically references the observations that are the result of the diagnostic report. By specifying target_resource_type='Observation', we're indicating that we want to include Observation resources specifically.

    .fetch_all(): This executes the query and retrieves all DiagnosticReport resources along with their related Patient and Observation resources as specified.
    """
    client = AsyncFHIRClient(
        api_url,
        authorization=f'Bearer {token}'
    )

    # bundle = await client.resources('DiagnosticReport').include('DiagnosticReport', 'subject', target_resource_type='Patient').fetch_all()
    bundle = await client.resources('DiagnosticReport').include('DiagnosticReport', 'subject', target_resource_type='Patient').include('DiagnosticReport', 'result', target_resource_type='Observation').fetch_all()
    return bundle