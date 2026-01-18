## 使用方法

将本仓库克隆到本地，然后将本仓库的 skills 目录下的文件夹按需软链接到目标工具的 skills 目录下。

例如你使用 pi coding agent，它的 skills 目录在 `~/.pi/agent/skills` 目录下，则将工具添加到 pi 需要执行：

```bash
mkdir -p ~/.pi/agent/skills
ln -s $PWD/skills/<tool_name> ~/.pi/agent/skills/<tool_name>
```

## 提示

本仓库无法开箱即用，仅供用于参考
