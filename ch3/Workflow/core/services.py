import json
from django.conf import settings
from core.models import Employee, WorkflowStep


# 從設定的路徑讀取組織樹 JSON；檔案不存在時回傳空清單
def get_org_tree():
    path = settings.ORG_TREE_PATH
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


# 遞迴深度優先搜尋：依 dept_code 找到對應節點，找不到回傳 None
def _find_node(nodes, dept_code):
    for node in nodes:
        if node.get("code") == dept_code:
            return node
        found = _find_node(node.get("children", []), dept_code)
        if found:
            return found
    return None


# 遞迴找父節點：回傳 dept_code 所在節點的直屬上層節點 dict；根節點無父節點時回傳 None
def _find_parent(nodes, dept_code, parent=None):
    for node in nodes:
        if node.get("code") == dept_code:
            return parent
        found = _find_parent(node.get("children", []), dept_code, node)
        if found is not None:
            return found
    return None


# 將組織樹展平為 [{"code": ..., "name": ...}, ...] 清單，供下拉選單使用
def get_dept_list():
    tree = get_org_tree()
    depts = []

    def _collect(nodes):
        for node in nodes:
            depts.append({"code": node["code"], "name": node["name"]})
            _collect(node.get("children", []))

    _collect(tree)
    return depts


def resolve_approver(step: WorkflowStep, submitter: Employee) -> Employee | None:
    """依步驟設定解析出實際審核人員；找不到合適人員時回傳 None。"""
    atype = step.approver_type

    # 指定人員：直接使用步驟上設定的固定員工
    if atype == "specific_employee":
        return step.specific_approver

    tree = get_org_tree()
    dept_code = submitter.department_code

    if atype == "direct_manager":
        # 多層級主管逐級上簽：
        #   第 1 關 → 申請人自身部門主管（levels_up = 0，不移動）
        #   第 2 關 → 上一級部門主管（levels_up = 1）
        #   第 N 關 → 沿組織樹向上走 N-1 層
        current_code = dept_code
        for _ in range(step.step_number - 1):
            parent_node = _find_parent(tree, current_code)
            if parent_node is None:
                # 已到達組織樹頂層，無更高層主管可簽
                break
            current_code = parent_node["code"]
        node = _find_node(tree, current_code)
        if node and node.get("manager_id"):
            try:
                return Employee.objects.get(pk=node["manager_id"])
            except Employee.DoesNotExist:
                pass

    elif atype == "dept_manager":
        # 有指定部門時找該部門主管；否則取申請人上一級部門的主管
        node = _find_node(tree, step.specific_dept) if step.specific_dept else _find_parent(tree, dept_code)
        if node and node.get("manager_id"):
            try:
                return Employee.objects.get(pk=node["manager_id"])
            except Employee.DoesNotExist:
                pass

    return None


# 取得指定步驟編號的所有審核人員清單（並簽情況下可能多人）
def get_next_approver(case, next_step_number):
    steps = case.workflow.steps.filter(step_number=next_step_number)
    approvers = []
    for step in steps:
        approver = resolve_approver(step, case.created_by)
        if approver:
            approvers.append(approver)
    return approvers
