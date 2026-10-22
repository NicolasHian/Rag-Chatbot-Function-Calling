-- aqui criamos a tabela e garantimos que nao tem teremos nomes repetidos 
CREATE TABLE IF NOT EXISTS funcionarios ( --cria uma tabela chamada funcionarios que funciona como um planilha o IF NOT EXISTS que dizer so cria se ainda nao existir 
    nome TEXT UNIQUE, -- criamos uma coluna nome que guarda o texto o UNIQUE proibe dois funcionarios com o mesmo nome 
    diasRestantes INTEGER -- terminamos de criar a tabela 
);

INSERT OR IGNORE INTO funcionarios (nome, diasRestantes) VALUES ('nicolas', 15); -- coloca um linha na tabela nesse caso nicolas com 15 dias de ferias o OR IGNORE que dizer e já existir alguém com esse nome, não faz nada e não dá erro
INSERT OR IGNORE INTO funcionarios (nome, diasRestantes) VALUES ('raiane', 30);
INSERT OR IGNORE INTO funcionarios (nome, diasRestantes) VALUES ('maria', 5);