const express = require('express');//importa o pacote express
const app = express(); // inicia o express 
const port = 3000; // qual a porta do computador // const = variavel 

app.get('/', (req, res) => {// app.get("/") seria o inicio do saite  o req seria oq o user estar pedindo dentro do saite e o res seria oq vai entregar oq o user pediu
  res.send('');// e oq o o user vai receber como se fosse a "comida" que ele pediu
});

app.listen(port, () => {//aqui e a onde nos abrimos o servidor e pedimos para ele ficar de olho na port que definimos 
  console.log(`Servidor rodando em http://localhost:${port}`); // uma msg para o "dono" falando oq estar acontecendo 
});


const db = require('./banco.js'); // <-- A PORTA DE ENTRADA do seu arquivo novo
app.get('/ferias/:nomeFuncionario', (req, res) => { // Cria uma rota de leitura (get). O :nomeFuncionario com os dois pontos significa que essa parte da URL é dinâmica. Se o usuário digitar /ferias/nicolas ou /ferias/maria, o Express vai aceitar e guardar a palavra digitada. (req, res) são o pedido do usuário e a sua ferramenta de resposta.
  const nomeBuscado = req.params.nomeFuncionario.toLowerCase(); // aqui ele pega o nome do user coloca e minusculo 

  // Como já importamos o 'db' lá em cima, podemos usar aqui normal
  db.get("SELECT * FROM funcionarios WHERE nome = ?", [nomeBuscado], (err, row) => { // aqui nos pesquisamos o nome se der um erro ele responde erro interno se ele achar ele fala o nome do funcionario e quantos dia ele tem
    if (err) return res.status(500).send("Erro interno.");
    
    if (row) {
      res.send(`O funcionário(a) ${row.nome} tem ${row.diasRestantes} dias de férias restantes.`);
    } else {
      res.status(404).send('Funcionário não encontrado no banco de dados.');// aqui caso o funcionario nao seja achado 
    }
  });
});


// const = variavel //express e o nome da variavel// require comondo do node para importa a bliblioteca //('express") o nome exato do pacote
// app nosso aplicativo express . para acessar funçoes internas do obj //get  um funçao para que cria um rota para ler dados 
// '/' Texto que representa o caminho da URL. A barra / sozinha significa a página inicial.
//,: Separa o caminho (a URL) da ação que vai acontecer
//(req, res): Parâmetros da função. req (request) traz os dados de quem acessou. res (response) traz as ferramentas para você responder.
//=>: Chamada de Arrow Function (função de seta). Substitui a palavra function e significa "faça a seguinte ação".


// banco de dados 
