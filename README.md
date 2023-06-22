# dataherald

Dataherald is a text-to-sql engine built for enteprise-level question answering over structured data. It allows you to set up an API from your database that can answer questions in plain English. You can use Dataherald to:

- Enable Q+A from your production DBs inside your SaaS application
- Allow business users to get insights from the data warehouse without going through a data analyst
- Create a ChatGPT plug-in from your proprietary data

... and many more!

Documentation

Discord

## Overview

### Background

LLMs are a phenomenal piece of technology, and the latest models have gotten very good at writing SQL. However we could not get existing frameworks to work with our structured data at a level which we could incorporate into our application. That is why we built and released this engine. 

### Goals

Dataherald is built to:

- Be easy to set up and add context
- Be able to answer complex queries
- Get better with usage
- Be fast


## Get Started

The simplest way to set up Dataherald is to use to create a managed deployment with a hosted API. We are rolling this service to select customers. Sign up for the waitlist <link>.

You can also self-host the engine locally. 


## Run Dataherald locally

To run Dataherald locally ...

## Contributing to Dataherald

Hello! We appreciate your interest in contributing to Dataherald. As a thriving company in the ever-evolving realm of data management, we warmly welcome any contributions you may have to offer. Whether you're inclined to develop new features, enhance our infrastructure, improve documentation, or squash pesky bugs, we are highly receptive to your ideas and expertise. Join us in our mission to revolutionize data handling, and together we can make a significant impact in this field. Thank you for considering becoming part of the Dataherald community!

It's essential that we maintain great documentation and testing. If you:

* Fix a bug
Add a relevant unit or integration test when possible. These live in tests/unit_tests # todo create a tests folder and configure to add unit tests


### Guidelines

To install requirements:
`pip3 install -r requirements.txt`


Code Formatting
To run formatting for this project:
`make format` # todo create a makefile and implement a formatting package

Linting
`make lint` # todo implement a lint command in the makefile

Coverage
`make coverage` # todo implement a coverage package

Testing
`make tests` # todo implement tests command in makefile
