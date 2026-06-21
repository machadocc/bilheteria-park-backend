# Bilheteria Park — Backend

API REST em FastAPI + PostgreSQL + Redis para gestão de bilheteria de parques.

## Estrutura dos serviços

```
docker-compose.yml  ← sobe TUDO (backend + frontend + db + redis)
├── web             → FastAPI na porta 8000
├── frontend        → Nginx + React na porta 80
├── db              → PostgreSQL na porta 5433 (host)
└── redis           → Redis na porta 6379
```

## Como rodar (desenvolvimento)

### 1. Configure o `.env`

Copie o exemplo e ajuste as variáveis:

```bash
cp .env.example .env
```

Variáveis obrigatórias:

| Variável | Descrição | Padrão |
|---|---|---|
| `ADMIN_USERNAME` | Usuário do painel admin | `admin` |
| `ADMIN_PASSWORD` | Senha do painel admin | `changeme123` |
| `JWT_SECRET_KEY` | Chave secreta para JWT (troque em produção) | — |
| `ENVIRONMENT` | `development` ou `production` | `development` |

> ⚠️ O `.env` usa `ENVIRONMENT` (com V). Versões antigas tinham o typo `ENRIONMENT` — se vier de uma versão antiga, corrija.

### 2. Suba todos os serviços

O `docker-compose.yml` do backend inclui o frontend. **Rode tudo a partir da pasta do backend:**

```bash
# O frontend deve estar em ../bilheteria-park-frontend (pasta irmã)
docker compose up --build
```

Ou em background:

```bash
docker compose up -d --build
```

### 3. Acesse

| Serviço | URL |
|---|---|
| Site público (compra de ingressos) | http://localhost |
| Painel admin | http://localhost/admin/login |
| API (docs interativos) | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

## Estrutura de pastas esperada

```
/
├── bilheteria-park-backend/   ← você está aqui
│   ├── docker-compose.yml     ← sobe tudo
│   ├── .env
│   ├── app/
│   └── ...
└── bilheteria-park-frontend/  ← pasta irmã (mesma raiz)
    ├── nginx.conf
    ├── Dockerfile
    └── src/
```

## Rotas da API

### Público (sem autenticação)
| Método | Rota | Descrição |
|---|---|---|
| GET | `/eventos/` | Lista eventos ativos com preço mínimo |
| GET | `/eventos/{id}` | Detalhes de um evento |
| POST | `/compras` | Compra ingresso (nome, email, CPF) |
| POST | `/auth/login` | Login admin → retorna JWT |

### Admin (requer `Authorization: Bearer <token>`)
| Método | Rota | Descrição |
|---|---|---|
| POST | `/admin/eventos` | Criar evento |
| PUT | `/admin/eventos/{id}` | Editar evento |
| DELETE | `/admin/eventos/{id}` | Remover evento |
| GET | `/admin/vendas` | Relatório de vendas por evento |

### Gestão interna
| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/events/` | Listagem/criação de eventos |
| GET/POST | `/batches/` | Lotes de ingressos |
| GET/POST | `/customers/` | Clientes |
| GET | `/dashboard/summary` | Resumo do painel |

## Migrations

O banco é criado automaticamente no startup via `create_all`. Migrações de colunas adicionadas posteriormente rodam automaticamente em `database.py → run_migrations()`.

Se precisar rodar a migration manualmente:

```bash
docker compose exec web python -c "from app.database import run_migrations; run_migrations()"
```

## Variáveis de ambiente completas

```env
DATABASE_URL=postgresql://ticketing:ticketing@localhost:5432/ticketing
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme123
JWT_SECRET_KEY=sua-chave-secreta-aqui
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
LOG_LEVEL=INFO
IP_FRONT=                # usado apenas em ENVIRONMENT=production
AWS_REGION=
AWS_SQS_QUEUE_URL=
AWS_SNS_TOPIC_ARN=
```
