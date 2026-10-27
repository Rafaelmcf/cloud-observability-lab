# Runbook: API Helpdesk fora do ar

Alerta: **API Helpdesk fora do ar** (Grafana, pasta `Helpdesk`, grupo `helpdesk-api`)

## O que o alerta significa

A métrica `up{job="helpdesk-api"}` ficou abaixo de 1 por mais de 1 minuto. O Prometheus não consegue coletar métricas de `helpdesk-container:8000`: a API está parada ou inacessível.

- Avaliação: a cada 1 minuto
- Pending period: 1 minuto
- Contact point: `empty` (laboratório; em produção seria Slack ou e-mail da equipe)

## Impacto

Os chamados não podem ser criados, listados nem atualizados enquanto a API estiver parada.

## Diagnóstico

Na EC2, conectado por SSH:

1. Listar todos os containers, inclusive os parados:

```bash
   sudo docker ps -a
```

   Se `helpdesk-container` aparecer como `Exited`, a API está parada.

2. Ler o código de saída:
   - `Exited (0)`: encerramento normal. Alguém parou o container.
   - `Exited (1)`, `Exited (137)` ou outro código diferente de zero: queda por erro ou falta de memória. Investigar mais fundo.

3. Ler as últimas linhas do log:

```bash
   sudo docker logs --tail 20 helpdesk-container
```

   Procurar por `Traceback`, `Error` ou `Killed`.

4. Se o container estiver `Up` e o alerta continuar disparado, o problema é de rede entre o Prometheus e a API. Conferir o target em `http://<IP-DA-EC2>:9090/targets`.

## Resolução

```bash
sudo docker start helpdesk-container
```

## Verificação

1. `sudo docker ps`: o `helpdesk-container` deve aparecer como `Up`.
2. No Grafana, o alerta volta a **Normal** em até 2 minutos.
3. O painel "Requisições por segundo" volta a registrar tráfego.

## Registro do incidente simulado

| Hora | Evento |
|---|---|
| 25/10 ~20:15 | `docker stop helpdesk-container` (incidente simulado) |
| 25/10 ~20:17 | Alerta em **Pending** |
| 25/10 ~20:18 | Alerta em **Firing** |
| 25/10 ~21:07 | Diagnóstico: `docker ps -a` mostra `Exited (0)`; logs mostram desligamento limpo |
| 26/10 ~15:40 | `docker start helpdesk-container` |
| 26/10 ~15:59 | Alerta de volta a **Normal** |

O incidente foi deixado aberto de propósito por cerca de 19 horas, então esse intervalo não representa um tempo real de resposta. O alerta funcionou como esperado: disparou cerca de 3 minutos depois da queda.

**Causa raiz:** container parado manualmente (`Exited (0)`).

**Evidências:** `_capturas/fase6-alertas/`

## Prevenção

- O container usa `--restart unless-stopped`, mas essa política **não** reinicia um container parado manualmente com `docker stop`. Ela só cobre quedas e reinicializações da instância.
- Em produção, enviar o alerta a um canal que a equipe veja (Slack, e-mail ou PagerDuty), em vez do contact point vazio.
- Adicionar alertas de taxa de erro 5xx e de latência p95.