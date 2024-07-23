@app.post("/tools/triage", tags=["Triage"])
async def rate_response(
    request: Request, body: TriageRequestBody = Body(...)
) -> dict:
    try:
        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-triage-{body.request_id}"

        # Step 2. Handle single patient input by converting it to a list
        if isinstance(body.patients, PatientParams):
            patients = [body.patients]
        else:
            patients = body.patients

        results = []
        for patient in patients:
            # Create TriageInteractionRequest for each patient
            triage_interaction_request = TriageInteractionRequest(
                request_id=body.request_id, patient_id=patient.patient_id, params=patient.params
            )

            # Check for new or complete interaction request
            cached_bir_json = caching_manager.get_json(key)
            if cached_bir_json is None:
                caching_manager.save_json(key, triage_interaction_request.json())
            else:
                cached_bir = TriageInteractionRequest(**cached_bir_json)
                if cached_bir.complete:
                    results.append(cached_bir)
                    continue

            # Interaction request is still WIP, so run the triage algorithm and cache result
            bir = TriageScoreInteraction(thresholds=thresholds_data_algo3).run_triage_algo(
                triage_interaction_request=triage_interaction_request
            )

            # Save the result and add to results
            caching_manager.save_json(key, bir.json())
            results.append(bir)

        # Sort results by score
        sorted_results = sorted(results, key=lambda x: x.triage_score.score, reverse=True)

        return {"results": sorted_results}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
