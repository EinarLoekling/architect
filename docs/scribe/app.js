
const API_URL = "http://localhost:5001";

const recordBtn = document.getElementById('record-btn');
const statusText = document.getElementById('status-text');
const transcriptArea = document.getElementById('transcript-area');
const generateBtn = document.getElementById('generate-btn');
const styleSelect = document.getElementById('style-select');
const contextInput = document.getElementById('context-input');
const resultSection = document.getElementById('result-section');
const emailOutput = document.getElementById('email-output');
const copyBtn = document.getElementById('copy-btn');
const retryBtn = document.getElementById('retry-btn');

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

// Audio Recording Logic
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    recordBtn.addEventListener('click', toggleRecording);
} else {
    statusText.textContent = "Audio API not supported";
    recordBtn.disabled = true;
}

async function toggleRecording() {
    if (!isRecording) {
        // Start Recording
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = sendAudioData;

            audioChunks = [];
            mediaRecorder.start();
            isRecording = true;
            recordBtn.classList.add('recording');
            statusText.textContent = "Recording... Tap to Stop";
        } catch (err) {
            console.error("Error accessing mic:", err);
            statusText.textContent = "Microphone Access Denied";
        }
    } else {
        // Stop Recording
        mediaRecorder.stop();
        isRecording = false;
        recordBtn.classList.remove('recording');
        statusText.textContent = "Processing...";
    }
}

async function sendAudioData() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.webm");

    try {
        statusText.textContent = "Transcribing...";
        const response = await fetch(`${API_URL}/transcribe`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.transcription) {
            transcriptArea.value = data.transcription;
            statusText.textContent = "Transcription Done";
        } else {
            statusText.textContent = "Transcription Failed";
            console.error(data.error);
        }
    } catch (err) {
        console.error("API Error:", err);
        statusText.textContent = "Error connecting to server";
    }
}

// Generation Logic
generateBtn.addEventListener('click', async () => {
    const text = transcriptArea.value;
    if (!text) {
        alert("Please record or type something first!");
        return;
    }

    const style = styleSelect.value;
    const context = contextInput.value;

    generateBtn.disabled = true;
    generateBtn.textContent = "Scribing...";

    try {
        const response = await fetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, style, context })
        });

        const data = await response.json();

        if (data.email) {
            emailOutput.innerText = data.email; // Use innerText to preserve formatting but avoid XSS
            resultSection.classList.remove('hidden');
            resultSection.scrollIntoView({ behavior: 'smooth' });
        } else {
            alert("Error generating email: " + (data.error || "Unknown error"));
        }

    } catch (err) {
        console.error(err);
        alert("Failed to connect to backend.");
    } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = "Scribe Email";
    }
});

// UI Actions
copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(emailOutput.innerText);
    copyBtn.innerText = "Copied!";
    setTimeout(() => copyBtn.innerText = "Copy to Clipboard", 2000);
});

retryBtn.addEventListener('click', () => {
    resultSection.classList.add('hidden');
    transcriptArea.focus();
});
