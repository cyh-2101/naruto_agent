# Naruto Agent Lab 中文说明

这是一个纯视觉、多角色格斗智能体研究平台，首批角色是鹰小队佐助、白面具和佩恩。当前
仓库拥有已通过 mock 验证的 Foundation 运行/录制底座，以及通过合成测试验证的
Architecture V2 契约；它还没有可用的游戏感知、角色机制、训练策略或自动战斗能力。

## V2 核心流程

```text
截屏 -> 被动感知 -> TemporalCombatState -> IR / SQ（默认）/ IQ
-> 共享时序骨干 -> 角色适配 -> SemanticAction
-> ActionCapabilities -> ActionScheduler -> SafetyGate -> 输入后端
```

- `Estimate[T]` 记录值、置信度、新鲜度、来源和无法获取的原因；
- IR 可以在证据足够时使用双方身份，SQ 只保留我方身份，IQ 隐藏双方身份；
- 策略只输出上下、左右、技能、方向、持续时间等语义，不知道键盘绑定；
- 动作能力判断不能绕过 scheduler 和 SafetyGate；
- 三个角色共享同一个时序架构，只保留各自的小型适配器、模板和已校准能力；
- Episode V2 会明确区分 valid、unknown、invalid、stale 和 not implemented。

## 安全边界

只允许训练模式、游戏 AI 练习和所有人同意的私人对局。禁止排位/公开自动化、非自愿对手、
读取游戏内存、注入、Hook、网络包、隐藏状态或反作弊绕过。所有输入默认 dry-run；当前没有
工作单授权自动输入，也没有启动 BC、PPO、RL、自博弈、HELT/PFSP 或 world model。

## 当前证据

2026-08-21 的安全测试结果是 64 个测试通过，覆盖旧 Foundation、V2 状态/视图/动作/能力/
数据契约和禁止绕过安全路径。它们是单元与 mock 证据，不是实机感知、DXCam 性能、角色
机制或游戏水平证据。

下一份 [Work Order 002](docs/CODEX_WORK_ORDER_002.md) 只是待批准方案：只做被动截屏验证、
本地校准、用户手动演示录制、窄范围感知与离线人工评估，不生成任何游戏输入，也不训练。

详细内容见 [Architecture V2](docs/ARCHITECTURE.md)、[项目状态](docs/PROJECT_STATUS.md) 和
[运行手册](docs/RUNBOOK.md)。项目负责人可以把 [learners.md](learners.md) 发给 ChatGPT，
让它按已经验证的能力教学。
