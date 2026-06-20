# Bilheteria Park - Backend

Projeto backend em Python com FastAPI para um sistema de bilheteria de parque de diversão.

## Objetivo
- Desenvolver API backend pronta para integração com frontend futuro
- Atender requisitos de sistemas distribuídos, observabilidade e deploy
- Preparar arquitetura para AWS, Kubernetes, Redis, SQS/SNS e banco relacional com SQLAlchemy

## Conteúdo
- `app/` - código do serviço FastAPI
- `Dockerfile` e `docker-compose.yml` - execução local com PostgreSQL e Redis
- `k8s/` - manifestos de Kubernetes para aplicação, banco e cache

## Execução local
1. `docker compose up --build`
2. A API estará disponível em `http://localhost:8000`
3. Documentação interativa: `http://localhost:8000/docs`

## Iniciar banco de dados localmente
A aplicação cria as tabelas automaticamente no startup.

## Observabilidade
- Endpoint de saúde: `/health`
- Métricas Prometheus: `/metrics`
