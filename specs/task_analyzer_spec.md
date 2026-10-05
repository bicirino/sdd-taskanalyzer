# Especificação Técnica do Módulo TaskAnalyzer (SDD)

## Propósito do Módulo
O módulo **TaskAnalyzer** é um componente central focado em análise avançada de tarefas e métricas de produtividade. Seu objetivo é processar em memória um conjunto de dados estruturados de tarefas e gerar indicadores quantitativos precisos.

## Contrato Executável de Interface

### Entradas (Inputs)
A função `analyze_tasks(tasks: list[dict]) -> dict` recebe uma lista de objetos representando tarefas. Cada elemento deve seguir estritamente o esquema:

| Campo | Tipo | Obrigatório? | Valores Válidos / Regras de Formato |
| :--- | :--- | :--- | :--- |
| `id` | Inteiro (`int`) | Sim | Maior que zero (`id > 0`), único na lista. |
| `titulo` | Texto (`str`) | Sim | Não vazio, sem espaços apenas. |
| `prioridade` | Texto (`str`) | Sim | Apenas `'alta'`, `'media'` ou `'baixa'`. |
| `status` | Texto (`str`) | Sim | Apenas `'concluida'`, `'pendente'` ou `'em_andamento'`. |
| `data_criacao` | Texto (`str`) | Sim | Formato ISO 8601 (`YYYY-MM-DD` ou `YYYY-MM-DDTHH:MM:SS`). |
| `data_prazo` | Texto (`str`) | Sim | Formato ISO 8601. Deve ser igual ou posterior à `data_criacao`. |
| `data_conclusao`| Texto (`str` / `None`) | Condicional | Formato ISO 8601. Obrigatório se `status == 'concluida'`. Nulo (`None`) se `pendente` ou `em_andamento`. |

### Saídas (Outputs)
O retorno deve ser um dicionário estruturado com o seguinte modelo exato:

```python
{
    "totais_gerais": {
        "total_tarefas": 0,           # int: total de tarefas recebidas
        "total_concluidas": 0,        # int: quantidade com status 'concluida'
        "total_pendentes": 0,         # int: quantidade com status 'pendente'
        "total_em_andamento": 0,      # int: quantidade com status 'em_andamento'
        "total_atrasadas": 0,         # int: concluídas com data_conclusao > data_prazo
        "tempo_medio_conclusao_dias": 0.0, # float: média em dias das concluídas
        "taxa_atraso_percentual": 0.0      # float: (total_atrasadas / total_concluidas) * 100
    },
    "indicadores_por_prioridade": {
        "alta": {
            "total": 0,
            "concluidas": 0,
            "atrasadas": 0,
            "tempo_medio_conclusao_dias": 0.0,
            "taxa_atraso_percentual": 0.0
        },
        "media": {
            "total": 0,
            "concluidas": 0,
            "atrasadas": 0,
            "tempo_medio_conclusao_dias": 0.0,
            "taxa_atraso_percentual": 0.0
        },
        "baixa": {
            "total": 0,
            "concluidas": 0,
            "atrasadas": 0,
            "tempo_medio_conclusao_dias": 0.0,
            "taxa_atraso_percentual": 0.0
        }
    }
}