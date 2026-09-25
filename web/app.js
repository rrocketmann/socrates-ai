const WEBLLM_URL = "https://esm.run/@mlc-ai/web-llm@0.2.85";
const MODEL_F16 = "SmolLM2-135M-Instruct-q0f16-MLC";
const MODEL_F32 = "SmolLM2-135M-Instruct-q0f32-MLC";

const SYSTEM = `You are SOCRATES-AI, a philosophical guide inspired by the Socratic method.

Your purpose: To help users gain knowledge and understanding through thoughtful questioning, rather than simply providing answers.

Instructions:
1. Read the user's statement or question carefully
2. Identify underlying assumptions, gaps in reasoning, or areas for deeper exploration
3. Respond with 2-4 clarifying questions that:
   - Challenge assumptions
   - Encourage critical thinking
   - Guide the user toward their own insights
   - Explore different perspectives
4. Keep your tone curious, respectful, and encouraging
5. Do NOT provide direct answers unless the user has thoroughly explored the topic through questions
6. Help users think for themselves

Style:
- Ask genuine, thought-provoking questions
- Build upon the user's previous responses
- Guide discovery rather than lecture
- Be concise but meaningful`;

const form = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const messages = document.getElementById("messages");
const status = document.getElementById("status");
const sendBtn = document.getElementById("send-btn");

const turns = [];
let engine = null;
let busy = false;

function setStatus(text) {
  status.textContent = text;
}

function setLocked(locked) {
  messageInput.disabled = locked;
  sendBtn.disabled = locked;
}

function addMessage(role, text) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;

  const roleLabel = document.createElement("div");
  roleLabel.className = "role";
  roleLabel.textContent = role === "assistant" ? "SOCRATES" : "YOU";

  const body = document.createElement("div");
  body.textContent = text;

  wrapper.appendChild(roleLabel);
  wrapper.appendChild(body);
  messages.appendChild(wrapper);
  messages.scrollTop = messages.scrollHeight;
  return body;
}

async function pickModel() {
  if (!navigator.gpu) {
    throw new Error("This browser cannot run the on-device model (no WebGPU).");
  }
  const adapter = await navigator.gpu.requestAdapter();
  if (!adapter) {
    throw new Error("This browser cannot run the on-device model (no GPU adapter).");
  }
  return adapter.features.has("shader-f16") ? MODEL_F16 : MODEL_F32;
}

async function boot() {
  try {
    const model = await pickModel();
    const webllm = await import(WEBLLM_URL);
    engine = await webllm.CreateMLCEngine(model, {
      initProgressCallback(report) {
        const pct = Math.round((report?.progress || 0) * 100);
        setStatus(`Loading… ${pct}%`);
      },
    });
    setStatus("Ready");
    setLocked(false);
    messageInput.focus();
  } catch (err) {
    setStatus(err.message || "The on-device model failed to load.");
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message || !engine || busy) return;

  addMessage("user", message);
  messageInput.value = "";
  busy = true;
  setLocked(true);
  setStatus("Thinking…");

  turns.push({ role: "user", content: message });
  while (turns.length > 8) turns.splice(0, 2);

  const body = addMessage("assistant", "");
  let reply = "";

  try {
    const stream = await engine.chat.completions.create({
      messages: [{ role: "system", content: SYSTEM }, ...turns],
      stream: true,
      temperature: 0.7,
      max_tokens: 256,
    });
    for await (const chunk of stream) {
      const delta = chunk.choices?.[0]?.delta?.content || "";
      if (!delta) continue;
      reply += delta;
      body.textContent = reply;
      messages.scrollTop = messages.scrollHeight;
    }
    turns.push({ role: "assistant", content: reply });
    setStatus("Ready");
  } catch (err) {
    turns.pop();
    body.textContent = reply || "The reply stopped early.";
    setStatus(err.message || "The reply failed.");
  } finally {
    busy = false;
    setLocked(false);
    messageInput.focus();
  }
});

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

boot();
