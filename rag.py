import pypdf # importa a bibliotedca que sabe ler pdf 
from langchain_core.documents import Document # importa a ferramente que vai guarda os pedaços do texto 
from langchain_text_splitters import RecursiveCharacterTextSplitter # isso traz a ferramenta de cortar
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS 

def load_pdf_pages(file_path: str) -> list[Document]:  #def cria uma funçao que pode ser usada varias vezes  nesse caso a funçao chama load_pdf_pages
    reader = pypdf.PdfReader(file_path) # aqui ele abre o pdf  e guarda em uma variavel que no caso se chama reader , a partir da qui o reader.pages e a lista de pagina desse pdf 
    return [
        Document(
            page_content=page.extract_text() or "", # a cada pagina esse codigo irar extrair (extract_text()) e guarda junto com a informaçao de qual pagina e qual arquivo e (o metadata)
            metadata={"source": file_path, "page": i},
        )
        for i, page in enumerate(reader.pages) # percorre essa lista de paginas uma por uma o enumerate e so um truque pra vc pegar ao mesmo tempo o numero de paginas
    ]

file_path = "manual_exemplo_nuvenflix.pdf" # guarda o nome do pdf em um variavel
docs = load_pdf_pages(file_path)# ler o pdf 

text_splitter = RecursiveCharacterTextSplitter( # aqui estamos configurando a ferramente da um nome ( text_splitter e depois chama a ferramenta )
    chunk_size=600, chunk_overlap=50, add_start_index=True # aqui colocamos em  chunk_size o tamanho de cada pedacinho do texto no caso 100 = a 100 caracteres o chunk_overlap serve para repetir os ultomos 20 caracteris do bloco anterior o  add_start_index=True liga aquela opção que guarda de onde cada pedaço começou no texto original.
)
all_splits = text_splitter.split_documents(docs)# aqui a onde e executado tudo que vc configurou acima ela vai pegar as 4 paginas do pdf e devolver um lista nova all_splits  só que agora com vários pedaços pequenos em vez de 4 páginas inteiras.

embeddings = HuggingFaceEmbeddings( # aqui nos chamos a ferramentea que ja importamos la em cima ela e a que realmente vai fazer transformat o texto em vetor 
    model_name="sentence-transformers/all-mpnet-base-v2", # aqui nos especificamos qual modelo quermos usar da huggingface
    encode_kwargs={"normalize_embeddings": True},# aqui nos deiaxmos o vetores do mesmo "tamanho" para deixar a comparaçao mais precisa 
)

vectorstore = FAISS.from_documents(all_splits, embeddings)# pegas os pedacinhos do texto transforma cada um em vetores e Guarda tudo no Faiss
#e o vectorstore que o outro codigo usa para procurar os trechos parecidos com a pergunta 
#FAISS e um biblioteca criada pela META que serve para guarda vetores e encontra de forma rapida os mais parecidos 

def responder_com_rag(pergunta: str, contexto: str, llm):#aqui criamos a funçao que responde usando os docs ela recebe a pergunta e o contexto que seria os rechos encontrados 
    prompt = f"""
Responda a pergunta usando apenas as informações do contexto abaixo. Use somente as partes do contexto que realmente respondam à pergunta e ignore o resto. Se a resposta não estiver no contexto, diga que não sabe.
Contexto:
{contexto}

Pergunta: {pergunta}
"""
    #aqui em cima nos montamos o texto que vai para a ia  e o f antes das """" permite colocar variaveis dentro do texto que sao trocadas pelos valores reais 
    resposta_rag = llm.invoke(prompt)# mando o texto para ia e recebe a resposta 
    print(resposta_rag.content)# mostra a resposta no terminal para conferencia 
    return resposta_rag.content#Devolve o texto da resposta para quem chamou a função