# Naruto Agent Lab 中文说明

这是一个从最终架构出发搭建的纯视觉、多角色格斗智能体平台。首批角色为：

- 鹰小队佐助 `taka_sasuke`
- 白面具 `white_mask`
- 佩恩 `pain`

系统最终会同时利用三类数据：你自己的“画面 + 按键”演示、没有按键标签的完整对局视频，以及 AI 在训练场里的闭环交互数据。

架构核心不是三个互不相关的脚本，而是：

- 共享视觉编码器与战斗理解；
- 共享时序记忆和对手建模；
- 分层决策：战略、战术、动作执行；
- 三个角色各自的 Adapter、技能知识包和连招图；
- 原始数据永久保留、模型和实验可复现；
- 后续可加入无标签视频学习、Offline RL、World Model、策略池和阵容级记忆。

## 给 Codex 的一句话

打开整个文件夹后发送：

`Read AGENTS.md and execute docs/CODEX_WORK_ORDER_001.md. Do not skip tests or documentation updates.`

第一轮只建设最终系统的可靠地基，不直接上 PPO，也不允许默认发送真实按键。
