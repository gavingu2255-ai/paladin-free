import { updateLights } from "./lights.js";

/* ============================================================
   API KEY HANDLING
   ============================================================ */
let apiKey = localStorage.getItem("openai_api_key") || "";

// Load saved key into modal when opened
export function loadApiKeyIntoModal() {
    const input = document.getElementById("api-key-input");
    if (input) input.value = apiKey;
}

// Save API key from modal
export function saveApiKey() {
    const input = document.getElementById("api-key-input");
    if (!input) return;

    apiKey = input.value.trim();
    localStorage.setItem("openai_api_key", apiKey);

    const modal = document.getElementById("settings-modal");
    if (modal) modal.classList.add("hidden");
    
    alert("API Key saved.");
}

/* ============================================================
   CHAT WINDOW RENDERING
   ============================================================ */
function addMessage(role, text) {
    const win = document.getElementById("chat-window");
    const div = document.createElement("div");
    div.className = `message ${role}`;

    // Correct label mapping
    const displayName = role === "assistant" ? "Paladin" : "You";

    // Use displayName instead of role
    div.textContent = `${displayName}: ${text}`;

    win.appendChild(div);
    win.scrollTop = win.scrollHeight;
}

/* ============================================================
   SEND MESSAGE TO BACKEND
   ============================================================ */
export async function sendMessage() {
    const inputEl = document.getElementById("input");
    const text = inputEl.value.trim();
    if (!text) return; 
    
    addMessage("user", text);
    inputEl.value = ""; 

    try {
        const res = await fetch("http://127.0.0.1:8001/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                conversation_id: "default",
                message: text,
                api_key: apiKey
            })
        });

        console.log("status:", res.status);

        let data;
        try {
            data = await res.json();
        } catch (err) {
            console.error("JSON parse error:", err);
            addMessage("assistant", "Backend returned invalid JSON.");
            return;
        }

        console.log("data:", data);

        const reply = data?.data?.reply ?? data?.reply ?? "(no reply)";
        const lights = data?.data?.lights ?? data?.lights ?? [];

        addMessage("assistant", reply);
        updateLights(lights);

        const tokenUsage = data?.data?.token_usage ?? data?.token_usage;
        if (tokenUsage) {
            const stats = tokenUsage;
            const panel = document.getElementById("token-stats");
            if (panel) {
                panel.innerHTML = `
                    <div>Total Input: ${stats.total_input}</div>
                    <div>Total Output: ${stats.total_output}</div>
                `;
            }
        }

        loadWorld();
        loadWorkflow();
        loadPersona();

    } catch (err) {
        console.error("fetch error:", err);
        addMessage("assistant", "Error talking to backend.");
    }
}

/* ============================================================
   FILE UPLOAD
   ============================================================ */
export async function uploadFile() {
    const fileInput = document.getElementById("file-input");
    if (!fileInput.files.length) {
        alert("No file selected.");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch(`http://127.0.0.1:8001/upload?conversation_id=default`, {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        addMessage("assistant", `File [${data.filename}] uploaded. Text extracted.`);
        console.log("Extracted content:", data.content);
        
        fileInput.value = "";
    } catch (err) {
        console.error("Upload error:", err);
        alert("Failed to upload file.");
        addMessage("assistant", "File upload failed.");
    }
}

/* ============================================================
   WORLD PANEL
   ============================================================ */
export async function loadWorld() {
    try {
        const res = await fetch(`http://127.0.0.1:8001/world?conversation_id=default`);
        const data = await res.json();
        document.getElementById("world-text").value = JSON.stringify(data.world, null, 2);
    } catch (err) { console.error("World load error:", err); }
}

export async function saveWorld() {
    const text = document.getElementById("world-text").value;
    let world = {};
    try { world = JSON.parse(text); } catch { alert("Invalid JSON"); return; }

    try {
        const res = await fetch(`http://127.0.0.1:8001/world?conversation_id=default`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(world)
        });
        if (res.ok) alert("World saved.");
    } catch (err) { console.error("World save error:", err); }
}

/* ============================================================
   PERSONA PANEL
   ============================================================ */
export async function loadPersona() {
    try {
        const res = await fetch(`http://127.0.0.1:8001/persona?conversation_id=default`);
        const data = await res.json();
        document.getElementById("persona-text").value = JSON.stringify(data.persona, null, 2);
    } catch (err) { console.error("Persona load error:", err); }
}

export async function savePersona() {
    const text = document.getElementById("persona-text").value;
    let persona = {};
    try { persona = JSON.parse(text); } catch { alert("Invalid JSON"); return; }

    try {
        const res = await fetch(`http://127.0.0.1:8001/persona?conversation_id=default`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(persona)
        });
        if (res.ok) alert("Persona saved.");
    } catch (err) { console.error("Persona save error:", err); }
}

/* ============================================================
   WORKFLOW PANEL
   ============================================================ */
export async function loadWorkflow() {
    try {
        const res = await fetch(`http://127.0.0.1:8001/workflow?conversation_id=default`);
        const data = await res.json();
        document.getElementById("workflow-text").value = JSON.stringify(data.workflow, null, 2);
    } catch (err) { console.error("Workflow load error:", err); }
}

export async function saveWorkflow() {
    const text = document.getElementById("workflow-text").value;
    let workflow = {};
    try { workflow = JSON.parse(text); } catch { alert("Invalid JSON"); return; }

    try {
        const res = await fetch(`http://127.0.0.1:8001/workflow?conversation_id=default`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(workflow)
        });
        if (res.ok) alert("Workflow saved.");
    } catch (err) { console.error("Workflow save error:", err); }
}
/* ============================================================
   EXPOSE FUNCTIONS TO WINDOW
   ============================================================ */
window.sendMessage = sendMessage;
window.uploadFile = uploadFile;
window.loadWorld = loadWorld;
window.saveWorld = saveWorld;
window.loadPersona = loadPersona;
window.savePersona = savePersona;
window.loadWorkflow = loadWorkflow;
window.saveWorkflow = saveWorkflow;

window.loadApiKeyIntoModal = loadApiKeyIntoModal;
window.saveApiKey = saveApiKey;

/* ============================================================
   INITIALIZATION
   ============================================================ */
window.addEventListener('DOMContentLoaded', () => {
    loadWorld();
    loadPersona();
    loadWorkflow();

    // ⭐ Enable Enter-to-Send
    const input = document.getElementById("input");
    if (input) {
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // ⭐ Enable Send button click
    const sendBtn = document.getElementById("send-btn");
    if (sendBtn) {
        sendBtn.addEventListener("click", sendMessage);
    }
});
