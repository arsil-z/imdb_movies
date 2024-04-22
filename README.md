# IMDB Movies

## Setup

Prerequisites:
1. You have docker installed in your machine.
2. You've cloned the service in your local machine.
3. You are in the root directory of the service.

This is a dockerized service so inorder to set it up locally we'll do the following steps:

1. Create docker network (required because there are multiple containers):
   `docker network create imdb_movies --subnet=10.10.0.0/24`
   
    If this gives permission error, try running with `sudo`

2. Now to run the service run the following command: 
   `docker compose up --build`


## Database Diagram
https://dbdiagram.io/d/imdb_movies_db_design-661f39ef03593b6b612e6dca

## File Processing Flow Architecture Diagram
https://drive.google.com/file/d/1FiNL740EwQ7MKAgYp5qCtZTbKh4iUMgE/view?usp=sharing

## REST APIs 

Both Postman collection and Environment can be imported for the ease of call the APIs.

Postman Collection:
https://drive.google.com/file/d/1wrj6CTwaHQOXdefhLRNgneaROcXvWKLP/view?usp=sharing

Postman Environment:
https://drive.google.com/file/d/15echWUp9xIHtdHPdztfYiywZ38zAfnJL/view?usp=sharing


## MongoDB Schema and Index
It's present in the `/schemas` directory


