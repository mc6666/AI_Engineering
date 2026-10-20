//const http = require("http");
const path = require("path");
const fs = require("fs");
const express = require("express");

const realtime_url = "https://api.openai.com/v1/realtime/translations/client_secrets";
const model = "gpt-realtime-translate";
const PORT = 5000;

const app = express();
// Serve static files from the 'public' folder
app.use(express.static(path.join(__dirname, 'public')));
// *** Crucial: Add middleware to parse incoming JSON request bodies
app.use(express.json()); 

app.get("/", (req, res) => {
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
    
app.post("/session", async (req, res) => {
  // console.log(req.body);
  const language = req.body.Language ?? "en";
  const response = await fetch(realtime_url,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
        "Content-Type": "application/json",
        "OpenAI-Safety-Identifier": "hashed-user-id",
      },
      body: JSON.stringify({
        session: {
          model: model,
          audio: {
            output: { language },
          },
        },
      }),
    }
  );

  res.status(response.status).json(await response.json());
});

app.listen(PORT, () => {
    console.log(
        `Server running at http://localhost:${PORT}`
    );
});