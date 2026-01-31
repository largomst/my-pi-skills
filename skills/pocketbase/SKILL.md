---
name: pocketbase
description: Comprehensive PocketBase database management skill. Use this skill when the user wants to interact with a PocketBase instance to manage collections, records, users, or perform database backups. It provides a Python client script to execute these operations.
---

# PocketBase Skill

## Overview

This skill allows you to interact with a PocketBase instance. It provides a Python script wrapper around the PocketBase API to perform common operations like managing collections, records, and users.

## Prerequisites

Ensure the following environment variables are set (or pass them as arguments to the script):
- `POCKETBASE_URL` (default: `http://127.0.0.1:8090`)
- `POCKETBASE_ADMIN_EMAIL` (for admin operations)
- `POCKETBASE_ADMIN_PASSWORD` (for admin operations)

## Usage

Use the `scripts/pb_client.py` script to interact with PocketBase. It is recommended to use `uv run` to execute the script, which handles dependencies automatically.

### Common Commands

#### 1. Collections

**List all collections:**
```bash
uv run pocketbase/scripts/pb_client.py list_collections
```

**Get a specific collection:**
```bash
uv run pocketbase/scripts/pb_client.py get_collection --collection <collection_id_or_name>
```

**Create a collection:**
```bash
uv run pocketbase/scripts/pb_client.py create_collection --name <name> --type <base|auth|view> --schema '<json_schema>'
```

#### 2. Records

**List records:**
```bash
uv run pocketbase/scripts/pb_client.py list_records --collection <collection_name> --page 1 --per-page 30 --filter 'created > "2023-01-01"'
```

**Create a record:**
```bash
uv run pocketbase/scripts/pb_client.py create_record --collection <collection_name> --data '{"field": "value"}'
```

**Update a record:**
```bash
uv run pocketbase/scripts/pb_client.py update_record --collection <collection_name> --id <record_id> --data '{"field": "new_value"}'
```

**Delete a record:**
```bash
uv run pocketbase/scripts/pb_client.py delete_record --collection <collection_name> --id <record_id>
```

#### 3. Users

**Create a user:**
```bash
uv run pocketbase/scripts/pb_client.py create_user --data '{"email": "user@example.com", "password": "password123", "passwordConfirm": "password123", "name": "User Name"}'
```

#### 4. Database

**Backup database:**
```bash
uv run pocketbase/scripts/pb_client.py backup_database --name <backup_name>
```

## detailed Arguments

- `--url`: PocketBase URL (overrides env var)
- `--email`: Admin email (overrides env var)
- `--password`: Admin password (overrides env var)
- `--collection`: Collection name or ID
- `--id`: Record ID or Collection ID
- `--data`: JSON data string
- `--filter`: Filter query string
- `--sort`: Sort query string
- `--page`: Page number
- `--per-page`: Items per page
- `--name`: Name for collection or backup
- `--type`: Collection type
- `--schema`: JSON schema string for collection creation

