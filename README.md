# Jiu-Jitsu Academy API

API REST desenvolvida com **Python, Django e Django Ninja** para gerenciar alunos, registrar aulas concluídas e acompanhar o progresso entre faixas em uma academia de Jiu-Jitsu.

Este repositório contém **somente o backend**. Os endpoints podem ser explorados pela documentação interativa do Django Ninja, sem necessidade de um frontend.

## Funcionalidades

- Cadastro e listagem de alunos.
- Atualização parcial dos dados cadastrais.
- Registro de uma ou mais aulas concluídas por aluno.
- Consulta do total de aulas e das aulas restantes para a próxima faixa.
- Validação de e-mail único, quantidade de aulas e regras de graduação definidas para o projeto.
- Testes automatizados da API e do cálculo de progressão.

## Tecnologias

- **Python** — linguagem principal.
- **Django** — modelos, ORM, migrações e persistência.
- **Django Ninja** — endpoints REST, validação e documentação OpenAPI/Swagger.
- **SQLite** — banco de dados utilizado no desenvolvimento.
- **Pydantic** — validação dos dados recebidos pela API.
- **Pytest + pytest-django** — testes automatizados.

## Estrutura do projeto

```text
jiujitsu-academy-api/
├── core/                    # Configuração, API principal e URLs do Django
│   ├── api.py
│   ├── settings.py
│   └── urls.py
├── treino/                  # Aplicação de alunos e aulas
│   ├── migrations/
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_api.py
│   │   └── test_graduacao.py
│   ├── api.py                # Rotas HTTP
│   ├── models.py             # Alunos e AulasConcluidas
│   ├── schemas.py            # Schemas de entrada e saída
│   └── graduacao.py          # Regra de cálculo de aulas
├── .env.example              # Exemplo de configurações locais
├── .gitignore
├── manage.py
├── pytest.ini
├── requirements.txt
└── README.md
```

> A estrutura acima reflete a organização proposta para publicação. Os arquivos de configuração e testes devem estar presentes na versão enviada ao GitHub.

## Como executar localmente

### 1. Pré-requisitos

- Python 3.12 ou versão compatível com as dependências do `requirements.txt`.
- Git (opcional, para clonar o repositório).

Clone o repositório (após publicá-lo) ou abra a pasta do projeto no terminal:

```bash
git clone URL_DO_SEU_REPOSITORIO
cd NOME_DA_PASTA_CLONADA
```

> Substitua `URL_DO_SEU_REPOSITORIO` pela URL real do GitHub depois da publicação e `NOME_DA_PASTA_CLONADA` pelo nome da pasta criada.

### 2. Ambiente virtual

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
python -m pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz, a partir do `.env.example`:

```dotenv
DJANGO_SECRET_KEY=substitua_por_uma_chave_aleatoria
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

Para gerar uma chave:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

O `.env` é privado e **não deve ser enviado ao GitHub**. Esta configuração pressupõe que `core/settings.py` já carrega o `.env` (por exemplo, com `python-dotenv`).

### 5. Aplicar migrações e iniciar o servidor

```bash
python manage.py migrate
python manage.py check
python manage.py runserver
```

A documentação interativa ficará disponível em:

**http://127.0.0.1:8000/api/docs**

## Endpoints

Com a configuração atual de rotas (`/api/`):

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/` | Cadastra um aluno |
| `GET` | `/api/alunos/` | Lista alunos cadastrados |
| `GET` | `/api/progresso_aluno/?email_aluno=...` | Consulta o progresso de um aluno |
| `POST` | `/api/aula_realizada/` | Registra aulas concluídas |
| `PATCH` | `/api/alunos/{aluno_id}` | Atualiza campos específicos de um aluno |

### Exemplo: cadastrar aluno

**`POST /api/`**

```json
{
  "nome": "Ana Silva",
  "email": "ana@example.com",
  "faixa": "B",
  "data_nascimento": "2001-05-15"
}
```

Em caso de sucesso, a API responde com **HTTP 201** e os dados do aluno, incluindo o identificador gerado.

### Exemplo: registrar aulas

**`POST /api/aula_realizada/`**

```json
{
  "email_aluno": "ana@example.com",
  "qtd": 5
}
```

O registro guarda a faixa do aluno no momento da inserção. Na versão atual, a quantidade permitida por requisição é de **1 a 100 aulas**.

### Exemplo: atualizar aluno

**`PATCH /api/alunos/1`**

```json
{
  "nome": "Ana Maria Silva"
}
```

O método `PATCH` permite alterar apenas os campos enviados.

## Progressão de faixas

O projeto considera as faixas **branca, azul, roxa, marrom e preta**. O número de aulas associado à próxima faixa é calculado por uma fórmula logarítmica implementada em `treino/graduacao.py`.

Na consulta de progresso, a API considera as aulas registradas **na faixa atual** e calcula quantas faltam para atingir a quantidade definida pela fórmula. Para a faixa preta, o campo `aulas_necessarias_para_proxima_faixa` retorna `null`, pois não há uma próxima faixa modelada.

**Importante:** essa lógica é uma **regra demonstrativa do projeto**, não um critério oficial de graduação em Jiu-Jitsu. O sistema calcula o progresso, mas **não promove automaticamente** o aluno para outra faixa.

## Testes automatizados

Os testes verificam cenários como:

- Cadastro válido, e-mail duplicado e restrições de graduação por idade.
- Listagem e atualização parcial de alunos.
- Consulta de progresso, incluindo aluno inexistente e faixa preta.
- Registro de aulas e rejeição de quantidades inválidas.
- Cálculo matemático e validação de níveis de faixa.

Para executar todos os testes:

```bash
python -m pytest -v
```

Para executar separadamente:

```bash
python -m pytest treino/tests/test_api.py -v
python -m pytest treino/tests/test_graduacao.py -v
```

O `pytest-django` utiliza um banco de testes separado do banco local de desenvolvimento.

## Observações de segurança e limitações

- Não publique `.env`, `db.sqlite3`, ambientes virtuais ou arquivos `__pycache__`.
- O projeto **ainda não implementa autenticação e autorização**: os endpoints devem ser utilizados apenas em ambiente de desenvolvimento ou demonstração controlada.
- O banco SQLite é utilizado para desenvolvimento local; configurações de produção precisam de revisão específica.
- Este repositório não contém interface web (frontend).

## Autor

**Ailesson** — [GitHub](https://github.com/Ailesson)

Projeto desenvolvido para estudo e demonstração de práticas de desenvolvimento de APIs REST com Python.
