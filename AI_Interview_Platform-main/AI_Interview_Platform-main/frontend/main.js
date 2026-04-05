const API_BASE = "http://127.0.0.1:8001";

function getToken() {
  return localStorage.getItem("token");
}

function authHeaders() {
  const token = getToken();
  if (!token) {
    window.location.href = "index.html";
    return {};
  }
  return {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + token
  };
}

// Speech Recognition (Chrome only)
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let isRecording = false;
let recognition = null;
let currentSpeechData = null;

function startSpeechRecognition(interview_id, question_index, question_text) {
  if (!SpeechRecognition) {
    alert("❌ Use Chrome for speech recording");
    return;
  }

  if (isRecording) {
    stopRecording();
    return;
  }

  // 🔥 STORE DATA GLOBALLY
  currentSpeechData = { interview_id, question_index, question_text };

  isRecording = true;
  const recordBtn = document.getElementById("record-btn");
  recordBtn.textContent = "🛑 STOP RECORDING";
  recordBtn.className = "btn btn-danger";
  document.getElementById("live-transcript").textContent = "🔴 Listening... Speak now!";
  
  recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'en-US';
  
  recognition.onresult = (e) => {
    let transcript = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      transcript += e.results[i][0].transcript;
    }
    document.getElementById("live-transcript").textContent = transcript || "Speak louder...";
  };
  
  recognition.onerror = (e) => {
    console.error("Speech error:", e.error);
    document.getElementById("live-transcript").textContent = "Error: " + e.error;
  };
  
  // 🔥 CRITICAL FIX: DISABLE AUTO-STOP
  recognition.onend = () => {
    // DO NOTHING - Manual stop only!
    console.log("Speech ended naturally - waiting for manual stop");
  };
  
  recognition.start();
  
  // 90-second timeout warning
  setTimeout(() => {
    if (isRecording) {
      alert("⏰ 90 seconds reached! Click STOP to evaluate.");
    }
  }, 90000);
}

function stopRecording() {
  console.log("🛑 MANUAL STOP CLICKED!");
  
  isRecording = false;
  if (recognition) {
    recognition.stop();
    recognition = null;
  }
  
  const recordBtn = document.getElementById("record-btn");
  recordBtn.textContent = "🎤 Record Answer";
  recordBtn.className = "btn btn-success";
  
  // 🔥 BULLETPROOF CLEANING
  const transcriptElement = document.getElementById("live-transcript");
  let rawTranscript = transcriptElement.textContent || "";
  
  let cleanTranscript = rawTranscript
    .replace(/listening|speaking|recording|louder|error|🔴|📝|❌|🎤|Speak/gi, '')
    .replace(/[^\w\s.,!?]/g, ' ')
    .replace(/\s{2,}/g, ' ')
    .trim();
  
  // Count words (2+ chars minimum)
  const words = cleanTranscript.split(/\s+/).filter(word => word.length >= 2);
  const wordCount = words.length;
  
  // 🔥 DEBUG EVERYTHING
  console.log("🔍 RAW TRANSCRIPT:", `"${rawTranscript}"`);
  console.log("🔍 CLEAN TRANSCRIPT:", `"${cleanTranscript}"`);
  console.log("🔍 ALL WORDS:", words);
  console.log("🔍 WORD COUNT:", wordCount);
  
  if (wordCount < 5) {
    const example = "I am preparing for my data science interview today";
    alert(`❌ Need 5+ words!\n\nGot ${wordCount} words: "${cleanTranscript}"\n\n✅ Try saying: "${example}" (8 words)`);
    transcriptElement.textContent = cleanTranscript || "Speak 5+ words...";
    return;
  }
  
  if (!currentSpeechData) {
    alert("❌ No interview context. Restart the question.");
    return;
  }
  
  transcriptElement.textContent = `✅ ${wordCount} words detected - Sending to AI...`;
  
  // Small delay for user feedback
  setTimeout(() => {
    evaluateAnswer({
      ...currentSpeechData,
      user_answer: cleanTranscript
    });
  }, 800);
}

async function evaluateAnswer(data) {
  try {
    const res = await fetch(API_BASE + "/evaluate_answer", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(data)
    });
    
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    
    const result = await res.json();
    
    addMessage(
      `🎯 Score: ${result.feedback.score}/10\n` +
      `✅ Strengths: ${result.feedback.strengths}\n` +
      `⚠️ Improve: ${result.feedback.weaknesses}\n` +
      `💡 Tip: ${result.feedback.advice}`,
      "ai"
    );
    
    if (data.question_index < 4) {
      currentQuestionIndex++;
      updateProgress();
      playCurrentQuestion();
    } else {
      setTimeout(() => window.location.href = "result.html", 2000);
    }
  } catch (error) {
    console.error("AI Evaluation failed:", error);
    addMessage("❌ Backend error. Is server running on port 8001?", "error");
  }
}
