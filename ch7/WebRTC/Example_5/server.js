const http = require("http");
const path = require("path");
const fs = require("fs");
const WebSocket = require("ws");

const PORT = 3000;

const server = http.createServer((req, res) => {
    // 讀取 public\index.html
    let filePath;
    if (req.url === "/") {
        filePath = path.join(__dirname, "public", "index.html");
    } else {
        filePath = path.join(__dirname, "public", req.url);
    }

    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(404);
            res.end("Not Found");
            return;
        }

        const ext = path.extname(filePath);

        const contentType = {
            ".html": "text/html",
            ".js": "application/javascript",
            ".css": "text/css"
        }[ext] || "text/plain";

        res.writeHead(200, {
            "Content-Type": contentType
        });

        res.end(data);
    });
});

// 建立 WebSocket 伺服器
const wss = new WebSocket.Server({
    server
});

let clients = [];
wss.on("connection", (ws) => {
    clients.push(ws);
    console.log("Client connected");
    ws.on("message", (message) => {
        console.log("Signal:", message.toString());
        // Forward signaling message to other clients
        clients.forEach((client) => {
            if (client !== ws &&
                client.readyState === WebSocket.OPEN) {
                client.send(message.toString());
            }
        });
    });

    ws.on("close", () => {
        clients = clients.filter(
            client => client !== ws
        );
        console.log("Client disconnected");
    });
});

server.listen(PORT, () => {
    console.log(
        `Server running at http://localhost:${PORT}`
    );
});