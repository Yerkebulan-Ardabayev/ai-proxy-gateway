# AI Proxy Gateway

DevOps-проект для изучения полного цикла разработки и деплоя приложения.

## Архитектура

FastAPI-приложение с 4 эндпоинтами, упакованное в Docker, развёрнутое в Kubernetes через Helm.

## Стек технологий

- **Приложение:** Python, FastAPI, Prometheus metrics
- **Контейнеризация:** Docker (multi-stage, ~65MB)
- **Оркестрация:** Kubernetes (Minikube), Helm
- **CI/CD:** GitHub Actions (lint → test → build)
- **Мониторинг:** Prometheus, Grafana
- **Инфраструктура:** Ubuntu Server 24.04 ARM, VMware Fusion

## API эндпоинты

| Эндпоинт | Описание |
|-----------|----------|
| /health | Проверка состояния |
| /api/chat | Отправка сообщения |
| /api/history | История сообщений |
| /api/stats | Статистика запросов |

## Быстрый старт

### Docker Compose

```bash
docker-compose up -d
```

### Kubernetes (Helm)

```bash
kubectl create namespace ai-proxy
helm install ai-proxy helm/ai-proxy -n ai-proxy
```

### Проверка

```bash
curl http://ai-proxy.local/health
```

## Структура проекта

```
ai-proxy-gateway/
├── app/
│   ├── main.py              # FastAPI приложение
│   └── metrics.py           # Prometheus метрики
├── tests/
│   └── test_api.py          # 5 тестов (pytest)
├── k8s/
│   ├── deployment.yaml      # 2 реплики
│   ├── service.yaml         # NodePort
│   ├── ingress.yaml         # ai-proxy.local
│   └── hpa.yaml             # автоскейлинг 2-5 подов
├── helm/
│   └── ai-proxy/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── ingress.yaml
│           └── hpa.yaml
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # 4 сервиса
└── .github/
    └── workflows/
        └── ci.yml           # GitHub Actions pipeline
```

## CI/CD Pipeline

GitHub Actions: **flake8** (lint) → **pytest** (test) → **docker build** (build)

## Фазы проекта

- [x] Фаза 1: Linux (Ubuntu Server VM)
- [x] Фаза 2: Приложение (FastAPI)
- [x] Фаза 3: Docker (multi-stage + compose)
- [x] Фаза 4: CI/CD (GitHub Actions)
- [x] Фаза 5: Kubernetes (манифесты + Helm)
- [ ] Фаза 6: Мониторинг в K8s
- [ ] Фаза 7: IaC + GitOps (Ansible, ArgoCD)
- [ ] Фаза 8: Документация и портфолио
