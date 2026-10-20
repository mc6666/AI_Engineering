const http = require("http");
const path = require("path");
const fs = require("fs");
//const express = require("express");

//const app = express();
const realtime_url = "https://api.openai.com/v1/realtime/translations/client_secrets";
const model = "gpt-live-transcribe";
const PORT = 3000;

// app.get("/", async (req, res) => {
const server = http.createServer(async (req, res) => {
    if (req.method === 'POST' && req.url === '/session') {
      const language = "en";

      const response = await fetch(
        "https://api.openai.com/v1/realtime/translations/client_secrets",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
            "Content-Type": "application/json",
            "OpenAI-Safety-Identifier": "hashed-user-id",
          },
          body: JSON.stringify({
            session: {
              model: "gpt-realtime-transcribe",
              audio: {
                output: { language },
              },
            },
          }),
        }
      );

      // res.status(response.status).json(response.json());
      res.writeHead(200);
      res.end(await response.json());
    }
    
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
    
// app.post("/session", async (req, res) => {
  // const language = req.body.targetLanguage ?? "en";

  // const response = await fetch(
    // "https://api.openai.com/v1/realtime/translations/client_secrets",
    // {
      // method: "POST",
      // headers: {
        // Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
        // "Content-Type": "application/json",
        // "OpenAI-Safety-Identifier": "hashed-user-id",
      // },
      // body: JSON.stringify({
        // session: {
          // model: "gpt-realtime-transcribe",
          // audio: {
            // output: { language },
          // },
        // },
      // }),
    // }
  // );

  // res.status(response.status).json(await response.json());
// }

// app.listen(3000, () => console.log("Server running on port 3000"));
server.listen(PORT, () => {
    console.log(
        `Server running at http://localhost:${PORT}`
    );
});