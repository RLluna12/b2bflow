# b2bflow – Desafio Estágio Python

Projeto que lê contatos cadastrados no **Supabase** e envia mensagens personalizadas via **WhatsApp** utilizando a **Z-API**.

---

## Fluxo

```
Supabase (tabela contacts) → Python → Z-API → WhatsApp
```

---

## Setup da Tabela no Supabase

1. Acesse [supabase.com](https://supabase.com) e crie um projeto gratuito.
2. No **SQL Editor**, execute:

```sql
CREATE TABLE contacts (
  id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name  TEXT NOT NULL,
  phone TEXT NOT NULL
);

INSERT INTO contacts (name, phone) VALUES
  ('João Silva',  '5511999990001'),
  ('Maria Souza', '5511999990002'),
  ('Pedro Lima',  '5511999990003');
```

> O campo `phone` deve estar no formato internacional sem `+` (ex.: `5511999990001`).

---

## Variáveis de Ambiente

Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
cp .env.example .env
```

| Variável           | Onde encontrar                                         |
|--------------------|--------------------------------------------------------|
| `SUPABASE_URL`     | Supabase → Project Settings → API → Project URL       |
| `SUPABASE_KEY`     | Supabase → Project Settings → API → anon public key   |
| `ZAPI_INSTANCE_ID` | Z-API → painel da instância                           |
| `ZAPI_TOKEN`       | Z-API → painel da instância → Token                   |
| `ZAPI_CLIENT_TOKEN`| Z-API → Account → Client-Token                        |

---

## Como Rodar

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/b2bflow-challenge.git
cd b2bflow-challenge

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# 5. Execute
python main.py
```

## Publicar no GitHub

1. Crie um repositório público no GitHub (ex.: `b2bflow-challenge`).
2. No seu diretório local, inicialize o repositório, adicione arquivos e faça commit:

```bash
git init
git add .
git commit -m "feat: inicial - envia contatos Supabase via Z-API"
# adicione o remote substituindo <URL> pelo repo que você criou
git remote add origin <URL>
git branch -M main
git push -u origin main
```

Se preferir, me envie a URL remota ou um token de acesso (PAT) e eu posso tentar empurrar o repositório para você (requer permissão). Caso contrário, siga os comandos acima.

### Exemplo de saída esperada

```
2025-06-19 10:00:00 [INFO] === Iniciando envio de mensagens ===
2025-06-19 10:00:01 [INFO] Buscando contatos no Supabase...
2025-06-19 10:00:01 [INFO] 3 contato(s) encontrado(s).
2025-06-19 10:00:02 [INFO] Enviando mensagem para João Silva (5511999990001)...
2025-06-19 10:00:02 [INFO] ✅ Mensagem enviada com sucesso para João Silva (5511999990001)
...
2025-06-19 10:00:04 [INFO] === Concluído | Enviados: 3 | Falhas: 0 ===
```

---

## Tecnologias

- Python 3.11+
- [Supabase Python SDK](https://github.com/supabase-community/supabase-py)
- [Z-API](https://z-api.io)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [requests](https://pypi.org/project/requests/)
