const sqlite3 = require('sqlite3').verbose(); // Importa o "gerenciador" do banco de dados. Aquele .verbose() no final é um comando para ele ser "tagarela": se acontecer qualquer erro no banco, ele vai imprimir mensagens bem detalhadas no termina
const fs = require('fs');// Importa o File System (Sistema de Arquivos). É uma ferramenta que já vem instalada no Node.js. O trabalho dela é simples: ler, criar, modificar ou apagar arquivos de texto do seu computador.

// 1. Cria a conexão
const db = new sqlite3.Database('./empresa.db'); // Aqui é onde o cofre é aberto. O código procura um arquivo chamado empresa.db na sua pasta. Se o arquivo não existir, o SQLite cria um novinho em folha na mesma hora. A partir dessa linha, a variável db se torna o "controle remoto" do seu banco de dados.

// 2. Lê e roda o seu arquivo setup.sql
const scriptSql = fs.readFileSync('./setup.sql', 'utf8'); // pedimos para ele ler o arquivo setup.sql que criamos antes. O 'utf8' avisa que é um arquivo de texto comum (que tem acentos, cedilha, etc). Ele pega todo o texto do SQL e guarda dentro da variável scriptSql
db.exec(scriptSql, (err) => { //O comando .exec() pega todo aquele texto SQL que acabamos de ler e manda o banco de dados executar de uma vez só (criar a tabela, inserir os dados). A parte do (err) é um inspetor de qualidade. Quando a execução termina, ele verifica: "Deu erro?"
  if (err) {
    console.error("Erro ao configurar banco:", err);
  } else {
    console.log("Banco configurado e pronto para uso!");
  }
});

// 3. A PORTA DE SAÍDA: exporta a conexão para quem precisar
module.exports = db; // Essa é a nossa porta de saída. Você está empacotando o controle remoto do banco (db) e deixando ele na vitrine.