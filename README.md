# IF678-ChatCIn

Projeto da cadeira de Infraestrutura de Comunicação do CIn-UFPE para implementação de um sistema de chat em grupo (ChatCIn) usando o protocolo de comunicação UDP. O projeto está dividido em três partes:

- **Project 1**: Implementação do envio e recebimento de arquivos usando UDP.
- **Project 2**: Implementação do RDT 3.0 sobre UDP na camada de aplicação, utilizando o código de transferência de arquivos da primeira parte.
- **Project 3**: Criação de um chat em grupo utilizando o RDT 3.0 implementado na segunda parte.

---

## 📂 Estrutura do Repositório

```
📁 IF678-ChatCIn
│
├── 📁 project_1
│   ├── 📁 files  # Armazena os arquivos
│   ├── client.py  # Código principal do cliente
│   ├── server.py  # Código principal do servidor
│
├── 📁 project_2
│   ├── client.py  # Cliente utilizando RDT 3.0
│   ├── rdt.py  # Implementação do RDT 3.0
│   ├── server.py  # Servidor utilizando RDT 3.0
│   ├── rdt.py  # Implementação do RDT 3.0
│
├── 📁 project_3
│   ├── 📁 client  # Implementação do chat em grupo
│   ├── 📁 server  # Implementação do chat em grupo
```

---

## 👨‍💻 Desenvolvimento do Projeto
A implementação foi feita de forma colaborativa, onde cada membro participou de sessões de desenvolvimento sem uma divisão rígida de tarefas específicas.

---

## 🔥 Como Rodar o Projeto

1. Certifique-se de ter o Python instalado.
2. Entre na pasta `server` do projeto correspondente e inicie o servidor:
   ```sh
   cd project_1
   python3 server.py
   ```
3. Em outra instância do terminal, entre na pasta `client` e execute o cliente:
   ```sh
   cd project_1
   python3 client.py
   ```
4. No **Project 1**, teste o envio e recepção de arquivos usando o protocolo UDP.
5. No **Project 2**, teste a confiabilidade do RDT 3.0.
6. No **Project 3**, teste o funcionamento do chat em grupo.

---

## 🛠️ Tecnologias Utilizadas
- **Python**
- **UDP Sockets** (via `socket`)
- **RDT 3.0**

---

## 📌 Considerações Finais
Este projeto visa implementar um sistema confiável de comunicação baseado no protocolo UDP, evoluindo desde a simples transferência de arquivos até a criação de um chat em grupo utilizando o protocolo RDT 3.0. Boa implementação! 🚀
