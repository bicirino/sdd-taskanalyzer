"""Módulo de Análise de Tarefas e Produtividade (TaskAnalyzer).

Implementação baseada em especificações (SDD) com desenvolvimento assistido por IA.
"""

from datetime import datetime
from typing import Any


class TaskValidationError(Exception):
    """Exceção customizada disparada para erros de validação ou inconsistência de dados."""

    pass


def _parse_iso_date(date_str: str | None) -> datetime | None:
    """Converte uma string no formato ISO 8601 em um objeto datetime.

    Suporta os formatos 'YYYY-MM-DD' e 'YYYY-MM-DDTHH:MM:SS'.
    """
    if date_str is None:
        return None

    if not isinstance(date_str, str) or not date_str.strip():
        raise TaskValidationError("A data deve ser uma string não vazia no formato ISO 8601.")

    clean_date = date_str.strip()
    try:
        # Suporta data simples (YYYY-MM-DD) ou com hora (YYYY-MM-DDTHH:MM:SS)
        if "T" in clean_date:
            return datetime.fromisoformat(clean_date)
        return datetime.strptime(clean_date, "%Y-%m-%d")
    except ValueError as exc:
        raise TaskValidationError(f"Data inválida ou fora do formato ISO 8601: '{date_str}'") from exc


def _validate_and_parse_task(task: dict[str, Any]) -> dict[str, Any]:
    """Valida individualmente os campos de uma tarefa e analisa suas datas."""
    if not isinstance(task, dict):
        raise TaskValidationError("Cada tarefa deve ser um dicionário.")

    # Validação de campos obrigatórios
    required_fields = ["id", "titulo", "prioridade", "status", "data_criacao", "data_prazo"]
    for field in required_fields:
        if field not in task:
            raise TaskValidationError(f"Campo obrigatório ausente na tarefa: '{field}'")

    # Validação de id e titulo
    if not isinstance(task["id"], int) or task["id"] <= 0:
        raise TaskValidationError("O campo 'id' deve ser um inteiro maior que zero.")

    if not isinstance(task["titulo"], str) or not task["titulo"].strip():
        raise TaskValidationError("O campo 'titulo' deve ser uma string não vazia.")

    # Validação dos domínios de prioridade e status
    valid_priorities = {"alta", "media", "baixa"}
    valid_statuses = {"concluida", "pendente", "em_andamento"}

    prioridade = str(task["prioridade"]).lower().strip()
    status = str(task["status"]).lower().strip()

    if prioridade not in valid_priorities:
        raise TaskValidationError(f"Prioridade inválida '{task['prioridade']}'. Valores aceitos: {valid_priorities}")

    if status not in valid_statuses:
        raise TaskValidationError(f"Status inválido '{task['status']}'. Valores aceitos: {valid_statuses}")

    # Processamento e parsing de datas
    dt_criacao = _parse_iso_date(task["data_criacao"])
    dt_prazo = _parse_iso_date(task["data_prazo"])
    dt_conclusao = _parse_iso_date(task.get("data_conclusao"))

    # Regras de consistência de datas
    if dt_prazo < dt_criacao:
        raise TaskValidationError("A 'data_prazo' não pode ser anterior à 'data_criacao'.")

    if status == "concluida":
        if dt_conclusao is None:
            raise TaskValidationError("Tarefas com status 'concluida' devem possuir 'data_conclusao'.")
        if dt_conclusao < dt_criacao:
            raise TaskValidationError("A 'data_conclusao' não pode ser anterior à 'data_criacao'.")
    else:
        # Para status diferente de concluída, data_conclusao é ignorada/deve ser None
        dt_conclusao = None

    # Cálculo do atraso (apenas se concluída)
    is_atrasada = False
    dias_conclusao = 0.0

    if status == "concluida" and dt_conclusao is not None:
        if dt_conclusao > dt_prazo:
            is_atrasada = True

        # Diferença em dias flutuantes
        delta = dt_conclusao - dt_criacao
        dias_conclusao = delta.total_seconds() / 86400.0

    return {
        "id": task["id"],
        "prioridade": prioridade,
        "status": status,
        "is_concluida": status == "concluida",
        "is_atrasada": is_atrasada,
        "dias_conclusao": dias_conclusao,
    }


def analyze_tasks(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Analisador de tarefas e gerador de métricas de produtividade.

    Args:
        tasks: Lista de dicionários contendo os dados das tarefas.

    Returns:
        Dicionário estruturado com os totais gerais e indicadores por prioridade.

    Raises:
        TaskValidationError: Se alguma entrada for inválida ou inconsistente.
    """
    if not isinstance(tasks, list):
        raise TaskValidationError("A entrada 'tasks' deve ser uma lista de tarefas.")

    # Estrutura base de resposta
    result: dict[str, Any] = {
        "totais_gerais": {
            "total_tarefas": len(tasks),
            "total_concluidas": 0,
            "total_pendentes": 0,
            "total_em_andamento": 0,
            "total_atrasadas": 0,
            "tempo_medio_conclusao_dias": 0.0,
            "taxa_atraso_percentual": 0.0,
        },
        "indicadores_por_prioridade": {
            "alta": {
                "total": 0,
                "concluidas": 0,
                "atrasadas": 0,
                "tempo_medio_conclusao_dias": 0.0,
                "taxa_atraso_percentual": 0.0,
            },
            "media": {
                "total": 0,
                "concluidas": 0,
                "atrasadas": 0,
                "tempo_medio_conclusao_dias": 0.0,
                "taxa_atraso_percentual": 0.0,
            },
            "baixa": {
                "total": 0,
                "concluidas": 0,
                "atrasadas": 0,
                "tempo_medio_conclusao_dias": 0.0,
                "taxa_atraso_percentual": 0.0,
            },
        },
    }

    if not tasks:
        return result

    # Acumuladores globais e por prioridade
    soma_dias_geral = 0.0
    p_data: dict[str, dict[str, Any]] = {
        "alta": {"total": 0, "concluidas": 0, "atrasadas": 0, "soma_dias": 0.0},
        "media": {"total": 0, "concluidas": 0, "atrasadas": 0, "soma_dias": 0.0},
        "baixa": {"total": 0, "concluidas": 0, "atrasadas": 0, "soma_dias": 0.0},
    }

    # Processamento sem mutar a lista de entrada
    for task_raw in tasks:
        parsed = _validate_and_parse_task(task_raw)
        p = parsed["prioridade"]
        st = parsed["status"]

        # Totais gerais de status
        if st == "pendente":
            result["totais_gerais"]["total_pendentes"] += 1
        elif st == "em_andamento":
            result["totais_gerais"]["total_em_andamento"] += 1

        # Estatísticas por prioridade
        p_data[p]["total"] += 1

        if parsed["is_concluida"]:
            result["totais_gerais"]["total_concluidas"] += 1
            p_data[p]["concluidas"] += 1
            soma_dias_geral += parsed["dias_conclusao"]
            p_data[p]["soma_dias"] += parsed["dias_conclusao"]

            if parsed["is_atrasada"]:
                result["totais_gerais"]["total_atrasadas"] += 1
                p_data[p]["atrasadas"] += 1

    # Cálculo das médias e percentuais gerais (Proteção contra ZeroDivisionError)
    total_conc = result["totais_gerais"]["total_concluidas"]
    if total_conc > 0:
        result["totais_gerais"]["tempo_medio_conclusao_dias"] = round(soma_dias_geral / total_conc, 2)
        result["totais_gerais"]["taxa_atraso_percentual"] = round(
            (result["totais_gerais"]["total_atrasadas"] / total_conc) * 100.0, 2
        )

    # Consolidação dos indicadores por prioridade
    for prio, data in p_data.items():
        res_prio = result["indicadores_por_prioridade"][prio]
        res_prio["total"] = data["total"]
        res_prio["concluidas"] = data["concluidas"]
        res_prio["atrasadas"] = data["atrasadas"]

        p_conc = data["concluidas"]
        if p_conc > 0:
            res_prio["tempo_medio_conclusao_dias"] = round(data["soma_dias"] / p_conc, 2)
            res_prio["taxa_atraso_percentual"] = round((data["atrasadas"] / p_conc) * 100.0, 2)

    return result
