# Testing API 

- Run the file app_triageScore.py located at `gt-service-tools`
  
![image](https://github.com/user-attachments/assets/a259e447-a97e-4830-99d1-69cf5b6352c2)

- The application will be running at `http://0.0.0.0:8002/docs`
- /tools/triage
  ```shell
  {
    "request_id": "demo123",
    "patients": [
        {
            "patient_id": "patient1",
            "params": {
                "external_hemorrhage": 3.0,
                "tension_pneumothorax": 4.0,
                "traumatic_brain_injury": 6.0,
                "burn": 2.0,
                "gcs": 10.0,
                "sbp": 60.0,
                "rr": 20.0
                     }
        },
        {
            "patient_id": "patient2",
            "params": {
                "splenic_laceration": 6.0,
                "gcs": 6.0,
                "sbp": 100.0,
                "rr": 40.0
            }
        }
    ]
  }
  ```
  - Make sure to change the request_id and patient_id as they are unique
  - The result is displayed based on highest triage score
  - Any number of patients can be added to the list!
 
- /tools/triage/scores
  ```shell
   [
    "patient1",
    "patient2"
   ]
  ```
  - Make sure to add patient_id that already existed else empty list
  - The result is displayed based on highest triage score

