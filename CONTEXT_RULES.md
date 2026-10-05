# CONTEXT_RULES.md - Governança de Contexto e Regras para IA

## 1. Diretrizes Arquiteturais (Obrigatórias)
- **Linguagem e Runtime:** Python 3.11+ utilizando exclusivamente bibliotecas padrão (`datetime`, `typing`, `math`) para a lógica de negócio.
- **Tipagem Estrita:** Uso obrigatório de *type hints* em 100% das funções, métodos e estruturas (`list[dict[str, Any]]`, `dict[str, Any]`, `str | None`).
- **Tratamento de Exceções Customizadas:** Toda falha de validação de dados de entrada ou incoerência de datas deve disparar obrigatoriamente a exceção `TaskValidationError`.
- **Imutabilidade das Entradas:** O módulo de análise não deve alterar, reordenar ou mutar a lista de tarefas recebida como entrada.

## 2. Proibições Explícitas (Regras Restritivas)
- **Sem Dependências Externas Desnecessárias:** É proibido o uso de bibliotecas como `pandas`, `numpy` ou frameworks pesados para o cálculo dos indicadores.
- **Sem Suposições ou "Adivinhações":** A IA não deve inferir regras de negócio ausentes no SDD. Diante de qualquer ambiguidade, deve interromper e solicitar esclarecimento ao humano responsável.
- **Proibido Alterar a Assinatura da Interface:** O formato do dicionário de saída (chaves, tipos e aninhamento) e o nome dos métodos/funções (`analyze_tasks`) não podem ser modificados sob nenhuma hipótese.
- **Proibido Silenciar Erros:** É proibido o uso de blocos `try-except` genéricos (`except Exception: pass`) que ocultem falhas de validação ou cálculo.

## 3. Regras de Interação e Validação do Assistente de IA
- **Validação Via Test Harness:** O assistente de IA só pode considerar o código de um módulo como "concluído" após a execução e aprovação integral (100% *pass*) da suíte de testes do `pytest`.
- **Desenvolvimento Incremental:** A IA deve implementar e submeter o código em etapas lógicas, aguardando validação a cada fase.
- **Feedback Transparente de Falhas:** Caso um teste falhe, a IA deve analisar a causa raiz no `pytest`, corrigir o código mantendo o contrato estrito, e reexecutar a suíte antes de apresentar a solução final.