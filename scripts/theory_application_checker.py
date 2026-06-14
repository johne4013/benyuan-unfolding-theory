#!/usr/bin/env python3
"""
理论应用检视脚本
在任务执行前，根据任务描述自动生成理论检视清单
"""

import json
from datetime import datetime
from pathlib import Path

class TheoryApplicationChecker:
    """根据任务描述生成理论应用检视清单"""

    def __init__(self):
        self.task_levels = {
            'simple': ['bug', '修复', '问题', '简单', '问答', '查询', '查找'],
            'engineering': [
                '文件', '配置', '代码', '工具', '部署', '修改',
                '脚本', '自动化', '集成', '优化', '性能', '健壮性', '错误处理',
                '指南', '说明', '文档', '集成指南'
            ],
            'subject': ['Hermes', '自己', '认同', '主体', '身份', '协同'],
            'theory': ['本原', '展开', '理论', '概念', '定义', '框架', '框架改进', '框架优化'],
            'core': ['core/', 'concepts.md', 'theory.md', '修改定义'],
        }

    def detect_task_level(self, task_description):
        """根据任务描述自动判断任务层级"""
        description = task_description.lower()

        # 检查 core 层（最高优先级）
        for keyword in self.task_levels['core']:
            if keyword.lower() in description:
                return 'core'

        # 检查理论层
        for keyword in self.task_levels['theory']:
            if keyword.lower() in description:
                return 'theory'

        # 检查主体层
        for keyword in self.task_levels['subject']:
            if keyword.lower() in description:
                return 'subject'

        # 检查工程层
        for keyword in self.task_levels['engineering']:
            if keyword.lower() in description:
                return 'engineering'

        # 默认简单
        return 'simple'

    def generate_checklist(self, task_id, task_name, task_description):
        """生成完整的检视清单"""

        task_level = self.detect_task_level(task_description)

        checklist = {
            'task_id': task_id,
            'task_name': task_name,
            'task_level': task_level,
            'created_at': datetime.now().isoformat(),
            'checklist': self._generate_checklist_items(task_level),
            'recommendations': self._generate_recommendations(task_level),
        }

        return checklist

    def _generate_checklist_items(self, task_level):
        """根据任务层级生成检视清单"""

        base_items = [
            {
                'dimension': '0. 事前差分申报',
                'status': '待填写',
                'result': None,
                'guidance': '理论让我做出了什么不同于默认做法的选择？同时写出反事实默认做法；填"无差分"合法'
            },
            {
                'dimension': '1. 层级定位',
                'status': '✓',
                'result': task_level,
                'action': self._get_level_action(task_level)
            }
        ]

        if task_level in ['engineering', 'theory', 'subject', 'core']:
            base_items.extend([
                {
                    'dimension': '2. 约束识别',
                    'status': '待填写',
                    'result': None,
                    'guidance': '列出 3-5 个关键约束'
                },
                {
                    'dimension': '3. 展开方向',
                    'status': '待填写',
                    'result': None,
                    'guidance': '明确 2-4 个关键阶段'
                },
                {
                    'dimension': '4. 失败条件',
                    'status': '待填写',
                    'result': None,
                    'guidance': '什么情况下应该停止'
                },
            ])

        if task_level in ['subject', 'theory']:
            base_items.append({
                'dimension': '5. 连续性维持',
                'status': '待填写',
                'result': None,
                'guidance': '与现有认同的一致性'
            })

        if task_level == 'core':
            base_items.append({
                'dimension': '6. 用户批准',
                'status': '必需',
                'result': '待用户确认',
                'guidance': '需要明确的用户授权'
            })

        return base_items

    def _get_level_action(self, level):
        """根据层级返回建议的行动"""
        actions = {
            'simple': '快速执行，事后总结',
            'engineering': '检查约束和失败条件，安全执行',
            'subject': '加载 agent_self_state，深度检视',
            'theory': '加载完整 core，完整检视，可能需要反馈',
            'core': '询问用户明确授权，需要备份',
        }
        return actions.get(level, '按标准流程执行')

    def _generate_recommendations(self, task_level):
        """生成推荐步骤"""
        recommendations = {
            'simple': [
                '直接执行任务',
                '完成后记录一句话总结',
            ],
            'engineering': [
                '识别关键约束',
                '确认失败条件',
                '执行任务',
                '完成后记录执行日志',
            ],
            'subject': [
                '读 agent_self_state.md',
                '执行完整的 6 个检视',
                '执行任务',
                '生成完整的反馈',
            ],
            'theory': [
                '加载 core/bootstrap.md',
                '执行完整的 6 个检视',
                '深度执行任务',
                '生成详细的反馈和理论候选',
            ],
            'core': [
                '询问用户',
                '备份现有 core',
                '执行完整的 6 个检视',
                '深度执行，生成详细的理由',
                '等待用户批准',
            ]
        }
        return recommendations.get(task_level, ['按标准流程执行'])

    def save_checklist(self, checklist, output_dir=None):
        """保存检视清单"""
        if output_dir is None:
            from paths import runtime_dir
            output_dir = runtime_dir() / "task_checklists"
        output_path = Path(output_dir).expanduser()
        output_path.mkdir(parents=True, exist_ok=True)

        checklist_file = output_path / f"{checklist['task_id']}-checklist.json"
        with open(checklist_file, 'w', encoding='utf-8') as f:
            json.dump(checklist, f, indent=2, ensure_ascii=False)

        return str(checklist_file)

    def print_checklist(self, checklist):
        """美化打印检视清单"""
        print(f"\n{'='*60}")
        print(f"理论应用检视清单")
        print(f"{'='*60}")
        print(f"\n任务 ID：{checklist['task_id']}")
        print(f"任务名：{checklist['task_name']}")
        print(f"任务层级：{checklist['task_level'].upper()}")

        print(f"\n【检视清单】")
        for item in checklist['checklist']:
            status_icon = '✓' if item.get('status') == '✓' else '◻'
            print(f"{status_icon} {item['dimension']}")
            if item.get('action'):
                print(f"   → {item['action']}")
            elif item.get('guidance'):
                print(f"   → {item['guidance']}")

        print(f"\n【推荐步骤】")
        for i, rec in enumerate(checklist['recommendations'], 1):
            print(f"{i}. {rec}")

        print(f"\n{'='*60}\n")


# 命令行使用
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("使用方法：")
        print("  python theory_application_checker.py <task_id> <task_name> [task_description]")
        print("\n例：")
        print("  python theory_application_checker.py task-001 '修复登录 bug' '登录页面偶尔失败'")
        sys.exit(1)

    task_id = sys.argv[1]
    task_name = sys.argv[2]
    task_desc = sys.argv[3] if len(sys.argv) > 3 else task_name

    checker = TheoryApplicationChecker()
    checklist = checker.generate_checklist(task_id, task_name, task_desc)

    # 打印到控制台
    checker.print_checklist(checklist)

    # 保存到文件
    saved_path = checker.save_checklist(checklist)
    print(f"✓ 检视清单已保存到：{saved_path}")
