## IF678-ChatCIn
Projeto da cadeira de Infraestrutura de Comunicação do CIn-UFPE para implementação de um sistema de chat em grupo (ChatCIn) usando protocolo de comunicação UDP. O projeto está dividido em duas partes principais:

- **Server**: Contém o código do servidor em Python, juntamente com as pastas `utils` e `files`, que auxiliam no gerenciamento dos arquivos recebidos e enviados.
- **Client**: Contém o código do cliente em Python, além das pastas `utils` e `files` específicas para a comunicação com o servidor.

Cada tipo de arquivo terá um fluxo de publicação e recebimento separado, sendo tratado por arquivos específicos dentro do diretório `utils`.

---

## 📂 Estrutura do Projeto

```
📁 IF678-ChatCIn
│
├── 📁 server
│   ├── server.py  # Código principal do servidor
│   ├── 📁 utils
│   │   ├── 📁 Publisher.py  # Responsável pela publicação
        ├── 📁 FileManager  # Responsável pelo gerenciamento
│   │   ├── 📁 Interpreter.py  # Responsável pelo recebimento
│   ├── 📁 files  # Armazena os arquivos do servidor
│
├── 📁 client
│   ├── client.py  # Código principal do cliente
│   ├── 📁 utils
│   │   ├── 📁 Publisher.py  # Responsável pela publicação
        ├── 📁 FileManager  # Responsável pelo gerenciamento
│   │   ├── 📁 Interpreter.py  # Responsável pelo recebimento
│   ├── 📁 files  # Armazena os arquivos do cliente
```

---

## 👨‍💻 Responsabilidades da Equipe
Cada membro da equipe será responsável por implementar a funcionalidade de publicação e recebimento de um tipo de arquivo específico:

| Membro        | Tipo de Arquivo | Status |
|--------------|----------------|----------------|
| João Marcelo | PDF            |       ❌       |
| João Pedro   | MP3            |       ❌       |
| Alberto      | MP4            |       ❌       |
| Bruno        | PNG            |       ❌       |
| Marco        | JPEG           |       ❌       |
| Victor       | TXT            |       ✅       |

Cada arquivo manipulado deve ser armazenado corretamente na pasta `files`, garantindo que o envio e recebimento de diferentes tipos de arquivos seja validado de forma independente.

---

## ✅ Checklist de Implementação

### 📌 Para cada tipo de arquivo, deve-se:

- [ ] Alterar a função em `server/utils/Publisher.py` para publicação do arquivo.
- [ ] Alterar a função em `server/utils/Interpreter.py` para recebimento do arquivo.
- [ ] Alterar a função em `client/utils/Publisher.py` para envio do arquivo.
- [ ] Alterar a função em `client/utils/Interpreter.py` para recepção do arquivo.
- [ ] Testar a publicação e recepção dos arquivos, garantindo que funcionam corretamente.
- [ ] Cada arquivo deve ser salvo em `server/files` e `client/files` de forma independente.

---

## 🔥 Como Rodar o Projeto

1. Certifique-se de ter o Python instalado.
2. Rode o servidor:
   ```sh
   cd server
   python3 server.py
   ```
3. Em outra instância do terminal, rode o cliente:
   ```sh
   cd client
   python3 client.py
   ```
4. Teste o envio e recepção de arquivos para garantir que cada tipo está funcionando corretamente.

---

## 🛠️ Tecnologias Utilizadas
- **Python**
- **UDP Sockets** (via `socket`)
- **Manipulação de Arquivos** (via `os` e bibliotecas específicas como `PyPDF2` para PDFs)

---

## 📌 Considerações Finais
Este projeto busca garantir a transmissão eficiente de diferentes tipos de arquivos dentro de uma rede. Cada membro da equipe deve focar na implementação e testes de seu tipo de arquivo específico, garantindo que todas as funcionalidades operem corretamente antes da entrega final. Boa implementação! 🚀

