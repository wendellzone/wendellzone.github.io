---
name: superpowers
description: 一组用于提升 agent 工作质量的流程型 skills，包括需求澄清、TDD、系统化调试、计划编写、代码审查和完成前验证。
metadata:
  source: openai-curated-remote/superpowers
  version: 5.1.4
---

# Superpowers

`superpowers` 是一组流程型 skills，不是单个独立 skill。它的目标是把常见工程工作拆成更可靠的执行流程，减少跳步骤、凭感觉修 bug、未验证就宣称完成等问题。

## 包含内容

- `using-superpowers`：在任务开始时检查并启用相关 skill。
- `brainstorming`：在创建功能、组件或行为变更前澄清需求。
- `writing-plans`：把多步骤需求整理成可执行计划。
- `test-driven-development`：用测试先行约束功能或修复。
- `systematic-debugging`：用可复现、可验证的方式定位问题根因。
- `verification-before-completion`：在声明完成前强制跑验证。
- `requesting-code-review` / `receiving-code-review`：规范代码审查和反馈处理。
- `subagent-driven-development` / `dispatching-parallel-agents`：在合适场景下拆分并行工作。
- `using-git-worktrees`：为隔离开发工作准备独立 worktree。
- `finishing-a-development-branch`：完成开发分支后的收尾流程。
- `executing-plans`：按既定计划执行并设置检查点。
- `writing-skills`：创建和验证新的 skills。

## 安装

下载 `superpowers.zip` 后，将其中的 `superpowers/` 目录放到 Codex plugin/skills 可识别的位置，或按你的客户端支持的 plugin 导入方式安装。

如果只需要其中某个流程，也可以单独复制 `superpowers/skills/<skill-name>/` 下的 skill。
