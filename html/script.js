
const themeToggle = document.getElementById("theme-toggle");

themeToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark");
});// aqui nos alteramos o tema do saite 

// ---------- Elementos do chat ----------
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const chatMessages = document.getElementById("chat-messages");
const historyList = document.getElementById("history-list");
const newChatBtn = document.getElementById("new-chat-btn");

// Cria e insere uma bolha de mensagem na tela
function addMessage(role, text) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`; // "user" ou "assistant"

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  wrapper.appendChild(bubble);
  chatMessages.appendChild(wrapper);

  // mantém o scroll sempre na última mensagem
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Adiciona um item na lista de histórico (sidebar)
function addHistoryItem(text) {
  const li = document.createElement("li");
  li.className = "history-item";
  li.textContent = text.length > 40 ? text.slice(0, 40) + "…" : text;
  historyList.insertBefore(li, historyList.firstChild);
}

// ---------- Envio de mensagem ----------
chatForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const texto = userInput.value.trim();
  if (!texto) return;

  addMessage("user", texto);
  addHistoryItem(texto);
  userInput.value = "";

  // Chamada para o backend Flask/FastAPI
  fetch("http://localhost:5000/perguntar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pergunta: texto })
  })
    .then((res) => res.json())
    .then((dados) => {
      addMessage("assistant", dados.resposta);
    })
    .catch((erro) => {
      console.error("Erro na requisição:", erro);
      addMessage("assistant", "Erro ao falar com o servidor.");
    });
});

// ---------- Nova conversa ----------
newChatBtn.addEventListener("click", () => {
  chatMessages.innerHTML = "";
});