# ☁️ Cloud Observability Lab

Laboratório de **observabilidade na AWS** — infraestrutura provisionada do zero com Terraform, monitoramento com Prometheus e Grafana, e resposta a incidentes documentada em runbooks.

> 🎯 **Objetivo:** simular o dia a dia de um time de Cloud Operations — provisionar, monitorar, receber alertas e responder a incidentes — aplicando boas práticas de IaC, segurança e FinOps desde o primeiro commit.

---

## 🏗️ Arquitetura atual

```
                  ┌────────────────────────────────────────────┐
                  │            VPC 10.0.0.0/16 (lab-vpc)       │
                  │                                            │
                  │   ┌────────────────────────────────────┐   │
 Internet ◄─────────► │  Subnet pública 10.0.1.0/24        │   │
        (lab-igw) │   │  us-east-1a                        │   │
                  │   │                                    │   │
                  │   │   🔜 EC2 + Docker (Fase 2)         │   │
                  │   │                                    │   │
                  │   └────────────────────────────────────┘   │
                  │                                            │
                  │   🔒 Security Group (lab-sg):              │
                  │      • SSH (22)     → apenas meu IP        │
                  │      • Grafana (3000) → apenas meu IP      │
                  │      • App (80)     → público              │
                  └────────────────────────────────────────────┘
```

## 📈 Progresso

| Fase | Conteúdo | Status |
|:---:|---|:---:|
| 0 | Fundação: repositório, IAM com menor privilégio, credenciais, AWS Budget | ✅ |
| 1 | Rede do zero: VPC, subnet pública, Internet Gateway, rotas e Security Group | ✅ |
| 2 | Servidor: EC2 via Terraform com Docker instalado por automação (user_data) | 🔜 |
| 3 | Observabilidade: Prometheus, Grafana, Node Exporter, cAdvisor e dashboards | 🔜 |
| 4 | Alertas com Alertmanager + incidentes simulados + runbooks | 🔜 |
| 5 | Bônus: health-check em bash e pipeline de validação do Terraform | 🔜 |

### ✅ Fase 0 — Fundação
- Estrutura de projeto organizada por responsabilidade (`terraform/`, `docker/`, `runbooks/`, `scripts/`)
- `.gitignore` protegendo state, chaves e variáveis sensíveis **antes do primeiro commit**
- Usuário IAM dedicado (`terraform-lab`) com política mínima — **princípio do menor privilégio**, sem uso da conta root
- **AWS Budget** configurado como guardrail de custo desde o dia zero (FinOps)

### ✅ Fase 1 — Rede do zero
- **VPC própria** (`10.0.0.0/16`) com DNS habilitado — sem uso da VPC default
- **Subnet pública** (`10.0.1.0/24`) em `us-east-1a` com IP público automático
- **Internet Gateway + route table** com rota `0.0.0.0/0` associada à subnet
- **Security Group** restritivo: SSH e Grafana liberados apenas para meu IP (via variável, fora do versionamento); somente a porta 80 pública
- Todos os recursos com **tags padronizadas** (`Project`, `ManagedBy`, `Owner`) via `default_tags` do provider

## 🧠 Decisões técnicas

| Decisão | Motivo |
|---|---|
| VPC própria em vez da default | Segurança por desenho + domínio dos componentes de rede |
| IP pessoal em `terraform.tfvars` (não versionado) | Separação entre código (público) e valores (locais/sensíveis) |
| `default_tags` no provider | Rastreabilidade e gestão de custo por projeto |
| Região `us-east-1` | Menor custo e compatibilidade com free tier |
| Fluxo `fmt → validate → plan → apply` em toda mudança | Nenhuma alteração aplicada sem revisão do plano |

## 🛠️ Stack

![Terraform](https://img.shields.io/badge/Terraform-%235835CC.svg?style=for-the-badge&logo=terraform&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazonwebservices&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)

## 📦 Estrutura do repositório

```
cloud-observability-lab/
├── terraform/
│   ├── providers.tf      # Provider AWS + default_tags
│   ├── network.tf        # VPC, subnet, IGW, rotas, Security Group
│   ├── variables.tf      # Declaração de variáveis
│   └── terraform.tfvars  # Valores locais (não versionado)
├── docker/               # Fase 2+: compose e configs de monitoramento
├── runbooks/             # Fase 4: documentação de incidentes
└── scripts/              # Fase 5: automações em bash
```

## 🚀 Como reproduzir

```bash
# Pré-requisitos: Terraform >= 1.5, AWS CLI configurado com usuário IAM

git clone https://github.com/Rafaelmcf/cloud-observability-lab.git
cd cloud-observability-lab/terraform

# Crie o terraform.tfvars com seu IP público:
echo 'my_ip = "SEU_IP/32"' > terraform.tfvars

terraform init
terraform plan
terraform apply
```

> 💸 **FinOps:** ao encerrar uma sessão de estudos, `terraform destroy` remove toda a infraestrutura. Reconstruir leva 2 minutos — essa é a vantagem do IaC.

---

*Projeto autoral em desenvolvimento, parte da minha transição de carreira para Cloud/DevOps. Fases 2 a 5 em andamento — acompanhe pelos commits.* 🚧
