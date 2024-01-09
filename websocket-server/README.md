# SmartGraph WebSocket server

## Overview

Code for the SmartGraph WebSocket server which allows the SmartGraph UI to run queries against the Neo4j database.

## Local Deployment

The run locally (not in docker) ensure that the SmartGraph Neo4J instance is running. Then follow these commands:

- Run `npm i` in the **websocket-server** directory
- Run `node websocket-server.ts` to run the server

The server runs on port 1338 by default but can be editted through the .env file in the root of the project.