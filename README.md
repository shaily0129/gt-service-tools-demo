# Testing API 

- 5 web-enabled services up and running so far!

- Run the file app.py located at `gt-service-tools`
  

- The application will be running at `http://0.0.0.0:8002/docs`
- /tools/triage
  ```shell
  {
    "request_id": "demo1",
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

- /tools/triage_category
  ```shell
  { "request_id": "demo1", "params": {"name":"Ted","triage_score":"78"} }
  ```
  
- /tools/patient_matrix
  ```shell
  {
  "patient_id": "demo1",
  "params": {
    "category": "minor"
   }
  }
  ```
  
- /tools/final_asset
  ```shell
    {
      "request_id": "demo1",
      "params": [
        {
          "patient_name": "Adrian Monk",
          "assets_possible": ["Black hawk HH60M", "Chinook CH47", "Chinook CH99", "Truck M1165", "Ambulance M997A3"],
          "triage_score": 20
        },
        {
          "patient_name": "Natalie Tieger",
          "assets_possible": ["Black hawk HH60M", "Chinook CH47", "Chinook CH99", "Truck M1165"],
          "triage_score": 10
        },
        {
          "patient_name": "Leland Stottlemeyer",
          "assets_possible": ["Black hawk HH60M", "Chinook CH47", "Chinook CH99", "Truck M1165"],
          "triage_score": 20
        }
      ]
    }
  ```

- /tools/final_cf
  ```shell
    {
      "request_id": "demo1",
      "params": [
        {
          "patient_name": "Adrian Monk",
          "care_facilities_possible": ["Battlefield Medical Center", "Noble Medical Center", "Young hearts Medical Center"],
          "triage_score": 20.0
        },
        {
          "patient_name": "Natalie Tieger",
          "care_facilities_possible": ["Battlefield Medical Center", "Noble Medical Center", "Young hearts Medical Center"],
          "triage_score": 10.0
        }
      ]
    }
    

  ```
  


