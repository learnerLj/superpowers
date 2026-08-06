# 纵深防御验证

## 概述

无效数据导致 bug 时，只在一个位置增加校验看似足够，但其它代码路径、重构或 mock 都可能绕过它。

**核心原则：** 在数据经过的每一层进行验证，让 bug 在结构上不可能发生。

## 为什么需要多层验证

单层验证只是“修复了这个 bug”；多层验证是“让这个 bug 无法发生”。入口校验捕获大部分错误，业务逻辑捕获边界情况，环境 guard 阻止特定上下文中的危险行为，debug 日志则在其它层失效时提供证据。

## 四层防御

### 第 1 层：入口校验

目的：在 API 边界拒绝明显无效的输入。

```typescript
function createProject(name: string, workingDirectory: string) {
  if (!workingDirectory || workingDirectory.trim() === '') {
    throw new Error('workingDirectory cannot be empty');
  }
  if (!existsSync(workingDirectory)) {
    throw new Error(`workingDirectory does not exist: ${workingDirectory}`);
  }
  if (!statSync(workingDirectory).isDirectory()) {
    throw new Error(`workingDirectory is not a directory: ${workingDirectory}`);
  }
}
```

### 第 2 层：业务逻辑校验

目的：确保数据符合当前操作的语义。

```typescript
function initializeWorkspace(projectDir: string, sessionId: string) {
  if (!projectDir) {
    throw new Error('projectDir required for workspace initialization');
  }
}
```

### 第 3 层：环境 guard

目的：在特定上下文中阻止危险操作。

```typescript
async function gitInit(directory: string) {
  if (process.env.NODE_ENV === 'test') {
    const normalized = normalize(resolve(directory));
    const tmpDir = normalize(resolve(tmpdir()));
    if (!normalized.startsWith(tmpDir)) {
      throw new Error(`Refusing git init outside temp dir during tests: ${directory}`);
    }
  }
}
```

### 第 4 层：debug 观测

目的：保留事后分析所需上下文。

```typescript
async function gitInit(directory: string) {
  const stack = new Error().stack;
  logger.debug('About to git init', {
    directory,
    cwd: process.cwd(),
    stack,
  });
}
```

## 应用步骤

1. 追踪数据流：坏值来自哪里，又在哪里被使用？
2. 映射所有检查点：列出数据经过的每一个位置。
3. 在每层增加验证：入口、业务、环境和 debug。
4. 分别测试每一层：主动绕过第 1 层，确认第 2 层仍能捕获。

## 实例

问题：空 `projectDir` 导致在源码目录执行 `git init`。

数据流：测试 setup 产生空字符串 -> `Project.create(name, '')` -> `WorkspaceManager.createWorkspace('')` -> `git init` 在 `process.cwd()` 中运行。

加入的四层防御：`Project.create()` 验证非空、存在且可写；`WorkspaceManager` 再次验证非空；`WorktreeManager` 在测试中拒绝对 tmpdir 外执行 `git init`；执行前记录 stack trace。

结果：1847 个测试全部通过，问题无法复现。测试过程中每一层都捕获了其它层遗漏的路径，因此不要停在单一校验点。
