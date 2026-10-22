# NuvemFlix Assistant — Chatbot RAG + Function Calling

Este é um projeto pessoal de estudo em Engenharia de IA Aplicada. O objetivo principal foi construir um assistente inteligente capaz de responder a dúvidas com base num manual em PDF (via RAG) e, sempre que o utilizador pede uma informação dinâmica (como os dias de férias de um colaborador), acionar automaticamente uma API própria em Node.js através de *function calling*.

Todo o ecossistema de inteligência artificial corre 100% de forma local na máquina, sem necessidade de chaves de API pagas e com custo zero.

---

## O que a aplicação faz

- **Consulta documental inteligente (RAG):** extrai contexto e responde a questões a partir do ficheiro `manual_exemplo_nuvenflix.pdf`.
- **Tomada de decisão em tempo real:** avalia cada mensagem e determina autonomamente se deve consultar o documento estático ou acionar a API externa para consultar dias de férias de um colaborador.
- **Mecanismo de tolerância a falhas (*fallback*):** caso o modelo tente acionar a API de forma equivocada (ver [Limitações e Aprendizagens](#limitações-e-aprendizagens)), o sistema interceta a falha e redireciona a resposta de imediato para o RAG, sem deixar o utilizador sem resposta.
- **Interface web limpa:** painel minimalista a preto e branco com suporte ao histórico da conversa diretamente no navegador.

---

## Como as peças comunicam (Arquitetura)

```
Utilizador (Navegador)
      │
      │  escreve pergunta
      ▼
 Frontend (HTML/CSS/JS)
      │  POST /perguntar
      ▼
 Backend Flask (main.py)
      │
      ├─► llm.bind_tools([ferias]).invoke(messages)   ← O modelo avalia: RAG ou chamada de função?
      │
      ├── SE decidiu acionar a função "ferias":
      │       │
      │       ├─► API Node.js (Express + SQLite) ── GET /ferias/:nome
      │       │
      │       ├── Resposta 200 (encontrou o registo) ─► Devolve o dado real
      │       └── Resposta 404 (erro ou nome inválido) ─► Fallback automático para o RAG
      │
      └── SE decidiu não acionar funções:
              │
              └─► RAG: consulta de similaridade no FAISS (vetor)
                       → constrói o contexto → llm.invoke(prompt) → resposta final
```

---

## Tecnologias utilizadas

| Camada | Tecnologia | Contexto de uso |
| :--- | :--- | :--- |
| **Modelo de Linguagem (LLM)** | Ollama (`llama3.2`) | Execução 100% local e privada |
| **Orquestração de IA** | LangChain | Integração de prompts, vetores e chamadas de ferramentas |
| **Embeddings** | `sentence-transformers/all-mpnet-base-v2` | Modelo do HuggingFace descarregado localmente |
| **Base de Dados Vetorial** | FAISS | Indexação e pesquisa de similaridade de texto |
| **Serviço Principal** | Python + Flask + flask-cors | Gestão do fluxo de decisão e RAG |
| **API de Dados Dinâmicos** | Node.js + Express + SQLite | Simulação do sistema de gestão de RH |
| **Frontend** | HTML5, CSS3 e JavaScript Vanilla | Interface simples sem dependências de frameworks |

---

## Organização do repositório

```
CHATBOT/
├── main.py                 # Backend Flask: orquestrador do RAG, chamadas de tools e fallback
├── rag.py                  # Processamento de PDF, embeddings, FAISS e geração de respostas
├── tools.py                # Registo da tool "ferias" (@tool) que comunica com a API Node
├── manual_exemplo_nuvenflix.pdf
├── html/
│   ├── index.html          # Interface de utilizador
│   ├── style.css           # Estilização
│   └── script.js           # Comunicação assíncrona com o Flask
└── meu-servidor-express/
    ├── index.js            # Rota GET /ferias/:nomeFuncionario
    ├── banco.js            # Conexão e inicialização do SQLite
    └── setup.sql           # Esquema da tabela e dados de teste de colaboradores
```

---

## Como executar localmente

Para colocar o ambiente a funcionar, é necessário abrir **três terminais distintos** em paralelo:

**1. Levantar o modelo local**  
Certifique-se de que o **Ollama** está ativo e com o modelo descarregado:
```bash
ollama run llama3.2
```

**2. Iniciar a API de Férias (Node.js)**
```bash
cd meu-servidor-express
node index.js        # Disponível na porta 3000
```

**3. Iniciar o Backend Flask (Python)**
```bash
# Dentro do ambiente virtual (venv) com as dependências instaladas:
# pip install flask flask-cors langchain langchain-ollama langchain-huggingface langchain-community pypdf faiss-cpu requests
python main.py        # Disponível na porta 5000
```

**4. Aceder ao Frontend**  
Abra o ficheiro `html/index.html` através de uma extensão local (como o Live Server no VS Code) ou de qualquer servidor estático.

---

## Decisões de arquitetura

- **FAISS em detrimento do Chroma:** a escolha pelo FAISS foi propositada para trabalhar diretamente com uma biblioteca de pesquisa vetorial de baixo nível, consolidando o conhecimento sem depender de abstrações prontas de bases de dados vetoriais geridas.
- **Processamento 100% offline:** a combinação de Ollama e HuggingFace local garante independência total de quotas, custos de faturação e chaves de terceiros.
- **Separação de ambientes (Python + Node.js):** em vez de unificar tudo em Python, a API de apoio foi isolada em Node.js/Express para demonstrar capacidade prática de integração entre ecossistemas distintos no portfólio.
- **Defesa em profundidade no código:** em vez de assumir cegamente que o LLM tomará sempre a decisão de roteamento correta, o backend inspeciona a resposta da chamada e assume a responsabilidade de corrigir o curso caso a ferramenta falhe.

---

## Limitações e aprendizagens

### 1. Desafios na relevância do RAG (`similarity_search_with_score`)
Durante a pesquisa por similaridade com `k=2`, foi identificado que fragmentos de texto sem relevância direta podem obter pontuações altas quando existe sobreposição lexical.

> **Caso prático:** ao questionar *"quais são os planos de assinatura"*, o melhor resultado devolvido (score 0.839) correspondia a um trecho sobre férias e planos de saúde. Já o trecho exato com a tabela de assinaturas obteve uma pontuação inferior (score 0.9418). Isto ocorre porque o termo "plano" se repete em áreas de negócio distintas do documento. A definição de um limiar estático de corte não soluciona o problema globalmente, evidenciando as restrições naturais de abordagens RAG puramente vetoriais sem etapas de *reranking* ou filtragem híbrida.

### 2. Viés de acionamento em modelos compactos (*Tool Calling*)
Ao vincular apenas uma ferramenta ao modelo (`bind_tools([ferias])`), o `llama3.2` demonstrou uma forte tendência para invocar a função mesmo em perguntas irrelevantes. O modelo chegou a passar valores como `nomeFuncionario: 'plano de assinatura'` para dúvidas sobre preços, ou `nomeFuncionario: 'nenhum'` para perguntas genéricas sobre a empresa.

Foram testadas três abordagens clássicas de engenharia de prompts:
1. Docstrings com especificações detalhadas de restrição de domínio.
2. Diretrizes explícitas na `SystemMessage`.
3. Demonstrações com exemplos (*few-shot*).

Nenhuma das técnicas eliminou o comportamento de forma estável, demonstrando tratar-se de uma característica de calibração inerente a modelos pequenos de parâmetros reduzidos.

**Solução implementada:** a estabilidade foi garantida na camada de código. O backend aproveita o erro HTTP `404` devolvido pela API do Node.js quando o nome não existe e, ao detetar a falha, descarta a chamada e processa a pergunta imediatamente pelo RAG. Desta forma, o utilizador final recebe uma resposta contextualizada sem interrupções visíveis.

---

## O que se segue no projeto

- [ ] Manutenção de contexto multi-turn (memória contínua entre mensagens)
- [ ] Implementação de ferramentas adicionais para validação de roteamento múltiplo
- [ ] Criação de cobertura de testes automatizados

---

## Autor

**Nicolas Hian** — [GitHub](https://github.com/NicolasHian) · [LinkedIn](https://linkedin.com/in/nicolashian)

*Projeto desenvolvido como exercício prático de Engenharia de IA Aplicada, priorizando a compreensão aprofundada da mecânica interna de RAG, embeddings e function calling face a implementações automáticas.*