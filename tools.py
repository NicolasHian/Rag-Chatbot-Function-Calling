from langchain.tools import tool # aqui importamos o tool que serve para transformar um funçao normal em uma ferramenta que a ia pode usar 
import requests #importamos a bliblioteca requests que serve para o python acessar endereços na internet (Apis)

@tool #marca a funçao a baixo como ferramente 
def ferias(nomeFuncionario: str) -> str:# aqui nos criamos a Funçao ferias ela recebe o nome do funcionario em texto str e devolvem um texto str tbm isso ajuda a IA a saber o preencher 
    """use essa funçao somente quando o user pergunta sobre as ferias especificas de alguem que estara quardado na variavel nomeFuncionario, caso nao aja nome de funcionario ou perguntas sobre ferias nao precisa chamar a funçao  exemplo de nome de funcionarios "Nicolas" ou  "Maria" ou "nicolas" ou"maria" antes de chmar a funcaçoo verifique se o nome e um nome proprio"""
# o texto acima e um msg para IA de como usar a ferramenta 
    url = f"http://localhost:3000/ferias/{nomeFuncionario}"#Monta o endereço da API colocando o nome no final Se o nome for “Maria” fica http://localhost:3000/ferias/Maria O localhost:3000 e outro programa rodando no seu computador que tem os dados de ferias
    resposta = requests.get(url)#acessa o endereço e guarda  o que a api respondeu 
    
    if resposta.status_code == 200: # verifica se deu certo o codigo 200 que dizer sucesso e o 404 nao encontrado 500 erro no servidor
        print("Requisição realizada com sucesso!\n")# mostra no terminal que foi sucesso 
        dados = resposta.text #Pega o conteúdo da resposta como texto por exemplo: Maria tem 15 dias de férias
        return dados# devolvemos o esse texto no ourto codigo e ele vira resultado_ferias 
    else:
        print(f"Erro na requisição. Código de status: {resposta.status_code}")
        return f"Erro na requisição. Código de status: {resposta.status_code}"