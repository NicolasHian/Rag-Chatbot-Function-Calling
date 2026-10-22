# NuvemFlix Assistant — Chatbot RAG + Function Calling

Projeto pessoal de estudo em Engenharia de IA Aplicada: um chatbot que responde perguntas sobre um manual em PDF (RAG) e, quando a pergunta exige um dado dinâmico (dias de férias de um funcionário), chama uma API própria em Node.js via *function calling*. Todo o pipeline de IA roda localmente, sem custo e sem API keys.

## O que o projeto faz

- Responde perguntas sobre o conteúdo de um PDF (`manual_exemplo_nuvenflix.pdf`) usando RAG (Retrieval-Augmented Generation).
- Decide automaticamente, a cada pergunta, se precisa consultar um dado dinâmico (dias de férias restantes de um funcionário) em vez de buscar no PDF — e chama uma API própria para isso.
- Se o modelo decidir chamar a API de forma equivocada (ver [Limitações](#limitações-conhecidas)), o sistema detecta o erro e cai de volta para o RAG, respondendo mesmo assim.
- Interface web simples (preto e branco, com histórico de conversas) para interagir com o chatbot pelo navegador.

## Arquitetura

```
Usuário (navegador)
      │
      │  digita pergunta
      ▼
 Frontend (HTML/CSS/JS)
      │  fetch POST /perguntar
      ▼
 Backend Flask (main.py)
      │
      ├─► llm.bind_tools([ferias]).invoke(messages)   ← decide: RAG ou função?
      │
      ├── SE decidiu chamar a tool "ferias":
      │       │
      │       ├─► API Node.js (Express + SQLite) ── GET /ferias/:nome
      │       │
      │       ├── SE deu 200 (achou o funcionário) → devolve o dado real
      │       └── SE deu 404 (erro/nome inválido)   → cai no RAG (fallback)
      │
      └── SE NÃO decidiu chamar nenhuma tool:
              │
              └─► RAG: busca no FAISS (vectorstore) → monta contexto
                       → prompt + contexto → llm.invoke(prompt) → resposta
```

## Stack

| Camada              | Tecnologia                                            |
|----------------------|-------------------------------------------------------|
| LLM                  | Ollama (`llama3.2`), 100% local                        |
| Orquestração de IA   | LangChain                                             |
| Embeddings           | `sentence-transformers/all-mpnet-base-v2` (HuggingFace) |
| Banco vetorial       | FAISS                                                 |
| Backend              | Python + Flask + flask-cors                           |
| API de dados dinâmicos | Node.js + Express + SQLite                          |
| Frontend             | HTML + CSS + JavaScript puro (sem framework)          |

## Estrutura do projeto

```
CHATBOT/
├── main.py                 # Backend Flask — orquestra RAG + tool calling + fallback
├── rag.py                  # Carregamento do PDF, embeddings, FAISS, responder_com_rag()
├── tools.py                # Tool "ferias" (@tool) que chama a API Node
├── manual_exemplo_nuvenflix.pdf
├── html/
│   ├── index.html          # Interface web
│   ├── style.css
│   └── script.js
└── meu-servidor-express/
    ├── index.js             # API Express — GET /ferias/:nomeFuncionario
    ├── banco.js             # Conexão SQLite
    └── setup.sql            # Schema + dados iniciais (funcionários)
```

## Como rodar

É preciso ter três processos rodando ao mesmo tempo, em terminais separados:

**1. Ollama** (precisa estar aberto com o modelo `llama3.2` disponível)

**2. API de férias (Node.js)**
```bash
cd meu-servidor-express
node index.js        # porta 3000
```

**3. Backend (Flask)**
```bash
# dentro do venv Python, com as dependências instaladas:
# pip install flask flask-cors langchain langchain-ollama langchain-huggingface langchain-community pypdf faiss-cpu requests
python main.py        # porta 5000
```

**4. Frontend**

Abrir `html/index.html` com uma extensão tipo Live Server (ou qualquer servidor estático).

## Decisões de design

- **FAISS em vez de Chroma**: escolhido de propósito para entender o mecanismo de busca vetorial sem depender de uma API de conveniência.
- **Embeddings e LLM locais**: todo o pipeline roda via Ollama + HuggingFace local, sem custo e sem depender de API keys de terceiros.
- **API de dados em Node.js (não em Python)**: decisão deliberada para o portfólio — mostrar integração entre duas linguagens diferentes (Python para IA, Node para a API de dados).
- **Validação + fallback em vez de confiar na decisão do modelo**: ver limitação #2 abaixo — em vez de tentar fazer o modelo decidir perfeitamente, o código valida o resultado da chamada antes de usá-lo (defesa em profundidade).

## Limitações conhecidas

### 1. Relevância do retrieval (RAG)

A busca por similaridade (`similarity_search_with_score`, k=2) às vezes retorna um chunk sem relação real com a pergunta, especialmente quando há sobreposição lexical entre tópicos diferentes do documento.

Exemplo: a pergunta "quais são os planos de assinatura" recuperou como *melhor* match (score 0.839) um chunk sobre férias/plano de saúde — enquanto o chunk correto (tabela de planos de assinatura) ficou com score *pior* (0.9418). A causa provável é a palavra "plano" aparecer nos dois contextos. Um corte fixo de score não resolveria, porque o que é "bom" ou "ruim" varia por pergunta — esse é um limite conhecido de RAG simples baseado em similaridade lexical/semântica.

### 2. Viés do modelo pequeno em tool calling

Com apenas uma *tool* vinculada (`bind_tools([ferias])`), o modelo local `llama3.2` tende a chamá-la mesmo para perguntas sem nenhuma relação com férias — por exemplo, chamando `ferias` com `nomeFuncionario: 'plano de assinatura'` para uma pergunta sobre planos, ou com `nomeFuncionario: 'nenhum'` para "me fale mais sobre a empresa" (o modelo literalmente "sabe" que não há nome válido, mas chama a função assim mesmo).

Três abordagens de prompt engineering foram testadas e **nenhuma eliminou o comportamento**: docstring mais específico, instrução de sistema (`SystemMessage`) com regra explícita, e a mesma instrução com exemplos few-shot. A conclusão foi que isso é uma limitação do modelo local (não um problema de como as instruções foram escritas) — modelos maiores tendem a lidar melhor com isso.

**Solução aplicada**: em vez de confiar na decisão do modelo, o backend valida o resultado real da chamada (usa o 404 que a própria API já retorna quando o nome não existe) e, se a chamada falhou, cai de volta para o RAG e responde mesmo assim — o usuário final nunca vê o erro interno. Essa é uma aplicação do conceito de defesa em profundidade.

## Próximos passos

- [ ] Loop de conversa com histórico (memória entre perguntas)
- [ ] Mais *tools* além de `ferias`, para mostrar que o padrão se generaliza
- [ ] Testes automatizados

## Autor

Nicolas Hian — [GitHub](https://github.com/NicolasHian) · [LinkedIn](https://linkedin.com/in/nicolashian)

Projeto construído como parte de um processo de aprendizado guiado em Engenharia de IA Aplicada (RAG, LangChain, embeddings, function calling), com foco em entender os conceitos por trás de cada peça, não apenas em fazer funcionar.
