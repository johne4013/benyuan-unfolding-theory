#!/usr/bin/env python3
"""
理论演化候选管理脚本
生成、查看和管理理论演化候选
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

class EvolutionCandidateManager:
    """管理理论演化候选"""

    def __init__(self, candidates_dir='~/.hermes/continuity/runtime/evolution_candidates'):
        self.candidates_dir = Path(candidates_dir).expanduser()
        self.candidates_dir.mkdir(parents=True, exist_ok=True)

    def create_candidate(self, candidate_type: str, title: str, description: str,
                        source_task: str, improvement_direction: str = None) -> Dict:
        """创建一个新的理论演化候选"""

        candidate = {
            'id': f"cand-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'created_at': datetime.now().isoformat(),
            'type': candidate_type,  # PATTERN, ANOMALY, ENHANCEMENT
            'priority': self._get_priority(candidate_type),
            'title': title,
            'description': description,
            'source_task': source_task,
            'improvement_direction': improvement_direction or '待定',
            'status': 'CANDIDATE',
            'evidence_count': 1,
            'awaiting_review': True,
            'notes': [],
            'expansion_type': 'pending',  # 待用户确认：法则属性型/展开属性型/混合型
            'hope_direction': '',         # 待用户填写：一句话描述希望方向
            'opens_new_possibility': '',  # 待用户确认：是/否及其原因
        }

        return candidate

    def _get_priority(self, candidate_type: str) -> str:
        """根据类型获取优先级"""
        priorities = {
            'ANOMALY': 'high',
            'PATTERN': 'medium',
            'ENHANCEMENT': 'low',
        }
        return priorities.get(candidate_type, 'medium')

    def save_candidate(self, candidate: Dict) -> str:
        """保存候选到文件"""

        filename = f"{candidate['id']}-{candidate['type'].lower()}.json"
        filepath = self.candidates_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(candidate, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def load_candidate(self, candidate_id: str) -> Dict:
        """加载一个候选"""

        files = list(self.candidates_dir.glob(f"{candidate_id}-*.json"))
        if not files:
            raise FileNotFoundError(f"未找到候选：{candidate_id}")

        try:
            with open(files[0], 'r', encoding='utf-8') as f:
                candidate = json.load(f)
            return candidate
        except json.JSONDecodeError as e:
            raise ValueError(f"候选文件格式错误 {files[0]}：{str(e)}")
        except Exception as e:
            raise RuntimeError(f"加载候选失败：{str(e)}")

    def list_candidates(self, status: str = None, candidate_type: str = None) -> List[Dict]:
        """列出所有候选"""

        candidates = []
        for candidate_file in self.candidates_dir.glob("*.json"):
            with open(candidate_file, 'r', encoding='utf-8') as f:
                candidate = json.load(f)

            # 过滤
            if status and candidate['status'] != status:
                continue
            if candidate_type and candidate['type'] != candidate_type:
                continue

            candidates.append(candidate)

        # 按优先级和创建时间排序
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        candidates.sort(key=lambda x: (
            priority_order.get(x['priority'], 3),
            x['created_at']
        ), reverse=True)

        return candidates

    def update_candidate_status(self, candidate_id: str, new_status: str,
                               decision_notes: str = None) -> Dict:
        """更新候选状态"""

        candidate = self.load_candidate(candidate_id)
        candidate['status'] = new_status
        candidate['awaiting_review'] = new_status == 'CANDIDATE'

        if decision_notes:
            if 'notes' not in candidate:
                candidate['notes'] = []
            candidate['notes'].append({
                'timestamp': datetime.now().isoformat(),
                'note': decision_notes,
            })

        # 重新保存
        old_file = list(self.candidates_dir.glob(f"{candidate_id}-*.json"))[0]
        old_file.unlink()
        self.save_candidate(candidate)

        return candidate

    def add_evidence(self, candidate_id: str, evidence_task: str, evidence_description: str) -> Dict:
        """为候选添加证据（用于PATTERN类型）"""

        candidate = self.load_candidate(candidate_id)
        candidate['evidence_count'] = candidate.get('evidence_count', 1) + 1
        candidate['evidence'] = candidate.get('evidence', [])
        candidate['evidence'].append({
            'task_id': evidence_task,
            'description': evidence_description,
            'timestamp': datetime.now().isoformat(),
        })

        # 重新保存
        old_file = list(self.candidates_dir.glob(f"{candidate_id}-*.json"))[0]
        old_file.unlink()
        self.save_candidate(candidate)

        return candidate

    def enrich_candidate_from_hope_tracking(self, candidate: Dict,
                                           hope_tracking_data: Dict) -> Dict:
        """从PORF观察5（希望追踪）中自动提取信息，填充候选的新字段"""

        if not hope_tracking_data:
            return candidate

        # 从hope_tracking中提取expansion_type信号
        limitation = hope_tracking_data.get('limitation_encountered', '').lower()
        possibility = hope_tracking_data.get('possibility_description', '').lower()

        if '约束' in limitation or '限制' in limitation:
            candidate['expansion_type'] = '法则属性型'
        elif '生成' in possibility or '展开' in possibility or '打开' in possibility:
            candidate['expansion_type'] = '展开属性型'
        else:
            candidate['expansion_type'] = '混合型'

        # 从impact_on_hope推导hope_direction
        impact = hope_tracking_data.get('impact_on_hope', '')
        if impact == '推进':
            candidate['hope_direction'] = f"推进：{hope_tracking_data.get('possibility_description', '')}"
        elif impact == '挑战':
            candidate['hope_direction'] = f"挑战：{hope_tracking_data.get('limitation_encountered', '')}"
        else:
            candidate['hope_direction'] = f"维持：当前方向保持"

        # 从新发现的可能性填充opens_new_possibility
        if hope_tracking_data.get('new_possibility_found') == '是':
            candidate['opens_new_possibility'] = f"是——{hope_tracking_data.get('possibility_description', '')}"
        else:
            candidate['opens_new_possibility'] = '否'

        return candidate

    def print_candidate(self, candidate: Dict) -> None:
        """美化打印候选"""

        print(f"\n{'='*70}")
        print(f"理论演化候选")
        print(f"{'='*70}")
        print(f"ID：{candidate['id']}")
        print(f"类型：{candidate['type']}")
        print(f"优先级：{candidate['priority'].upper()}")
        print(f"状态：{candidate['status']}")
        print(f"标题：{candidate['title']}")
        print(f"\n描述：")
        print(f"{candidate['description']}")
        if candidate.get('improvement_direction'):
            print(f"\n改进方向：")
            print(f"{candidate['improvement_direction']}")
        if candidate.get('evidence_count', 1) > 1:
            print(f"\n证据数量：{candidate['evidence_count']}")
        print(f"\n创建于：{candidate['created_at']}")
        print(f"{'='*70}\n")

    def print_candidates_summary(self, candidates: List[Dict]) -> None:
        """打印候选摘要"""

        if not candidates:
            print("未找到候选")
            return

        print(f"\n{'='*70}")
        print(f"理论演化候选摘要")
        print(f"{'='*70}")

        by_type = {}
        for candidate in candidates:
            ctype = candidate['type']
            if ctype not in by_type:
                by_type[ctype] = []
            by_type[ctype].append(candidate)

        for ctype in ['ANOMALY', 'PATTERN', 'ENHANCEMENT']:
            if ctype in by_type:
                print(f"\n【{ctype}】({len(by_type[ctype])} 个)")
                for cand in by_type[ctype]:
                    status = '✓' if cand['status'] == 'INTEGRATED' else '◻'
                    priority = '🔴' if cand['priority'] == 'high' else '🟡' if cand['priority'] == 'medium' else '🟢'
                    evidence = f" [{cand.get('evidence_count', 1)}x]" if cand.get('evidence_count', 1) > 1 else ""
                    print(f"  {status} {priority} {cand['id']}: {cand['title']}{evidence}")

        print(f"\n{'='*70}\n")


# 命令行接口
if __name__ == '__main__':
    import sys

    manager = EvolutionCandidateManager()

    if len(sys.argv) < 2:
        print("理论演化候选管理工具")
        print("="*70)
        print("\n使用方法：")
        print("  list              列出所有候选")
        print("  list-pending      列出待评审候选")
        print("  show <id>         查看一个候选")
        print("  approve <id>      批准一个候选")
        print("  reject <id>       拒绝一个候选")
        print("  defer <id>        延迟一个候选")
        print("  add-evidence <id> <task> <description>")
        print("                    为 PATTERN 类候选添加证据")
        print("\n" + "="*70)

    elif sys.argv[1] == 'list':
        candidates = manager.list_candidates()
        manager.print_candidates_summary(candidates)

    elif sys.argv[1] == 'list-pending':
        candidates = manager.list_candidates(status='CANDIDATE')
        manager.print_candidates_summary(candidates)

    elif sys.argv[1] == 'show' and len(sys.argv) > 2:
        candidate = manager.load_candidate(sys.argv[2])
        manager.print_candidate(candidate)

    elif sys.argv[1] == 'approve' and len(sys.argv) > 2:
        candidate = manager.update_candidate_status(
            sys.argv[2], 'APPROVED',
            '用户批准进入理论更新流程'
        )
        print(f"✓ 已批准：{candidate['title']}")

    elif sys.argv[1] == 'reject' and len(sys.argv) > 2:
        reason = sys.argv[3] if len(sys.argv) > 3 else '不符合条件'
        candidate = manager.update_candidate_status(
            sys.argv[2], 'REJECTED',
            f'拒绝理由：{reason}'
        )
        print(f"✗ 已拒绝：{candidate['title']}")

    elif sys.argv[1] == 'defer' and len(sys.argv) > 2:
        candidate = manager.update_candidate_status(
            sys.argv[2], 'DEFERRED',
            '延迟评审，标记为未来研究'
        )
        print(f"⏸ 已延迟：{candidate['title']}")

    elif sys.argv[1] == 'add-evidence' and len(sys.argv) > 3:
        task_id = sys.argv[2]
        task_name = sys.argv[3]
        description = sys.argv[4] if len(sys.argv) > 4 else task_name
        candidate = manager.add_evidence(task_id, task_name, description)
        print(f"✓ 已添加证据：现在有 {candidate['evidence_count']} 个证据")

    else:
        print("命令不认识，使用 --help 查看帮助")
