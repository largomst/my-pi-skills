---
name: vision-describe
description: 当需要理解图片内容时，使用此 skill。
---


### vision describe

Image understanding via VLM. Provide either `--image` or `--file-id`, not both.

```bash
mmx vision describe (--image <path-or-url> | --file-id <id>) [flags]
```

| Flag | Type | Description |
|---|---|---|
| `--image <path-or-url>` | string | Local path or URL (auto base64-encoded) |
| `--file-id <id>` | string | Pre-uploaded file ID (skips base64) |
| `--prompt <text>` | string | Question about the image (default: `"Describe the image."`) |

```bash
mmx vision describe --image photo.jpg --prompt "What breed?" --output json
```

**stdout**: description text (text mode) or full response (json mode).