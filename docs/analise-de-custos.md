# Análise de custos

Projeto: Helpdesk API com Prometheus e Grafana, em 5 containers Docker numa única EC2 `t3.micro` (`us-east-1`, 8 GiB de EBS).

## Custo da arquitetura atual (EC2)

| Item | Cálculo | Custo/mês |
|---|---|---|
| EC2 `t3.micro` (Linux, sob demanda) | US$ 0,0104/h × 730 h | US$ 7,59 |
| IPv4 público | US$ 0,005/h × 730 h | US$ 3,65 |
| Volume EBS de 8 GiB (gp3) | 8 × US$ 0,08 | US$ 0,64 |
| **Total ligado 24/7** | | **≈ US$ 11,88** (≈ US$ 0,39/dia) |

Com a instância parada, o custo cai para só o EBS: **≈ US$ 0,64/mês** (≈ US$ 0,02/dia). O IPv4 público automático é liberado ao parar a instância e deixa de ser cobrado.

Não inclui transferência de dados, irrelevante nesse volume de tráfego.

## Gasto real no período

- Gasto até 26/10: US$ 7,64 (previsão do mês: US$ 9,95), abaixo do teto de US$ 11,88 porque a instância não ficou ligada o tempo todo.
- Créditos: AWS Free Tier (US$ 84,95 restantes) e três créditos "Explore AWS" de US$ 20, válidos até 02/03/2027.
- Até a validade dos créditos, o pior caso (ligado 24/7) seria ≈ US$ 51, dentro do saldo. A fatura (Bills) fica em US$ 0,00 depois dos créditos.

## Controles de custo aplicados

1. **Parar a EC2 ao fim de cada sessão.** Maior economia, de ≈ US$ 0,39 para ≈ US$ 0,02 por dia.
2. **Sem Elastic IP.** Um endereço IPv4 público custa US$ 0,005/h. O endereço automático some ao parar a instância, o que evita pagar por ele parado. O custo é o IP mudar a cada reinício, o que exige atualizar o Security Group.
3. **Orçamento `lab-guardrail`** (AWS Budgets) com alertas em 85% do custo real, 100% do custo real e 100% do custo previsto.
   - O limite inicial era de US$ 5, abaixo do custo real do projeto. Os alertas nasceram disparados e continuaram disparados, e um alerta que sempre dispara deixa de ser notado.
   - O limite foi ajustado para **US$ 12**, o custo real do projeto ligado 24/7. Agora um alerta indica gasto acima do esperado.
   - O orçamento **avisa, não bloqueia**: não há ação automática configurada.
4. **Security Group restrito ao IP do operador** nas portas 22, 8000, 9090 e 3000. O banco PostgreSQL não tem porta publicada e só é alcançável pela rede Docker.

## Alternativa serverless

Mesma API, reescrita em API Gateway (HTTP API) + Lambda + DynamoDB.

Premissas (minhas, não medidas): 0,65 req/s médios (≈ 1,71 milhão de requisições/mês, o tráfego do gerador de carga); 40% das chamadas são escritas e 60% leituras; cada execução Lambda leva 100 ms com 256 MB (0,025 GB-s).

| Componente | Cálculo | Sem free tier | Com free tier |
|---|---|---|---|
| API Gateway HTTP API | 1,71 M × US$ 1,00/M | 1,71 | 1,71 |
| Lambda, requisições | 1,71 M × US$ 0,20/M | 0,34 | 0,14 |
| Lambda, duração | 42.700 GB-s × US$ 0,0000166667 | 0,71 | 0,00 |
| DynamoDB, gravações (on-demand) | 0,68 M × US$ 0,625/M | 0,43 | 0,43 |
| DynamoDB, leituras (on-demand) | 1,03 M × US$ 0,125/M | 0,13 | 0,13 |
| **Total** | | **≈ US$ 3,32** | **≈ US$ 2,41** |

O free tier do Lambda é de 1 milhão de requisições e 400 mil GB-s por mês. O armazenamento do DynamoDB (25 GB grátis) não gera custo aqui. Não inclui CloudWatch Logs nem o free tier de 12 meses do API Gateway para contas novas.

**Ponto de equilíbrio:** o custo variável do serverless é de ≈ US$ 1,94 por milhão de requisições. Contra os US$ 11,88 fixos da EC2, o equilíbrio fica em torno de **6 milhões de requisições por mês (≈ 2,3 req/s médios)**. Abaixo disso o serverless é mais barato, acima a EC2 passa a compensar.

Ressalvas:
- A alternativa exigiria reescrever a aplicação. O DynamoDB é NoSQL e não substitui o PostgreSQL sem mudar o modelo de dados.
- O `GET /chamados` devolve todos os registros, sem paginação. No DynamoDB isso viraria uma varredura (`Scan`) cara à medida que a tabela crescesse.
- Prometheus e Grafana auto-hospedados precisam de uma máquina ligada o tempo todo. No serverless a observabilidade seria feita com CloudWatch.

## Decisão

Para este projeto, a EC2 foi escolhida porque o objetivo é **aprender e demonstrar observabilidade com Prometheus e Grafana, Docker, PostgreSQL e resposta a incidente**. Essa pilha pede um ambiente que fique ligado e sob controle do operador. Em tráfego baixo e sem esse objetivo didático, a opção serverless custaria menos (≈ US$ 2,41 a US$ 3,32 contra US$ 11,88 por mês).

## Fontes dos preços (us-east-1)

- [Holori, t3.micro](https://calculator.holori.com/aws/ec2/t3.micro/us-east-1)
- [AWS News Blog, cobrança de IPv4 público](https://aws.amazon.com/blogs/aws/new-aws-public-ipv4-address-charge-public-ip-insights)
- [Computing for Geeks, EBS gp3](https://computingforgeeks.com/aws-costs-explained-real-numbers/)
- [AWS Lambda pricing](https://aws.amazon.com/lambda/pricing/)
- [AWS Compute Blog, HTTP APIs](https://aws.amazon.com/blogs/compute/announcing-http-apis-for-amazon-api-gateway)
- [Bytebase, DynamoDB pricing](https://www.bytebase.com/blog/understanding-dynamodb-pricing/)

Valores consultados em 26/10/2026. Conferir na calculadora oficial da AWS antes de usar para decisões reais.