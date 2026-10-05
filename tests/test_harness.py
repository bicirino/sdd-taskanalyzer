"""Suíte de testes (Test Harness) do TaskAnalyzer conforme SDD."""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from task_analyzer import TaskValidationError, analyze_tasks  # noqa: E402

PRIORIDADES = ("alta", "media", "baixa")

TOTAIS_GERAIS_KEYS = (
    "total_tarefas",
    "total_concluidas",
    "total_pendentes",
    "total_em_andamento",
    "total_atrasadas",
    "tempo_medio_conclusao_dias",
    "taxa_atraso_percentual",
)

INDICADOR_PRIORIDADE_KEYS = (
    "total",
    "concluidas",
    "atrasadas",
    "tempo_medio_conclusao_dias",
    "taxa_atraso_percentual",
)


def _make_task(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": 1,
        "titulo": "Tarefa de exemplo",
        "prioridade": "media",
        "status": "pendente",
        "data_criacao": "2024-01-01",
        "data_prazo": "2024-01-10",
        "data_conclusao": None,
    }
    base.update(overrides)
    return base


def _assert_contract_shape(result: dict[str, Any]) -> None:
    assert set(result.keys()) == {"totais_gerais", "indicadores_por_prioridade"}
    assert set(result["totais_gerais"].keys()) == set(TOTAIS_GERAIS_KEYS)
    assert set(result["indicadores_por_prioridade"].keys()) == set(PRIORIDADES)
    for prio in PRIORIDADES:
        assert set(result["indicadores_por_prioridade"][prio].keys()) == set(INDICADOR_PRIORIDADE_KEYS)


def test_lista_vazia_retorna_estrutura_zerada() -> None:
    result = analyze_tasks([])

    _assert_contract_shape(result)
    assert result["totais_gerais"]["total_tarefas"] == 0
    assert result["totais_gerais"]["total_concluidas"] == 0
    assert result["totais_gerais"]["tempo_medio_conclusao_dias"] == 0.0
    assert result["totais_gerais"]["taxa_atraso_percentual"] == 0.0


def test_metricas_gerais_e_por_prioridade() -> None:
    tasks = [
        _make_task(
            id=1,
            titulo="Concluída no prazo",
            prioridade="alta",
            status="concluida",
            data_criacao="2024-01-01",
            data_prazo="2024-01-10",
            data_conclusao="2024-01-05",
        ),
        _make_task(
            id=2,
            titulo="Concluída atrasada",
            prioridade="media",
            status="concluida",
            data_criacao="2024-01-01",
            data_prazo="2024-01-03",
            data_conclusao="2024-01-05",
        ),
        _make_task(id=3, titulo="Pendente", prioridade="baixa", status="pendente"),
        _make_task(id=4, titulo="Em andamento", prioridade="alta", status="em_andamento"),
    ]

    result = analyze_tasks(tasks)

    _assert_contract_shape(result)
    totais = result["totais_gerais"]
    assert totais["total_tarefas"] == 4
    assert totais["total_concluidas"] == 2
    assert totais["total_pendentes"] == 1
    assert totais["total_em_andamento"] == 1
    assert totais["total_atrasadas"] == 1
    assert totais["tempo_medio_conclusao_dias"] == 4.0
    assert totais["taxa_atraso_percentual"] == 50.0

    alta = result["indicadores_por_prioridade"]["alta"]
    assert alta == {
        "total": 2,
        "concluidas": 1,
        "atrasadas": 0,
        "tempo_medio_conclusao_dias": 4.0,
        "taxa_atraso_percentual": 0.0,
    }

    media = result["indicadores_por_prioridade"]["media"]
    assert media == {
        "total": 1,
        "concluidas": 1,
        "atrasadas": 1,
        "tempo_medio_conclusao_dias": 4.0,
        "taxa_atraso_percentual": 100.0,
    }

    baixa = result["indicadores_por_prioridade"]["baixa"]
    assert baixa["total"] == 1
    assert baixa["concluidas"] == 0
    assert baixa["atrasadas"] == 0


def test_data_iso_com_hora() -> None:
    tasks = [
        _make_task(
            status="concluida",
            data_criacao="2024-01-01T08:00:00",
            data_prazo="2024-01-02T08:00:00",
            data_conclusao="2024-01-02T12:00:00",
        )
    ]

    result = analyze_tasks(tasks)

    assert result["totais_gerais"]["total_concluidas"] == 1
    assert result["totais_gerais"]["total_atrasadas"] == 1
    assert result["totais_gerais"]["tempo_medio_conclusao_dias"] == 1.17


def test_entrada_deve_ser_lista() -> None:
    with pytest.raises(TaskValidationError, match="lista de tarefas"):
        analyze_tasks({"id": 1})  # type: ignore[arg-type]


def test_campo_obrigatorio_ausente_dispara_erro() -> None:
    task = _make_task()
    del task["titulo"]
    with pytest.raises(TaskValidationError, match="Campo obrigatório ausente"):
        analyze_tasks([task])


@pytest.mark.parametrize(
    "task_patch, match",
    [
        ({"id": 0}, "id"),
        ({"id": -1}, "id"),
        ({"titulo": "   "}, "titulo"),
        ({"prioridade": "urgente"}, "Prioridade inválida"),
        ({"status": "cancelada"}, "Status inválido"),
        ({"data_criacao": "2024-01-10", "data_prazo": "2024-01-01"}, "data_prazo"),
        (
            {"status": "concluida", "data_conclusao": None},
            "data_conclusao",
        ),
        (
            {
                "status": "concluida",
                "data_criacao": "2024-01-10",
                "data_prazo": "2024-01-15",
                "data_conclusao": "2024-01-05",
            },
            "data_conclusao",
        ),
        ({"data_criacao": "data-invalida"}, "ISO 8601"),
    ],
)
def test_validacao_de_entrada(task_patch: dict[str, Any], match: str) -> None:
    task = _make_task(**task_patch)
    with pytest.raises(TaskValidationError, match=match):
        analyze_tasks([task])


def test_nao_muta_lista_de_entrada() -> None:
    tasks = [_make_task(id=1), _make_task(id=2, status="em_andamento")]
    snapshot = copy.deepcopy(tasks)

    analyze_tasks(tasks)

    assert tasks == snapshot
