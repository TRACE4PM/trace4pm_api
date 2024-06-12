# app

## Add your files

```
cd existing_repo
git remote add origin https://gitlab.univ-lr.fr/trace_clustering/app.git
git branch -M main
git push -uf origin main
```

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

    - Amira Ania DAHACHE

### Licence
The project is released under the L3i license.
