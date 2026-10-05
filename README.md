# TaskAnalyzer (`sdd-taskanalyzer`)

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Test Status](https://img.shields.io/badge/pytest-passing-brightgreen)](https://docs.pytest.org/)

Módulo de análise de produtividade e tarefas construído com desenvolvimento assistido por Inteligência Artificial (AI Harness), orientado a especificações (SDD - Spec-Driven Development) e governança rigorosa de contexto.

---

## 🎯 Propósito do Projeto
O **TaskAnalyzer** é um componente Python projetado para processar conjuntos de dados de tarefas e calcular indicadores quantitativos essenciais:
- Tempo médio de conclusão de tarefas em dias.
- Taxa de atraso percentual (geral e por prioridade).
- Contagem consolidada de status (concluída, pendente, em andamento e atrasada).

---

## 🛠️ Estrutura do Repositório
```text
sdd-taskanalyzer/
├── README.md               # Documentação principal e guia de execução
├── CONTEXT_RULES.md        # Diretrizes rígidas e regras de governança para IA
├── .gitignore             # Arquivos e diretórios ignorados pelo Git
├── requirements.txt        # Dependências autorizadas do projeto (pytest)
├── specs/
│   └── task_analyzer_spec.md  # Especificação técnica do contrato (SDD)
├── tests/
│   └── test_harness.py     # Suíte de testes automatizados com pytest
└── src/
    └── task_analyzer.py    # Código funcional gerado via IA e homologado por humano
``` 
--- 

## 🚦 Regras de Governança e Arquitetura 

- **Linguagem**: Python 3.11+ utilizando apenas bibliotecas padrão (datetime, typing, math).
- **Sem Dependências de Processamento**: Proibido o uso de pandas, numpy ou frameworks pesados.
- **Tipagem Estrita**: Type hints em 100% das funções e parâmetros.
- **Tratamento de Exceções**: Disparo obrigatório de TaskValidationError para dados ou datas inválidas.

## 🚀 Como Configurar e Executar

### 1.) Clonar o repositório 

``` bash 

git clone [https://github.com/SEU_USUARIO/sdd-taskanalyzer.git](https://github.com/SEU_USUARIO/sdd-taskanalyzer.git)
cd sdd-taskanalyzer

``` 


### 2.) Criar e ativar o Ambiente Virtual (venv) 

``` bash 
python -m venv venv 

#Linux / macOs
source venv/bin/activate 

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

``` 

### 3.) Instalar Dependências 

``` bash 

pip install -r requirements.txt 

``` 

### 4.) Executar a Suíte de Testes (Test Harness)

``` bash 

pytest tests/ -v 

``` 

## 📝 Homologação e Licença 
Projeto desenvolvido no âmbito da disciplina de Bootcamp III, focado em metodologias modernas de desenvolvimento assistido por IA e especificação executável (SDD).