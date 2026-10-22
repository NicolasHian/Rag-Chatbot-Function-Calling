import pypdf # importa a bibliotedca que sabe ler pdf 
from langchain_core.documents import Document # importa a ferramente que vai guarda os pedaços do texto 
from langchain_text_splitters import RecursiveCharacterTextSplitter # isso traz a ferramenta de cortar
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS 
from langchain_ollama import ChatOllama
from langchain.tools import tool
import requests
from langchain_core.messages import HumanMessage, SystemMessage

#bloco 1 

def load_pdf_pages(file_path: str) -> list[Document]:  #def cria uma funçao que pode ser usada varias vezes  nesse caso a funçao chama load_pdf_pages
    reader = pypdf.PdfReader(file_path) # aqui ele abre o pdf  e guarda em uma variavel que no caso se chama reader , a partir da qui o reader.pages e a lista de pagina desse pdf 
    return [
        Document(
            page_content=page.extract_text() or "", # a cada pagina esse codigo irar extrair (extract_text()) e guarda junto com a informaçao de qual pagina e qual arquivo e (o metadata)
            metadata={"source": file_path, "page": i},
        )
        for i, page in enumerate(reader.pages) # percorre essa lista de paginas uma por uma o enumerate e so um truque pra vc pegar ao mesmo tempo o numero de paginas
    ]


file_path = "manual_exemplo_nuvenflix.pdf"
docs = load_pdf_pages(file_path)

text_splitter = RecursiveCharacterTextSplitter( # aqui estamos configurando a ferramente da um nome ( text_splitter e depois chama a ferramenta )
    chunk_size=600, chunk_overlap=50, add_start_index=True # aqui colocamos em  chunk_size o tamanho de cada pedacinho do texto no caso 100 = a 100 caracteres o chunk_overlap serve para repetir os ultomos 20 caracteris do bloco anterior o  add_start_index=True liga aquela opção que guarda de onde cada pedaço começou no texto original.
)
all_splits = text_splitter.split_documents(docs)# aqui a onde e executado tudo que vc configurou acima ela vai pegar as 4 paginas do pdf e devolver um lista nova all_splits  só que agora com vários pedaços pequenos em vez de 4 páginas inteiras.

embeddings = HuggingFaceEmbeddings( # aqui nos chamos a ferramentea que ja importamos la em cima ela e a que realmente vai fazer transformat o texto em vetor 
    model_name="sentence-transformers/all-mpnet-base-v2", # aqui nos especificamos qual modelo quermos usar da huggingface
    encode_kwargs={"normalize_embeddings": True},
)
vetor = embeddings.embed_query("frase de teste qualquer")

vectorstore = FAISS.from_documents(all_splits, embeddings)

frase = input("Digite sua pergunta:").strip() # .strip() remove espaços extras no começo e no fim
resultados = vectorstore.similarity_search_with_score(frase, k=2) #  aqui é a busca de verdade. Ele pega o texto da sua pergunta, transforma em vetor (usando o mesmo modelo), e compara com os 62 vetores guardados, achando os mais parecidos. O k=2 diz "me devolve só os 2 chunks mais parecidos". O resultado é uma lista com esses 2 chunks

llm = ChatOllama(
    model="llama3.2",
    temperature=0,# parametro para ela "arrisca" na resposta  no modo 0 ela segue a resposta "mais provavel" quando mais vc sobe mais ela arrisca
    base_url="http://127.0.0.1:11434",
)

messages = [
    SystemMessage(content="Você é um assistente inteligente com acesso a uma função tool chamada ferias Regras de Decisão para a Tool ferias: 1. **QUANDO CHAMAR:** Você DEVE chamar a função ferias SOMENTE se a mensagem do usuário mencionar explicitamente ou perguntar sobre férias de um funcionário específico ex: Quantos dias o Nome tem de férias QUANDO NÃO CHAMAR: Você NÃO DEVE chamar a função ferias sob nenhuma outra circunstância. Perguntas sobre planos, conversas gerais ou outros assuntos devem ser respondidas normalmente usando o contexto disponível, sem acionar a tool.Exemplos de Comportamento: Exemplo 1:Mensagem do usuário: Quantos dias o Nicolas tem de férias?Decisão correta Chamar a função ferias e retornar a resposta com base no resultado. Decisão errada:* Não chamar a função e inventar ou ignorar a pergunta.Exemplo 2:Mensagem do usuário:* Quais são os planos para o projeto? Decisão correta:* Analisar os chunks de contexto disponíveis, verificar a proximidade/relevância e responder diretamente à pergunta. **NÃO** chame a função ferias. Decisão errada:* Chamar a função ferias para uma pergunta que não tem relação com férias de funcionários."),
    HumanMessage(frase)
]

pergunta = frase # aqui pegamos a frase que o user colcou la em cima e coloca ela dentro da variavel pergunta 
contexto = "\n\n".join([r.page_content for r, j in resultados]) # prepara o contexto a partir dos chunks encontrados

# --- FUNÇÃO DO RAG (Princípio DRY) ---
def responder_com_rag(pergunta: str, contexto: str):
    prompt = f"""
Responda a pergunta usando apenas as informações do contexto abaixo. Use somente as partes do contexto que realmente respondam à pergunta e ignore o resto. Se a resposta não estiver no contexto, diga que não sabe.
Contexto:
{contexto}

Pergunta: {pergunta}
"""
    resposta_rag = llm.invoke(prompt)
    print(resposta_rag.content)
    return resposta_rag.content


@tool
def ferias(nomeFuncionario: str) -> str:
    """use essa funçao somente quando o user pergunta sobre as ferias especificas de alguem que estara quardado na variavel nomeFuncionario, caso nao aja nome de funcionario ou perguntas sobre ferias nao precisa chamar a funçao  exemplo de nome de funcionarios "Nicolas" ou  "Maria" ou "nicolas" ou"maria" antes de chmar a funcaçoo verifique se o nome e um nome proprio"""

    url = f"http://localhost:3000/ferias/{nomeFuncionario}"
    resposta = requests.get(url)
    #  (código HTTP 200)
    if resposta.status_code == 200:
        print("Requisição realizada com sucesso!\n")
        dados = resposta.text
        return dados   
    else:
        print(f"Erro na requisição. Código de status: {resposta.status_code}")
        return f"Erro na requisição. Código de status: {resposta.status_code}"


llm_com_ferramentas = llm.bind_tools([ferias])
resposta = llm_com_ferramentas.invoke(messages)
print(resposta.tool_calls)

# CHECK 1: O modelo decidiu chamar a ferramenta?
if resposta.tool_calls:
    print("A funçao foi chamada")
    primeira_chamada = resposta.tool_calls[0]
    nome = primeira_chamada['args']['nomeFuncionario']
    resultado_ferias = ferias.invoke({"nomeFuncionario": nome})
    
    # CHECK 2 (Aninhado): A chamada da API deu erro?
    if "Erro" in resultado_ferias:
        print("A API retornou erro. Usando o RAG como fallback...")
        responder_com_rag(pergunta, contexto) # Chama a função no lugar 1
    else:
        print(resultado_ferias)

# CAMINHO DIRETO DO RAG: O modelo não chamou a ferramenta
else:
    print("A funçao nao foi chamada")
    responder_com_rag(pergunta, contexto) # Chama a função no lugar 2