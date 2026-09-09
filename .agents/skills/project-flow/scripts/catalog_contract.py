"""Local product catalog contract and deterministic approval projection."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime


SCOPE_FIELDS = {"title_convention", "input_inventory", "behaviors", "dependency_reasons", "order_reasons"}
ITEM_FIELDS = {"delivery"}


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be non-empty text")
    return value


def shape(value, keys, label):
    if not isinstance(value, dict) or value.keys() != set(keys):
        raise ValueError(f"{label} has missing or unknown fields")


def strings(value, label, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError(f"{label} must be an array")
    for entry in value:
        text(entry, label)
    if len(value) != len(set(value)):
        raise ValueError(f"{label} contains duplicates")
    return value


def decision(value, label):
    shape(value, {"statement", "confirmed_by", "confirmed_at"}, label)
    for key in value:
        text(value[key], f"{label}.{key}")
    if datetime.fromisoformat(value["confirmed_at"].replace("Z", "+00:00")).tzinfo is None:
        raise ValueError(f"{label} requires a timezone")


def convention(value, ready=True):
    if value is None and not ready:
        return
    shape(value, {"surfaces", "audiences", "audience_mode", "shared_public_rule", "confirmation"}, "title_convention")
    surfaces = strings(value["surfaces"], "surfaces", True)
    if not set(surfaces) <= {"WEB", "APP"}:
        raise ValueError("invalid surface prefix")
    strings(value["audiences"], "audiences")
    for audience in value["audiences"]:
        if not re.fullmatch(r"[A-Z][A-Z0-9_-]*", audience):
            raise ValueError("invalid audience prefix")
    if value["audience_mode"] not in {"single", "aggregate", "multiple"}:
        raise ValueError("invalid audience_mode")
    text(value["shared_public_rule"], "shared_public_rule")
    decision(value["confirmation"], "title convention confirmation")


def delivery(value, naming, ready=True):
    if value is None and not ready:
        return
    convention(naming)
    shape(value, {"surface", "audiences", "name", "title", "visible_delivery", "user_result", "included", "boundary_reason"}, "delivery")
    if value["surface"] not in naming["surfaces"]:
        raise ValueError("invalid delivery surface prefix")
    audiences = strings(value["audiences"], "delivery audiences")
    if not set(audiences) <= set(naming["audiences"]):
        raise ValueError("unconfirmed audience prefix")
    if value["surface"] == "WEB" and not audiences:
        raise ValueError("WEB requires an audience")
    if value["surface"] == "APP" and "BACKOFFICE" in audiences:
        raise ValueError("APP cannot use BACKOFFICE")
    if naming["audience_mode"] != "multiple" and len(audiences) > 1:
        raise ValueError("multiple audiences require the multiple convention")
    for field in ("name", "title", "visible_delivery", "user_result", "boundary_reason"):
        text(value[field], f"delivery.{field}")
    if "[" in value["name"] or "]" in value["name"]:
        raise ValueError("delivery name must not contain prefixes")
    strings(value["included"], "delivery.included", True)
    expected = " ".join(f"[{prefix}]" for prefix in [value["surface"], *audiences]) + " " + value["name"]
    if value["title"] != expected:
        raise ValueError("delivery title disagrees with confirmed prefixes and name")


def projection(state):
    """Exclude processing status so interview progress does not revoke the catalog."""
    by_id = {item["id"]: item for item in state["catalog"]}
    result = {
        "projection_version": 1,
        **{field: state[field] for field in sorted(SCOPE_FIELDS)},
        "catalog": [{key: value for key, value in by_id[item_id].items() if key != "status"} for item_id in state["suggested_order"]],
        "retired": [{key: value for key, value in item.items() if key != "status"} for item in state["catalog"] if item["lifecycle"] == "retired"],
        **{field: state[field] for field in ("sources", "source_allocation", "candidates", "dependency_graph", "parallel_ready_groups", "suggested_order")},
    }
    if "legacy_review" in state:
        review = state["legacy_review"]
        previous = json.dumps(review["previous_state"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        result["legacy_review"] = {"reason": review["reason"], "previous_state_sha256": hashlib.sha256(previous.encode("utf-8")).hexdigest()}
    retired_relations = [relation for relation in state.get("relations", []) if relation["status"] == "retired"]
    if retired_relations:
        result["retired_relations"] = retired_relations
    return result


def literal(value):
    # Keep evidence and titles literal: embedded Markdown cannot hide a catalog row.
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True) if not isinstance(value, str) else value
    return "".join("\\" + char if char in "\\`*_{}[]<>()#+-.!|" else ("<br>" if char == "\n" else char) for char in raw.replace("\r", ""))


LABELS = {
    "surfaces": "Superfícies", "audiences": "Públicos", "audience_mode": "Convenção de públicos",
    "shared_public_rule": "Telas compartilhadas e públicas", "confirmation": "Confirmação",
    "statement": "Decisão", "confirmed_by": "Confirmado por", "confirmed_at": "Confirmado em",
    "description": "Comportamento", "evidence": "Evidências", "evidence_kind": "Tipo de evidência",
    "disposition": "Destino", "owner": "Item responsável", "consumers": "Itens consumidores",
    "repository": "Confronto com o repositório", "proposed_change": "Mudança proposta",
    "decision": "Decisão", "source_id": "Fonte", "locator": "Localizador", "status": "Estado",
    "selection": "Tipo de seleção", "requested": "Material solicitado", "entries": "Inventário",
    "references": "Referências entre fontes", "from_source": "Fonte de origem", "target": "Destino da referência",
    "role": "Papel da fonte", "origin": "Origem", "item": "Item", "blocked_by": "Bloqueado por",
    "provided_capability": "Capacidade fornecida", "blocking_reason": "Por que impede a entrega",
    "basis": "Critério de ordem", "rationale": "Justificativa", "source_allocation": "Alocação de fontes",
    "item_ids": "Itens", "catalog_item_ids": "Itens", "ownership": "Local de armazenamento", "path": "Caminho",
    "human_objective": "Objetivo humano", "actors": "Atores", "observable_result_or_deviation": "Resultado ou desvio",
    "separation_reason": "Justificativa do limite", "candidate_ids": "Candidatos", "lifecycle": "Ciclo de vida",
    "suggested_position": "Posição", "id": "ID", "name": "Nome", "type": "Tipo", "delivery": "Entrega",
}


def details(value, indent=0):
    """Render structured evidence legibly without letting source markup hide content."""
    prefix = "  " * indent + "- "
    if isinstance(value, dict):
        lines = []
        for key in sorted(value):
            entry = value[key]
            label = LABELS.get(key, key)
            if isinstance(entry, (dict, list)) and entry:
                lines += [prefix + label + ":", *details(entry, indent + 1)]
            else:
                lines += [prefix + label + ": " + (literal(entry) if entry is not None and entry != [] else "Nenhum.")]
        return lines
    if isinstance(value, list):
        if not value:
            return [prefix + "Nenhum."]
        if all(not isinstance(entry, (dict, list)) for entry in value):
            return [prefix + ", ".join(literal(entry) for entry in value)]
        lines = []
        for index, entry in enumerate(value, 1):
            lines += [prefix + f"Registro {index}:", *details(entry, indent + 1)]
        return lines
    return [prefix + literal(value)]


def render(state):
    data = projection(state)
    lines = ["<!-- project-flow:catalog:start -->", "## Convenção de títulos", "", *details(data["title_convention"]), "", "## Catálogo", ""]
    for position, item in enumerate(data["catalog"], 1):
        value = item["delivery"]
        lines += [f"### {position}. {literal(item['id'])} — {literal(item['type'])}: {literal(value['title'])}", ""]
        for label, content in (("Público", value["audiences"]), ("Entrega visível", value["visible_delivery"]), ("Resultado para o usuário", value["user_result"]), ("Incluído", value["included"]), ("Limite", value["boundary_reason"]), ("Dependências", item["dependencies"]), ("Justificativas dos bloqueios", [edge for edge in data["dependency_reasons"] if edge["item"] == item["id"]]), ("Motivo da posição", next(reason for reason in data["order_reasons"] if reason["item"] == item["id"]))):
            if isinstance(content, list):
                lines += [f"- {label}:", *details(content, 1)]
            elif isinstance(content, dict):
                lines += [f"- {label}:", *details(content, 1)]
            else:
                lines += [f"- {label}: {literal(content)}"]
        metadata = {key: value for key, value in item.items() if key not in {"id", "type", "name", "delivery", "dependencies"}}
        lines += ["", *details(metadata), ""]
    for label, field in (("Cobertura comportamental", "behaviors"), ("Inventário e referências", "input_inventory"), ("Fontes", "sources"), ("Alocação física das fontes", "source_allocation"), ("Candidatos", "candidates"), ("Itens retirados", "retired"), ("Grafo de bloqueios", "dependency_graph"), ("Justificativas de dependências", "dependency_reasons"), ("Ordem aprovada", "suggested_order"), ("Justificativas da ordem", "order_reasons"), ("Grupos sem bloqueios entre si no grafo", "parallel_ready_groups")):
        lines += [f"## {label}", ""]
        lines += details(data[field])
        lines += [""]
    for label, field in (("Estado legado preservado", "legacy_review"), ("Relações planejadas retiradas", "retired_relations")):
        if field in data:
            lines += [f"## {label}", "", *details(data[field]), ""]
    return "\n".join([*lines, "<!-- project-flow:catalog:end -->", ""])


def digest(state):
    return hashlib.sha256(render(state).encode("utf-8")).hexdigest()


def validate_scope(state):
    ready = "catalog-proposed" in state["completed_phases"]
    for field in SCOPE_FIELDS:
        if field not in state:
            raise ValueError(f"scope v3 missing {field}")
    for field in ("behaviors", "dependency_reasons", "order_reasons"):
        if not isinstance(state[field], list):
            raise ValueError(f"{field} must be an array")
    convention(state["title_convention"], ready)
    if not ready:
        if any(a["status"] == "valid" for a in state["approvals"]):
            raise ValueError("approval requires a proposed catalog")
        return
    items = {item["id"]: item for item in state["catalog"] if item["lifecycle"] == "active"}
    for item in state["catalog"]:
        delivery(item["delivery"], state["title_convention"])
        if item["name"] != item["delivery"]["name"]:
            raise ValueError("catalog name disagrees with delivery")
    for allocation in state["source_allocation"]:
        consumers = {item["id"] for item in state["catalog"] if allocation["source_id"] in item["evidence"]}
        if set(allocation["item_ids"]) != consumers:
            raise ValueError("source allocation must match every item's evidence references")
    for candidate in state["candidates"]:
        owners = {item["id"] for item in state["catalog"] if candidate["id"] in item["candidate_ids"]}
        if set(candidate["catalog_item_ids"]) != owners:
            raise ValueError("candidate mapping must agree in both directions")
    valid_approvals = [a for a in state["approvals"] if a["kind"] == "complete-catalog-and-order" and a["status"] == "valid"]
    if len(valid_approvals) > 1:
        raise ValueError("only one complete catalog approval may be valid")
    approved = bool(valid_approvals)
    inventory = state["input_inventory"]
    shape(inventory, {"selection", "requested", "entries", "references"}, "input_inventory")
    if inventory["selection"] not in {"complete-package", "selected-files"}:
        raise ValueError("input inventory selection is invalid")
    strings(inventory["requested"], "requested inputs", True)
    if not isinstance(inventory["entries"], list) or not isinstance(inventory["references"], list):
        raise ValueError("inventory entries and references must be arrays")
    sources = {entry["source_id"] for entry in state["source_allocation"]}
    entry_ids = set()
    for entry in inventory["entries"]:
        shape(entry, {"source_id", "origin", "role", "decision"}, "inventory entry")
        if entry["source_id"] in entry_ids or entry["source_id"] not in sources:
            raise ValueError("inventory has duplicate or unknown source")
        entry_ids.add(entry["source_id"])
        text(entry["origin"], "inventory origin")
        if entry["role"] not in {"behavioral", "contextual", "excluded", "pending"}:
            raise ValueError("invalid inventory role")
        if entry["role"] == "excluded":
            decision(entry["decision"], "source exclusion")
        if approved and entry["role"] == "pending":
            raise ValueError("unresolved source blocks approval")
    if entry_ids != sources:
        raise ValueError("inventory must reconcile every source")
    reference_ids = set()
    for reference in inventory["references"]:
        shape(reference, {"id", "from_source", "target", "status", "source_id", "decision"}, "reference")
        text(reference["id"], "reference id")
        text(reference["target"], "reference target")
        if reference["id"] in reference_ids or reference["from_source"] not in sources:
            raise ValueError("duplicate or unknown reference")
        reference_ids.add(reference["id"])
        if reference["status"] not in {"included", "excluded", "pending"}:
            raise ValueError("invalid reference disposition")
        if reference["status"] == "included" and reference["source_id"] not in sources:
            raise ValueError("included reference needs an inventoried source")
        if reference["status"] == "excluded" or (inventory["selection"] == "selected-files" and reference["status"] == "included"):
            decision(reference["decision"], "external reference decision")
        if approved and reference["status"] == "pending":
            raise ValueError("unresolved reference blocks approval")
    behavior_ids, witnessed = set(), set()
    for behavior in state["behaviors"]:
        shape(behavior, {"id", "description", "evidence", "evidence_kind", "audiences", "disposition", "owner", "consumers", "repository", "decision"}, "behavior")
        behavior_id = text(behavior["id"], "behavior id")
        if behavior_id in behavior_ids:
            raise ValueError("duplicate behavior responsibility")
        behavior_ids.add(behavior_id)
        text(behavior["description"], "behavior description")
        strings(behavior["audiences"], "behavior audiences")
        if not set(behavior["audiences"]) <= set(state["title_convention"]["audiences"]):
            raise ValueError("behavior uses an unconfirmed audience")
        if behavior["evidence_kind"] not in {"demonstrated", "annotation", "ambiguity"}:
            raise ValueError("invalid behavior evidence kind")
        if not isinstance(behavior["evidence"], list) or not behavior["evidence"]:
            raise ValueError("behavior requires evidence")
        for evidence in behavior["evidence"]:
            shape(evidence, {"source_id", "locator"}, "behavior evidence")
            if evidence["source_id"] not in sources:
                raise ValueError("unknown behavior evidence source")
            text(evidence["locator"], "evidence locator")
            witnessed.add(evidence["source_id"])
        disposition = behavior["disposition"]
        if disposition not in {"covered", "existing-confirmed", "excluded", "pending"}:
            raise ValueError("invalid behavior disposition")
        strings(behavior["consumers"], "behavior consumers")
        if not set(behavior["consumers"]) <= items.keys() or behavior["owner"] in behavior["consumers"]:
            raise ValueError("invalid behavior consumers")
        if disposition == "covered":
            if not isinstance(behavior["owner"], str) or behavior["owner"] not in items:
                raise ValueError("covered behavior needs exactly one active owner")
            if any(e["source_id"] not in items[behavior["owner"]]["evidence"] for e in behavior["evidence"]):
                raise ValueError("behavior owner must reference its evidence")
        elif behavior["owner"] is not None:
            raise ValueError("only covered behavior has an owner")
        repository = behavior["repository"]
        shape(repository, {"status", "evidence", "proposed_change"}, "behavior repository")
        if repository["status"] not in {"absent", "partial", "existing", "unknown"}:
            raise ValueError("invalid repository comparison")
        strings(repository["evidence"], "repository evidence", repository["status"] != "unknown")
        text(repository["proposed_change"], "proposed change")
        if disposition in {"existing-confirmed", "excluded"}:
            decision(behavior["decision"], "behavior disposition decision")
        if disposition == "existing-confirmed" and repository["status"] != "existing":
            raise ValueError("partial implementation is not confirmed existing coverage")
        if approved and (disposition == "pending" or repository["status"] == "unknown"):
            raise ValueError("unresolved behavior blocks approval")
    behavioral_sources = {entry["source_id"] for entry in inventory["entries"] if entry["role"] == "behavioral"}
    if not behavioral_sources <= witnessed:
        raise ValueError("missing behavioral coverage")
    if set(items) - {b["owner"] for b in state["behaviors"] if b["disposition"] == "covered"}:
        raise ValueError("every active item must own a behavior")
    pairs = set()
    for edge in state["dependency_reasons"]:
        shape(edge, {"item", "blocked_by", "provided_capability", "blocking_reason", "evidence"}, "dependency reason")
        pair = (edge["item"], edge["blocked_by"])
        if pair in pairs:
            raise ValueError("duplicate dependency reason")
        pairs.add(pair)
        text(edge["provided_capability"], "provided capability")
        text(edge["blocking_reason"], "delivery blocking reason")
        strings(edge["evidence"], "dependency evidence or decision", True)
    if pairs != {(e["item"], e["blocked_by"]) for e in state["dependency_graph"]}:
        raise ValueError("dependency reasons must exactly match graph")
    if [reason["item"] for reason in state["order_reasons"]] != state["suggested_order"]:
        raise ValueError("order reasons must follow the complete order")
    for reason in state["order_reasons"]:
        shape(reason, {"item", "basis", "rationale", "evidence"}, "order reason")
        if reason["basis"] not in {"dependency", "confirmed-priority", "usage-lifecycle", "stable-id"}:
            raise ValueError("invalid order basis")
        text(reason["rationale"], "order rationale")
        strings(reason["evidence"], "order evidence or decision", True)
    for approval in state["approvals"]:
        if approval["kind"] == "complete-catalog-and-order" and approval["status"] == "valid" and approval["subject_sha256"] != digest(state):
            raise ValueError("catalog approval hash does not match complete projection")
