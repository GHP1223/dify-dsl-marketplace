#!/usr/bin/env python3
"""Dify DSL linter — validates YAML structure, node fields, selectors, and connectivity."""

from __future__ import annotations

import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

SPECIAL_SELECTOR_ROOTS = {"sys", "env", "conversation", "rag"}
UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)


def get_node_type(node: dict) -> str:
    if not isinstance(node, dict):
        return ""
    data = node.get("data") or {}
    return data.get("type") or node.get("type") or ""


def add_issue(issues: list[dict], severity: str, code: str, path: str, message: str) -> None:
    issues.append({"severity": severity, "code": code, "path": path, "message": message})


def validate_selector(issues: list[dict], selector: object, path: str, node_ids: set[str]) -> None:
    if not isinstance(selector, list) or len(selector) < 2:
        add_issue(issues, "error", "selector_shape_invalid", path, "selector must be an array of length >= 2")
        return
    root = selector[0]
    if not isinstance(root, str):
        add_issue(issues, "error", "selector_root_invalid", path, "selector first element must be a string")
        return
    if root in SPECIAL_SELECTOR_ROOTS or root in node_ids:
        return
    add_issue(issues, "error", "selector_target_missing", path, f"selector references unknown node or system root: {root}")


# ── Per-node validators ──────────────────────────────────────

def validate_end(issues: list[dict], node: dict, node_ids: set[str]) -> None:
    outputs = (node.get("data") or {}).get("outputs") or []
    for i, output in enumerate(outputs):
        selector = output.get("value_selector")
        if selector is not None:
            validate_selector(issues, selector, f"nodes[{node['id']}].data.outputs[{i}].value_selector", node_ids)


def validate_if_else(issues: list[dict], node: dict, outgoing_handles: dict[str, set[str]], node_ids: set[str]) -> None:
    data = node.get("data") or {}
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        add_issue(issues, "error", "if_else_cases_missing", f"nodes[{node['id']}].data.cases", "if-else missing cases")
        return
    allowed_handles = {"false"}
    for ci, case in enumerate(cases):
        case_id = case.get("case_id")
        if not case_id:
            add_issue(issues, "error", "if_else_case_id_missing", f"nodes[{node['id']}].data.cases[{ci}].case_id", "if-else case missing case_id")
            continue
        allowed_handles.add(str(case_id))
        for cj, cond in enumerate(case.get("conditions") or []):
            selector = cond.get("variable_selector")
            if selector is not None:
                validate_selector(issues, selector, f"nodes[{node['id']}].data.cases[{ci}].conditions[{cj}].variable_selector", node_ids)
    outgoing = outgoing_handles.get(str(node.get("id")), set())
    unexpected = sorted(h for h in outgoing if h and h not in allowed_handles)
    for h in unexpected:
        add_issue(issues, "error", "if_else_handle_unexpected", f"edges[source={node['id']}].sourceHandle", f"if-else has undeclared branch handle: {h}")
    if "false" not in outgoing:
        add_issue(issues, "error", "if_else_false_missing", f"edges[source={node['id']}]", "if-else missing false/default branch")


def validate_question_classifier(issues: list[dict], node: dict, outgoing_handles: dict[str, set[str]], node_ids: set[str]) -> None:
    data = node.get("data") or {}
    qs = data.get("query_variable_selector")
    if qs is None:
        add_issue(issues, "error", "question_classifier_query_missing", f"nodes[{node['id']}].data.query_variable_selector", "question-classifier missing query_variable_selector")
    else:
        validate_selector(issues, qs, f"nodes[{node['id']}].data.query_variable_selector", node_ids)
    classes = data.get("classes")
    if not isinstance(classes, list) or not classes:
        add_issue(issues, "error", "question_classifier_classes_missing", f"nodes[{node['id']}].data.classes", "question-classifier missing classes")
        return
    cids = []; cid_set = set()
    for i, c in enumerate(classes):
        cid = c.get("id")
        if not cid: add_issue(issues, "error", "question_classifier_class_id_missing", f"nodes[{node['id']}].data.classes[{i}].id", "class missing id"); continue
        cids.append(str(cid)); cid_set.add(str(cid))
        if not isinstance(c.get("name"), str) or not c["name"].strip():
            add_issue(issues, "error", "question_classifier_class_name_missing", f"nodes[{node['id']}].data.classes[{i}].name", "class missing name")
    for cid, n in Counter(cids).items():
        if n > 1: add_issue(issues, "error", "question_classifier_class_id_duplicate", f"nodes[{node['id']}].data.classes", f"duplicate class id: {cid}")
    outgoing = outgoing_handles.get(str(node.get("id")), set())
    unexpected = sorted(h for h in outgoing if h and h not in cid_set)
    for h in unexpected: add_issue(issues, "error", "question_classifier_handle_unexpected", f"edges[source={node['id']}].sourceHandle", f"undeclared handle: {h}")
    missing = sorted(c for c in cid_set if c not in outgoing)
    for h in missing: add_issue(issues, "error", "question_classifier_handle_missing", f"edges[source={node['id']}]", f"class {h} has no outgoing edge")


def validate_parameter_extractor(issues: list[dict], node: dict, node_ids: set[str]) -> None:
    data = node.get("data") or {}
    qs = data.get("query")
    if qs is None: add_issue(issues, "error", "parameter_extractor_query_missing", f"nodes[{node['id']}].data.query", "parameter-extractor missing query")
    else: validate_selector(issues, qs, f"nodes[{node['id']}].data.query", node_ids)
    if not data.get("reasoning_mode"): add_issue(issues, "error", "parameter_extractor_reasoning_mode_missing", f"nodes[{node['id']}].data.reasoning_mode", "parameter-extractor missing reasoning_mode")
    params = data.get("parameters")
    if not isinstance(params, list) or not params: add_issue(issues, "error", "parameter_extractor_parameters_missing", f"nodes[{node['id']}].data.parameters", "parameter-extractor missing parameters")


def validate_knowledge_retrieval(issues: list[dict], node: dict, node_ids: set[str]) -> None:
    data = node.get("data") or {}
    ds = data.get("dataset_ids")
    if not isinstance(ds, list) or not ds: add_issue(issues, "error", "knowledge_retrieval_dataset_ids_missing", f"nodes[{node['id']}].data.dataset_ids", "knowledge-retrieval dataset_ids must not be empty")
    qs = data.get("query_variable_selector")
    if qs is None: add_issue(issues, "error", "knowledge_retrieval_query_missing", f"nodes[{node['id']}].data.query_variable_selector", "knowledge-retrieval missing query_variable_selector")
    else: validate_selector(issues, qs, f"nodes[{node['id']}].data.query_variable_selector", node_ids)
    mode = data.get("retrieval_mode")
    if mode not in {"multiple", "single"}: add_issue(issues, "error", "knowledge_retrieval_mode_invalid", f"nodes[{node['id']}].data.retrieval_mode", "retrieval_mode must be single or multiple")
    if mode == "multiple":
        config = data.get("multiple_retrieval_config") or {}
        top_k = config.get("top_k")
        if not isinstance(top_k, int) or top_k < 1: add_issue(issues, "error", "knowledge_retrieval_topk_invalid", f"nodes[{node['id']}].data.multiple_retrieval_config.top_k", "top_k must be >= 1")
    if mode == "single":
        sm = (data.get("single_retrieval_config") or {}).get("model")
        if not isinstance(sm, dict): add_issue(issues, "error", "knowledge_retrieval_single_model_missing", f"nodes[{node['id']}].data.single_retrieval_config.model", "single mode requires model")


def validate_list_operator(issues: list[dict], node: dict, node_ids: set[str]) -> None:
    data = node.get("data") or {}
    var = data.get("variable")
    if var is None: add_issue(issues, "error", "list_operator_variable_missing", f"nodes[{node['id']}].data.variable", "list-operator missing variable")
    else: validate_selector(issues, var, f"nodes[{node['id']}].data.variable", node_ids)
    for key in ("filter_by", "order_by", "limit"):
        if key not in data: add_issue(issues, "error", f"list_operator_{key}_missing", f"nodes[{node['id']}].data.{key}", f"list-operator missing {key}")
    limit = data.get("limit") or {}
    if isinstance(limit, dict) and limit.get("enabled"):
        size = limit.get("size")
        if not isinstance(size, int) or size < 1: add_issue(issues, "error", "list_operator_limit_invalid", f"nodes[{node['id']}].data.limit.size", "limit.size must be >= 1 when enabled")


def validate_iteration(issues: list[dict], node: dict, node_types: dict[str, str], node_ids: set[str]) -> None:
    data = node.get("data") or {}
    for field in ("iterator_selector", "output_selector", "start_node_id"):
        if field not in data: add_issue(issues, "error", f"iteration_{field}_missing", f"nodes[{node['id']}].data.{field}", f"iteration missing {field}")
    if "iterator_selector" in data: validate_selector(issues, data["iterator_selector"], f"nodes[{node['id']}].data.iterator_selector", node_ids)
    if "output_selector" in data: validate_selector(issues, data["output_selector"], f"nodes[{node['id']}].data.output_selector", node_ids)
    sid = data.get("start_node_id")
    if sid and node_types.get(sid) != "iteration-start": add_issue(issues, "error", "iteration_start_node_invalid", f"nodes[{node['id']}].data.start_node_id", f"start_node_id does not point to iteration-start: {sid}")


def validate_loop(issues: list[dict], node: dict, node_types: dict[str, str], node_ids: set[str]) -> None:
    data = node.get("data") or {}
    for field in ("loop_count", "break_conditions", "logical_operator", "start_node_id"):
        if field not in data: add_issue(issues, "error", f"loop_{field}_missing", f"nodes[{node['id']}].data.{field}", f"loop missing {field}")
    sid = data.get("start_node_id")
    if sid and node_types.get(sid) != "loop-start": add_issue(issues, "error", "loop_start_node_invalid", f"nodes[{node['id']}].data.start_node_id", f"start_node_id does not point to loop-start: {sid}")
    for i, cond in enumerate(data.get("break_conditions") or []):
        selector = cond.get("variable_selector")
        if selector is not None: validate_selector(issues, selector, f"nodes[{node['id']}].data.break_conditions[{i}].variable_selector", node_ids)


def validate_variable_aggregator(issues: list[dict], node: dict, node_ids: set[str]) -> None:
    data = node.get("data") or {}
    if not data.get("output_type"): add_issue(issues, "error", "variable_aggregator_output_type_missing", f"nodes[{node['id']}].data.output_type", "variable-aggregator missing output_type")
    vars_ = data.get("variables")
    if not isinstance(vars_, list) or not vars_: add_issue(issues, "error", "variable_aggregator_variables_missing", f"nodes[{node['id']}].data.variables", "variable-aggregator missing variables"); return
    for i, sel in enumerate(vars_): validate_selector(issues, sel, f"nodes[{node['id']}].data.variables[{i}]", node_ids)


def validate_assigner(issues: list[dict], node: dict, node_ids: set[str]) -> None:
    data = node.get("data") or {}
    if data.get("version") != "2": add_issue(issues, "warning", "assigner_version_not_explicit", f"nodes[{node['id']}].data.version", 'assigner should use version: "2"')
    items = data.get("items")
    if not isinstance(items, list) or not items: add_issue(issues, "error", "assigner_items_missing", f"nodes[{node['id']}].data.items", "assigner missing items"); return
    for i, item in enumerate(items):
        selector = item.get("variable_selector")
        if selector is None: add_issue(issues, "error", "assigner_target_missing", f"nodes[{node['id']}].data.items[{i}].variable_selector", "assigner item missing variable_selector")
        else: validate_selector(issues, selector, f"nodes[{node['id']}].data.items[{i}].variable_selector", node_ids)
        if item.get("input_type") == "variable": validate_selector(issues, item.get("value"), f"nodes[{node['id']}].data.items[{i}].value", node_ids)


def validate_human_input(issues: list[dict], node: dict) -> None:
    data = node.get("data") or {}
    dm = data.get("delivery_methods")
    if not isinstance(dm, list) or not dm: add_issue(issues, "error", "human_input_delivery_missing", f"nodes[{node['id']}].data.delivery_methods", "human-input missing delivery_methods")
    ua = data.get("user_actions")
    if not isinstance(ua, list) or not ua: add_issue(issues, "error", "human_input_actions_missing", f"nodes[{node['id']}].data.user_actions", "human-input missing user_actions")
    else:
        aids = [a.get("id") for a in ua if isinstance(a, dict)]
        for aid, n in Counter(aids).items():
            if aid and n > 1: add_issue(issues, "error", "human_input_action_id_duplicate", f"nodes[{node['id']}].data.user_actions", f"duplicate action id: {aid}")


def validate_trigger_webhook(issues: list[dict], node: dict) -> None:
    data = node.get("data") or {}
    body = data.get("body")
    if body is not None and not isinstance(body, list): add_issue(issues, "error", "trigger_webhook_body_invalid_type", f"nodes[{node['id']}].data.body", "trigger-webhook body must be an array, not an object")


def validate_trigger_schedule(issues: list[dict], node: dict) -> None:
    data = node.get("data") or {}
    mode = data.get("mode")
    if mode == "cron" and not data.get("cron_expression"): add_issue(issues, "error", "trigger_schedule_cron_missing", f"nodes[{node['id']}].data.cron_expression", "trigger-schedule cron mode requires cron_expression")


def validate_trigger_plugin(issues: list[dict], node: dict) -> None:
    data = node.get("data") or {}
    for field in ("plugin_id", "provider_id", "event_name", "subscription_id", "plugin_unique_identifier", "event_parameters"):
        if field not in data: add_issue(issues, "error", f"trigger_plugin_{field}_missing", f"nodes[{node['id']}].data.{field}", f"trigger-plugin missing {field}")


def validate_agent(issues: list[dict], node: dict) -> None:
    data = node.get("data") or {}
    for field in ("agent_strategy_provider_name", "agent_strategy_name", "agent_strategy_label", "agent_parameters"):
        if field not in data: add_issue(issues, "error", f"agent_{field}_missing", f"nodes[{node['id']}].data.{field}", f"agent missing {field}")


# ── NEW validators ────────────────────────────────────────────

def validate_llm(issues: list[dict], node: dict) -> None:
    data = node.get("data") or {}
    model = data.get("model") or {}
    if not model.get("provider"): add_issue(issues, "error", "llm_provider_missing", f"nodes[{node['id']}].data.model.provider", "llm missing model.provider")
    if not model.get("name"): add_issue(issues, "error", "llm_model_name_missing", f"nodes[{node['id']}].data.model.name", "llm missing model.name")
    pt = data.get("prompt_template")
    if not isinstance(pt, list) or not pt: add_issue(issues, "error", "llm_prompt_template_missing", f"nodes[{node['id']}].data.prompt_template", "llm missing prompt_template")
    ctx = data.get("context") or {}
    if "variable_selector" not in ctx: add_issue(issues, "warning", "llm_context_selector_missing", f"nodes[{node['id']}].data.context", "llm context.variable_selector recommended")


def validate_code(issues: list[dict], node: dict) -> None:
    data = node.get("data") or {}
    cl = data.get("code_language")
    if cl not in ("python3", "javascript"): add_issue(issues, "error", "code_language_invalid", f"nodes[{node['id']}].data.code_language", "code node requires code_language: python3 or javascript")
    code = data.get("code")
    if not isinstance(code, str) or not code.strip(): add_issue(issues, "error", "code_body_missing", f"nodes[{node['id']}].data.code", "code node missing code body")
    outputs = data.get("outputs")
    if not isinstance(outputs, dict) or not outputs: add_issue(issues, "error", "code_outputs_missing", f"nodes[{node['id']}].data.outputs", "code node missing outputs")


def validate_tool(issues: list[dict], node: dict) -> None:
    data = node.get("data") or {}
    for field in ("provider_id", "provider_name", "provider_type", "tool_name"):
        if field not in data or not data[field]: add_issue(issues, "error", f"tool_{field}_missing", f"nodes[{node['id']}].data.{field}", f"tool node missing {field}")


def validate_start(issues: list[dict], node: dict) -> None:
    data = node.get("data") or {}
    variables = data.get("variables") or []
    names = [v.get("variable") for v in variables if isinstance(v, dict)]
    for name, n in Counter(names).items():
        if name and n > 1: add_issue(issues, "error", "start_variable_duplicate", f"nodes[{node['id']}].data.variables", f"start node has duplicate variable name: {name}")


def validate_knowledge_index(issues: list[dict], node: dict) -> None:
    data = node.get("data") or {}
    if not data.get("chunk_structure"): add_issue(issues, "error", "knowledge_index_chunk_structure_missing", f"nodes[{node['id']}].data.chunk_structure", "knowledge-index missing chunk_structure")
    if not data.get("index_chunk_variable_selector"): add_issue(issues, "error", "knowledge_index_selector_missing", f"nodes[{node['id']}].data.index_chunk_variable_selector", "knowledge-index missing index_chunk_variable_selector")


# ── Edge data validators ──────────────────────────────────────

def validate_edge_data(issues: list[dict], edge: dict, index: int, node_types: dict[str, str]) -> None:
    """Check isInIteration + isInLoop + loop_id/iteration_id on every edge."""
    ed = edge.get("data") or {}
    eid = f"edges[{index}]"
    if ed.get("isInLoop"):
        if "loop_id" not in ed:
            add_issue(issues, "error", "edge_loop_id_missing", f"{eid}.data.loop_id", "loop edge missing loop_id")
    if ed.get("isInIteration"):
        if "iteration_id" not in ed:
            add_issue(issues, "error", "edge_iteration_id_missing", f"{eid}.data.iteration_id", "iteration edge missing iteration_id")


def validate_conversation_variables(issues: list[dict], cvars: list) -> None:
    """Check conversation_variables id is valid UUID."""
    for i, cv in enumerate(cvars):
        if not isinstance(cv, dict): continue
        cid = cv.get("id", "")
        if not UUID_RE.match(str(cid)):
            add_issue(issues, "error", "conversation_variable_id_not_uuid", f"conversation_variables[{i}].id", f"conversation_variables id must be valid UUID, got: {cid}")


def validate_version(issues: list[dict], version: object) -> None:
    """Check version is a string."""
    if version is None:
        add_issue(issues, "warning", "version_missing", "version", "version field missing, defaults to 0.1.0")
    elif not isinstance(version, str):
        add_issue(issues, "error", "version_not_string", "version", f"version must be a string (e.g. \"0.6.0\"), got {type(version).__name__}: {version}")


# ── Main lint entry ───────────────────────────────────────────

def lint_dsl(path: Path, data: dict) -> dict:
    issues: list[dict] = []
    kind = data.get("kind", "")
    app = data.get("app") or {}
    mode = app.get("mode", "")
    workflow = data.get("workflow") or {}
    graph = workflow.get("graph") or {}
    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []

    # Version
    validate_version(issues, data.get("version"))

    # Conversation variables
    cvs = workflow.get("conversation_variables") or []
    if cvs:
        validate_conversation_variables(issues, cvs)

    if not nodes:
        add_issue(issues, "error", "nodes_missing", "workflow.graph.nodes", "no nodes found")
    if not edges:
        add_issue(issues, "warning", "edges_missing", "workflow.graph.edges", "no edges found")

    node_ids = []
    node_types: dict[str, str] = {}
    type_counts: Counter[str] = Counter()

    for i, node in enumerate(nodes):
        nid = node.get("id")
        if not nid:
            add_issue(issues, "error", "node_id_missing", f"nodes[{i}].id", "node missing id"); continue
        node_ids.append(str(nid))
        nt = get_node_type(node)
        if not nt:
            add_issue(issues, "error", "node_type_missing", f"nodes[{nid}].data.type", "node missing data.type"); continue
        node_types[str(nid)] = nt
        type_counts[nt] += 1

    for nid, n in Counter(node_ids).items():
        if n > 1: add_issue(issues, "error", "node_id_duplicate", f"nodes[{nid}].id", f"duplicate node id: {nid}")

    nid_set = set(node_types)
    outgoing_handles: dict[str, set[str]] = defaultdict(set)

    # validate edges
    for i, edge in enumerate(edges):
        src, tgt = edge.get("source"), edge.get("target")
        if src not in nid_set: add_issue(issues, "error", "edge_source_missing", f"edges[{i}].source", f"edge source unknown: {src}")
        if tgt not in nid_set: add_issue(issues, "error", "edge_target_missing", f"edges[{i}].target", f"edge target unknown: {tgt}")
        if src:
            h = edge.get("sourceHandle")
            if isinstance(h, str): outgoing_handles[str(src)].add(h)
        # NEW: edge data validation
        validate_edge_data(issues, edge, i, node_types)

    # Graph-level constraints
    if type_counts.get("start") and any(nt.startswith("trigger-") for nt in type_counts):
        add_issue(issues, "error", "mixed_start_and_trigger", "workflow.graph.nodes", "start and trigger-* nodes cannot coexist")

    if kind in ("app", ""):
        if mode == "workflow" and not type_counts.get("end"):
            add_issue(issues, "error", "workflow_end_missing", "workflow.graph.nodes", "workflow mode requires an end node")
        if mode == "advanced-chat" and not type_counts.get("answer"):
            add_issue(issues, "error", "advanced_chat_answer_missing", "workflow.graph.nodes", "advanced-chat mode requires an answer node")
    elif kind == "rag_pipeline" and not type_counts.get("knowledge-index"):
        add_issue(issues, "error", "rag_pipeline_knowledge_index_missing", "workflow.graph.nodes", "rag_pipeline requires a knowledge-index node")

    # Container children parentId check
    container_ids = set()
    for nid, nt in node_types.items():
        if nt in ("loop", "iteration"):
            container_ids.add(nid)
    for node in nodes:
        nid = str(node.get("id"))
        nt = node_types.get(nid, "")
        if nt in ("loop-start", "loop-end", "iteration-start") or (nid in container_ids):
            continue  # skip container start/end nodes and containers themselves
        pid = node.get("parentId")
        if pid and pid in container_ids:
            pass  # correctly parented
        # Not an error to be outside a container; this is just metadata

    # Per-type validators with arg counts: (issues, node) or (issues, node, nid_set)
    _2ARG = {"start", "llm", "code", "tool", "agent", "human-input", "trigger-webhook", "trigger-schedule", "trigger-plugin", "knowledge-index"}
    _3ARG = {"end", "parameter-extractor", "knowledge-retrieval", "list-operator", "variable-aggregator", "assigner"}
    _HANDLES = {"if-else", "question-classifier"}
    _CONTAINER = {"iteration", "loop"}

    for node in nodes:
        nid = str(node.get("id"))
        nt = node_types.get(nid)
        if not nt: continue

        if nt in _HANDLES:
            if nt == "if-else":
                validate_if_else(issues, node, outgoing_handles, nid_set)
            else:
                validate_question_classifier(issues, node, outgoing_handles, nid_set)
        elif nt in _CONTAINER:
            if nt == "iteration":
                validate_iteration(issues, node, node_types, nid_set)
            else:
                validate_loop(issues, node, node_types, nid_set)
        elif nt in _2ARG:
            fn = {"start": validate_start, "llm": validate_llm, "code": validate_code, "tool": validate_tool,
                  "agent": validate_agent, "human-input": validate_human_input, "trigger-webhook": validate_trigger_webhook,
                  "trigger-schedule": validate_trigger_schedule, "trigger-plugin": validate_trigger_plugin,
                  "knowledge-index": validate_knowledge_index}[nt]
            fn(issues, node)
        elif nt in _3ARG:
            fn = {"end": validate_end, "parameter-extractor": validate_parameter_extractor,
                  "knowledge-retrieval": validate_knowledge_retrieval, "list-operator": validate_list_operator,
                  "variable-aggregator": validate_variable_aggregator, "assigner": validate_assigner}[nt]
            fn(issues, node, nid_set)

    error_count = sum(1 for i in issues if i["severity"] == "error")
    warning_count = sum(1 for i in issues if i["severity"] == "warning")
    return {"path": str(path), "kind": kind or "(unknown)", "mode": mode or "(unknown)", "node_count": len(nodes), "edge_count": len(edges), "error_count": error_count, "warning_count": warning_count, "issues": issues}


def render_report(report: dict) -> str:
    lines = [
        f"sample: {report['path']}",
        f"kind: {report['kind']}  mode: {report['mode']}",
        f"nodes: {report['node_count']}  edges: {report['edge_count']}",
        f"errors: {report['error_count']}  warnings: {report['warning_count']}",
    ]
    if report["issues"]:
        lines.append("")
        for issue in report["issues"]:
            lines.append(f"  [{issue['severity']}] {issue['code']} | {issue['path']} | {issue['message']}")
    else:
        lines.append("\n  No issues found.")
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) not in {2, 3}:
        print("Usage: python lint_dsl.py <dsl-path> [--json]", file=sys.stderr)
        return 1
    path = Path(sys.argv[1]).expanduser().resolve()
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        return 1
    emit_json = len(sys.argv) == 3 and sys.argv[2] == "--json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as exc:
        print(f"Error: YAML parse failed — {exc}", file=sys.stderr)
        return 1
    report = lint_dsl(path, data)
    if emit_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_report(report))
    return 1 if report["error_count"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
