from flask import Flask, request, jsonify
from flask_cors import CORS 
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from rag import vectorstore, responder_com_rag
from tools import ferias

app = Flask(__name__)
CORS(app) #  acesso ao back e frontend 

# aqui  damos inicio ao modelo selecionado
llm = ChatOllama(
    model="llama3.2",
    temperature=0,
    base_url="http://127.0.0.1:11434",
)
llm_com_ferramentas = llm.bind_tools([ferias])# aqui nos damos acesso a llm a ferramenta ferias 

SYSTEM_PROMPT = (# aqui pdeomos dizer que e um prompt escondido ou  as regras da ia
    "Você é um assistente inteligente com acesso a uma função tool chamada ferias. "
    "Regras de Decisão para a Tool ferias: "
    "1. QUANDO CHAMAR: Você DEVE chamar a função ferias SOMENTE se a mensagem do usuário mencionar "
    "explicitamente ou perguntar sobre férias de um funcionário específico (ex: Quantos dias o Nome tem de férias). "
    "2. QUANDO NÃO CHAMAR: Você NÃO DEVE chamar a função ferias sob nenhuma outra circunstância. "
    "Perguntas sobre planos, conversas gerais ou outros assuntos devem ser respondidas normalmente "
    "usando o contexto disponível, sem acionar a tool."
)

@app.route("/perguntar", methods=["POST"])
def perguntar():# nessa duas linhas nos criamos o endereço /perguntar que sera a onde o saite irar mandar as perguntas 
    dados = request.get_json() # aqui o sistema le oq o saite mandou ele pede o arquivo json do saite 
    pergunta = dados.get("pergunta", "").strip()#aqui nos vamos pegar a pergunta e tirar os espaços sobrando 

    if not pergunta:
        return jsonify({"resposta": "Por favor, envie uma pergunta válida."}), 400 # aqui se a pergunta estiver vazia ele pede novamente 

    # Prepara os chunks do RAG
    resultados = vectorstore.similarity_search_with_score(pergunta, k=2) # usamos o pdf e ele irar procura os 2 trechos mais parecidos com a pergunta 
    contexto = "\n\n".join([r.page_content for r, j in resultados])# aqui ele pega os 2 trechos mais parecido e junta em um so 

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=pergunta)
    ]# aqui nos mandamos as regras que estao la em cima e tbm a pergunta do user 

    resposta = llm_com_ferramentas.invoke(messages)# aqui sera a onde a IA vai decidir se usa a tool ou noo
    print("Tool calls:", resposta.tool_calls)#mostra oq a IA decidiu 

    # CHECK 1 caso o modelo decida usar a ferramenta ela entrar aqui
    if resposta.tool_calls:
        print("A função foi chamada")
        primeira_chamada = resposta.tool_calls[0]# aqui nos vamos pegar o pedido da ia 
        nome = primeira_chamada['args']['nomeFuncionario']# aqui nos pegamos o nome do funcionario que a IA encontrou na pergunta 
        resultado_ferias = ferias.invoke({"nomeFuncionario": nome})# e aqui consultamos o sistema das ferias com o nome do funcionario

        # CHECK 2 se o sistema retornar erro nos respondemos usando o plano B  que seria usar o fallback
        if "Erro" in resultado_ferias:
            print("A API retornou erro. Usando o RAG como fallback...")
            texto_final = responder_com_rag(pergunta, contexto, llm)
        else:# caso o sistema retorne tudo certo com as informaçoes sera a resposta 
            texto_final = resultado_ferias

    # se a pergunta nao for nd relacionado a ferramenta(ferias) nos respondemos usando os docs
    else:
        print("A função não foi chamada")
        texto_final = responder_com_rag(pergunta, contexto, llm)

    # Manda a resposta de volta para o site.
    return jsonify({"resposta": texto_final})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)# Liga o servidor na porta 5000.