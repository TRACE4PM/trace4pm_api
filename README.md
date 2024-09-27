# TRACE4PM API 

TRACE4PM is an API designed to model user behaviors within information systems by leveraging advanced process mining techniques. With a strong focus on trace clustering, TRACE4PM enables efficient discovery and analysis of user interaction patterns.
The API integrates a fully automated pipeline, streamlining the process from raw data parsing to process modeling. TRACE4PM offers four dedicated micro-services:
- Parser Service: Prepares and structures the input data, ensuring it's ready for further analysis.
- Tagger Service: Automatically tags events with relevant metadata to enrich the process mining results.
- Trace Clustering Service: Groups traces into meaningful clusters, facilitating deeper insights into user behavior patterns.
- Process Modeler Service: Generates process models based on the clustered traces or on the whole event logs, providing clear visual representations of the discovered processes.


## Installation and Configuration

**Pre-requisites**: 
- Ensure that Docker is installed on your machine.
- **Installation**:
- Clone the repository to your local machine.
- Navigate to the project directory and run the following command in your terminal to build the images and start the Docker containers:
`docker-compose up`
- **Adding a New Microservice**
- This project is based on a microservices architecture.
To add a new microservice you have to : 
- Add the link to the service's Git repository in the Poetry configuration file (pyproject.toml) under the [tool.poetry.dependencies] section. For example:
`discover = {git = "https://gitlab.univ-lr.fr/trace_clustering/services/clustering.git"}`
- **Adding a New API Route**
- Create a new Python file in the src/routers directory with the desired API.
- Include the router in src/main.py.


## Description
This project is a based on a microservices architecture where we communicate with the services using FASTAPI.
The purpose of this project is the development of a platform to model users' behaviors in e-learning platforms such as moodle 
based on their navigation traces, using process mining and different trace clustering techniques.


### Author(s)

    - Marwa Trablesi Hamdi
    - Ronan Champagnat
    - Cyrille Suire
    - Amira Ania DAHACHE


