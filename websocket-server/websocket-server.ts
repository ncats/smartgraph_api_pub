"use strict";

const path = require("path");
const neo4j = require("neo4j-driver");
const webSocketServer = require("websocket").server;
const http = require("http");

const envPath = path.resolve(process.cwd(), "..", ".env");
require("dotenv").config({ path: envPath });

const neo4jUser = process.env["neo4j_user"];
const neo4jPassword = process.env["neo4j_password"];
const neo4jHost = `bolt://${process.env["neo4j_host"]}:${process.env["neo4j_port_bolt"]}`;
const driver = neo4j.driver(
    neo4jHost,
    neo4j.auth.basic(neo4jUser, neo4jPassword),
    { connectionPoolSize: 50 }
);

const webSocketsServerPort = process.env["sg_websocket_server_port"] || 1338;
const basePath = process.env["sg_websocket_base_path"] || "/";
process.title = "smartgraph-websocket-server";

function startWebSocketServer() {
    let server = http.createServer(function (request, response) { });
    server.listen(webSocketsServerPort, function () {
        console.log(
            new Date() + " Server is listening on port " + webSocketsServerPort
        );
    });

    let wsServer = new webSocketServer({
        httpServer: server,
        path: basePath,
    });

    wsServer.on("request", function (request) {
        console.log(new Date() + " Connection requested from remote address '" + request.remoteAddress + "' at origin '" + request.origin + "'");

        // accept connection - you should check 'request.origin' to make sure that
        // client is connecting from your website
        // (http://en.wikipedia.org/wiki/Same_origin_policy)
        let connection = request.accept(null, request.origin); // TODO: This needs to be changed to be more restrictive.
        console.log(new Date() + " Connection accepted");
    
        // user sent some message
        connection.on("message", function (message) {
            console.log(new Date() + " Received message from remote address '" + request.remoteAddress + "' at origin '" + request.origin + "'. Message: \n" + message.utf8Data + '\n');
            try {
                let mes = JSON.parse(message.utf8Data);
                let params;
                if (typeof mes.params.qParam == "number") {
                    params = { qParam: neo4j.int(mes.params.qParam) };
                } else {
                    params = mes.params;
                }
                const session = driver.session();
                session.run(mes.message, params).subscribe({
                    onNext: result => {
                        let ret;
                        //parse results based on query type
                        switch (mes.type) {
                            case "compoundSearch":
                            case "targetSearch": {
                                ret = {
                                    type: mes.type,
                                    data: {
                                        display: result._fields[0],
                                        value: result._fields[1],
                                    },
                                };
                                break;
                            }
                            default: {
                                ret = { type: mes.type, data: result };
                                break;
                            }
                        }
                        connection.send(JSON.stringify(ret));
                    },
                    onCompleted: (summary) =>{
                        if (mes.type == "counts") {
                            connection.send(JSON.stringify({ type: "counts" }));
                        } else {
                            connection.send(JSON.stringify({ type: "done" }));
                        }
                        session.close();
                    },
                    onError: error =>{
                        console.log(error);
                        connection.send(JSON.stringify({ type: 'error', error: error }));
                    },
                });
            } catch (err) {
                console.error("Failed to handle WebSocket message:", err);
                connection.send(JSON.stringify({ type: 'error', error: err }));
            }
        });
    
        // user disconnected
        connection.on("close", function (/*connection*/) { // Remove the 'connection' parameter as it's not used.
            console.log(new Date() + " Peer " + request.remoteAddress + " disconnected.");
        });
    });
}

async function main() {
    // Check environment variables
    if (!neo4jUser || !neo4jPassword || !neo4jHost) {
        console.error(new Date() + " - Required environment variables are missing.");
        process.exit(1);
    }

    const MAX_ATTEMPTS = 5;
    const TIMEOUT = 15000; // 15 seconds in milliseconds

    for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
        const session = driver.session();
        try {
            console.log(new Date() + ` - Attempting to connect to Neo4j at ${neo4jHost}...`)
            await session.run('MATCH (n) RETURN n LIMIT 1'); // Simple query to test connection
            console.log(new Date() + ` - Connected to Neo4j successfully on attempt ${attempt} at ${neo4jHost}`);
            session.close();
            break;
        } catch (error) {
            session.close();
            if (attempt === MAX_ATTEMPTS) {
                console.error(new Date() + ` - Failed to connect to Neo4j after ${MAX_ATTEMPTS} attempts.`);
                process.exit(1); // Exit with error after all attempts
            } else {
                console.warn(new Date() + ` - Connection attempt ${attempt} failed. Retrying in ${TIMEOUT / 1000} seconds...`);
                await new Promise(resolve => setTimeout(resolve, TIMEOUT));
            }
        }
    }

    // Test Neo4j connection & start WebSocket server
    const session = driver.session();
    try {
        await session.run('MATCH (n) RETURN n LIMIT 1'); // Simple query to test connection
        console.log(new Date() +  ` - Connected to Neo4j successfully at ${neo4jHost}`);
        session.close();

        // Start the WebSocket server only after verifying the Neo4j connection
        startWebSocketServer();
    } catch (error) {
        console.error(new Date() + ` - Failed to connect to Neo4j  at ${neo4jHost}:`, error);
        session.close();
        driver.close();
        process.exit(1); // Exit with error
    }

    // Graceful shutdown
    process.on("SIGINT", async () => {
        console.log("Gracefully shutting down...");
        driver.close();
        process.exit();
    });
}

// Start by testing the Neo4j connection
main();
