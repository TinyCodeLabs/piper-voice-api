import express from "express";
import net from "net";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { randomUUID } from "crypto";
import { config } from "dotenv";
config();

const app = express();
app.use(express.json());

const SOCKET_PATH = "/app/run/tts.sock";
const OUTPUT_DIR = "/app/out";
const VOICES_DIR = "/app/voices";
const VOICES_IMPORT = "/app/voices_import";
const DELETE_SEC = process.env.DELETE_SECONDS || 1000;
console.log("Deleting files", DELETE_SEC, "after they are created");
const PORT = 3000;

// __dirname replacement for ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// --------------------
// In-memory job store
// --------------------
const jobs = new Map();
const queue = [];
let isProcessing = false;
let deleteFiles = [];

// --------------------
// Queue processor
// --------------------
async function processQueue() {
  if (isProcessing || queue.length === 0) return;

  isProcessing = true;
  const job = queue.shift();

  try {
    jobs.get(job.id).status = "processing";
    await sendToTTS(job.payload);
    deleteFiles.push({ job, filename: job.payload.output, added: Date.now() });
    jobs.get(job.id).status = "done";
  } catch (err) {
    jobs.get(job.id).status = "error";
    jobs.get(job.id).error = err.message;
  }

  isProcessing = false;
  processQueue();
}

async function collectGarbage() {
  const now = Date.now();
  const keep = [];

  for (const file of deleteFiles) {
    const age = (now - file.added) / 1000;

    if (age > DELETE_SEC) {
      console.log("🗑 deleting:", file.job.id);

      try {
        fs.unlink(path.join(OUTPUT_DIR, file.filename), (err) => {
          if (err && err.code !== "ENOENT") {
            console.error(err);
          }
        });
      } catch (err) {
        if (err.code !== "ENOENT") {
          console.error(err);
        }
      }
    } else {
      keep.push(file);
    }
  }

  deleteFiles = keep;
}
// --------------------
// Unix socket communication
// --------------------
function sendToTTS(payload) {
  return new Promise((resolve, reject) => {
    const client = net.createConnection(SOCKET_PATH);

    let buffer = "";

    client.on("connect", () => {
      client.write(JSON.stringify(payload));
    });

    client.on("data", (data) => {
      buffer += data.toString();

      try {
        // Try parsing as soon as possible
        const response = JSON.parse(buffer);
        client.destroy(); // Close connection manually

        if (response.status === "ok") {
          resolve(response);
        } else {
          reject(new Error(response.error));
        }
      } catch {
        // JSON incomplete → wait for more data
      }
    });

    client.on("error", (err) => {
      client.destroy();
      reject(err);
    });
  });
}

// --------------------
// POST /tts
// --------------------
app.post("/tts", (req, res) => {
  const { text, voice } = req.body;

  if (!text) {
    return res.status(400).json({ error: "Missing text" });
  }

  const id = randomUUID();
  const filename = `${id}.wav`;

  const payload = {
    text,
    voice,
    filename,
    output: filename,
  };

  jobs.set(id, {
    id,
    status: "queued",
    file: path.join(OUTPUT_DIR, filename),
  });

  queue.push({ id, payload });
  processQueue();

  res.json({ id });
});

// --------------------
// GET /tts/:id
// --------------------
app.get("/tts/:id", (req, res) => {
  const job = jobs.get(req.params.id);

  if (!job) {
    return res.status(404).json({ error: "Job not found" });
  }

  res.json({ id: job.id, status: job.status });
});

// --------------------
// GET /tts/:id/audio
// --------------------
app.get("/tts/:id/audio", (req, res) => {
  const job = jobs.get(req.params.id);

  if (!job) {
    return res.status(404).json({ error: "Job not found" });
  }

  if (job.status !== "done") {
    return res.status(400).json({ error: "Audio not ready" });
  }

  res.sendFile(path.resolve(job.file));
});

process.on("uncaughtExeption", (err) => console.log(err));

app.listen(PORT, () => {
  console.log(`🚀 TTS API running on http://localhost:${PORT}`);
  setInterval(collectGarbage, 5000);
});
