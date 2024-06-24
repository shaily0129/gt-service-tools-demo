# MCP

## Overview Test
The goal of this framework is to define a flexible approach for enabling a library of Triage 
Algorithms, whilst defining common structures, enabling the application to be scaffolded whilst the algortithms are in development.

### Triage Algorithms
In emergency medical care, triage algorithms play a crucial role in prioritizing patient care based on the severity of their condition and the available resources. Here's a summary of triage algorithms in emergency medical care:
Triage algorithms vary in complexity and scope, ranging from basic systems that categorize patients into priority levels (e.g., "urgent," "non-urgent") to advanced algorithms that consider multiple vital signs, patient history, and injury mechanisms to determine the appropriate level of care.
Common triage algorithms include the Simple Triage and Rapid Treatment (START) algorithm, the JumpSTART algorithm for pediatric patients, the Manchester Triage System (MTS), the Canadian Triage and Acuity Scale (CTAS), and the Emergency Severity Index (ESI), among others.
These algorithms may be tailored for specific environments, such as mass casualty incidents, emergency departments, or pre-hospital settings.

Triage algorithms typically assess patients based on various factors, including vital signs (e.g., heart rate, respiratory rate, oxygen saturation), chief complaints, mechanism of injury, and potential for deterioration.
They often use a combination of objective measurements and subjective assessments to assign patients to different triage categories.
Some algorithms prioritize rapid assessment and treatment (e.g., START), while others focus on comprehensive evaluations to ensure appropriate resource allocation (e.g., CTAS).

The landscape of emergency medical care is dynamic, with evolving patient needs, clinical guidelines, and resource availability.

A flexible framework for enabling a library of triage algorithms within an application allows healthcare providers to adapt to changing circumstances and tailor triage protocols to their specific needs.
Such a framework facilitates the integration of new algorithms as they are developed or modified, ensuring that PRCC teams have access to the most appropriate and up-to-date triage tools.

![Triage.png](./gt-service-tools/docs%2FTriage.png)

![Triage2.png](docs%2FTriage2.png)

Triage algorithms are essential tools in emergency medical care, providing structured approaches to prioritize patient care based on the severity of their condition. 
A flexible framework for enabling a library of triage algorithms within an application ensures that we can evolve the algorithms whilst scaffolding the rest of the application

## Approach
The framework has at its core the TriageFactory.  This Class is responsible for initialising
all algorithms in a consistant approach.  The Factory, as the name suggests, is built o

![Sw-TriageFramework.png](docs%2FSw-TriageFramework.png)


## Algo Developers
Simwerx has engaged with a University to provide a rules based approach for defining TriageScores
It is expected that the development team will conform to the framework and add their specific implementation into the library
To do this they need to do follow the following threestep process following:

* Create a folder in the service_triage folder and name the older algo_triage_XXX, where XXX represents their algo name
* Implement their Triage Algo Class that implements the class called Triage.  This class has a method named triage that expects as input a patient and returns a TriageScore
    ```
    class Triage:
        def triage(self, patient: Patient) -> TriageScore:
            raise NotImplementedError("Subclasses must implement triage method.")
    ```

* Update the FactoryAlgoTriage class an insert their Algo Name into the Factory, ensuring to add to the TriageAlgoName ENUM types
    ![Factory.png](docs/Factory.png)


## Key Design Considerations
* Factory Approach for Algo Instantiation
* Flexible Approach needed for modelling a Patient
* Formality required for input and output of the Triage Process
* Looking to bake in explainability for the Triage Score From Day 1


## Notes
It is very likely that this framework needs to be extended.  As the needs arise, please discuss the classes and method definitions with the 
approppriate technical owner from Simwerx.






