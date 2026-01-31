# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
# ]
# ///
import argparse
import os
import sys
import json
import requests
from typing import Optional, Dict, Any, List

# Default PocketBase URL
DEFAULT_PB_URL = "http://127.0.0.1:8090"

class PocketBaseClient:
    def __init__(self, url: str, email: Optional[str] = None, password: Optional[str] = None):
        self.url = url.rstrip('/')
        self.token = None
        self.admin_email = email
        self.admin_password = password
        
        # Try to authenticate if credentials are provided
        if self.admin_email and self.admin_password:
            self.authenticate_admin()

    def authenticate_admin(self):
        """Authenticate as admin to get a token."""
        # Try new v0.23+ superuser auth first
        try:
            resp = requests.post(f"{self.url}/api/collections/_superusers/auth-with-password", json={
                "identity": self.admin_email,
                "password": self.admin_password
            })
            if resp.status_code == 404:
                 # Fallback to old admin auth
                 resp = requests.post(f"{self.url}/api/admins/auth-with-password", json={
                    "identity": self.admin_email,
                    "password": self.admin_password
                })
            
            resp.raise_for_status()
            data = resp.json()
            self.token = data.get("token")
        except Exception as e:
            print(f"Warning: Failed to authenticate as admin: {e}", file=sys.stderr)

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = self.token
        return headers

    def list_collections(self):
        """List all collections."""
        resp = requests.get(f"{self.url}/api/collections", headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()

    def get_collection(self, collection_id_or_name: str):
        """Get details of a single collection."""
        resp = requests.get(f"{self.url}/api/collections/{collection_id_or_name}", headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()

    def create_collection(self, name: str, schema: List[Dict[str, Any]], type: str = 'base', **kwargs):
        """Create a new collection."""
        data = {
            "name": name,
            "type": type,
            "schema": schema, 
            "fields": schema,
            **kwargs
        }
        
        resp = requests.post(f"{self.url}/api/collections", json=data, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()

    def list_records(self, collection: str, page: int = 1, per_page: int = 30, filter_str: str = "", sort_str: str = ""):
        """List records in a collection."""
        params = {
            "page": page,
            "perPage": per_page,
            "filter": filter_str,
            "sort": sort_str
        }
        resp = requests.get(f"{self.url}/api/collections/{collection}/records", params=params, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()

    def create_record(self, collection: str, data: Dict[str, Any]):
        """Create a record in a collection."""
        resp = requests.post(f"{self.url}/api/collections/{collection}/records", json=data, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()

    def update_record(self, collection: str, record_id: str, data: Dict[str, Any]):
        """Update a record."""
        resp = requests.patch(f"{self.url}/api/collections/{collection}/records/{record_id}", json=data, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()

    def delete_record(self, collection: str, record_id: str):
        """Delete a record."""
        resp = requests.delete(f"{self.url}/api/collections/{collection}/records/{record_id}", headers=self._get_headers())
        resp.raise_for_status()
        return {"success": True}

    def create_user(self, email: str, password: str, password_confirm: str, name: str = "", collection: str = "users"):
        """Create a new user."""
        data = {
            "email": email,
            "password": password,
            "passwordConfirm": password_confirm,
            "name": name,
            "emailVisibility": True
        }
        return self.create_record(collection, data)

    def backup_database(self, name: str = ""):
        """Create a backup."""
        data = {"name": name} if name else {}
        resp = requests.post(f"{self.url}/api/backups", json=data, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()

def main():
    parser = argparse.ArgumentParser(description="PocketBase Client Skill")
    parser.add_argument("action", help="Action to perform")
    parser.add_argument("--url", default=os.environ.get("POCKETBASE_URL", DEFAULT_PB_URL), help="PocketBase URL")
    parser.add_argument("--email", default=os.environ.get("POCKETBASE_ADMIN_EMAIL"), help="Admin Email")
    parser.add_argument("--password", default=os.environ.get("POCKETBASE_ADMIN_PASSWORD"), help="Admin Password")
    
    # Common arguments
    parser.add_argument("--collection", help="Collection name or ID")
    parser.add_argument("--id", help="Record ID or Collection ID")
    parser.add_argument("--data", help="JSON data for creation/update")
    parser.add_argument("--filter", default="", help="Filter query")
    parser.add_argument("--sort", default="", help="Sort query")
    parser.add_argument("--page", type=int, default=1, help="Page number")
    parser.add_argument("--per-page", type=int, default=30, help="Items per page")
    parser.add_argument("--name", help="Name for collection/backup/etc")
    parser.add_argument("--type", default="base", help="Collection type (base, auth, view)")
    parser.add_argument("--schema", help="JSON schema/fields definition for collection")

    args = parser.parse_args()

    client = PocketBaseClient(args.url, args.email, args.password)

    try:
        if args.action == "list_collections":
            print(json.dumps(client.list_collections(), indent=2))
        
        elif args.action == "get_collection":
            if not args.collection:
                print("Error: --collection is required", file=sys.stderr)
                sys.exit(1)
            print(json.dumps(client.get_collection(args.collection), indent=2))
            
        elif args.action == "create_collection":
            if not args.name:
                print("Error: --name is required", file=sys.stderr)
                sys.exit(1)
            schema = []
            if args.schema:
                try:
                    schema = json.loads(args.schema)
                except json.JSONDecodeError:
                    print("Error: Invalid JSON for --schema", file=sys.stderr)
                    sys.exit(1)
            print(json.dumps(client.create_collection(args.name, schema, args.type), indent=2))
            
        elif args.action == "list_records":
            if not args.collection:
                print("Error: --collection is required", file=sys.stderr)
                sys.exit(1)
            print(json.dumps(client.list_records(args.collection, args.page, args.per_page, args.filter, args.sort), indent=2))
            
        elif args.action == "create_record":
            if not args.collection or not args.data:
                print("Error: --collection and --data are required", file=sys.stderr)
                sys.exit(1)
            try:
                data = json.loads(args.data)
            except json.JSONDecodeError:
                print("Error: Invalid JSON for --data", file=sys.stderr)
                sys.exit(1)
            print(json.dumps(client.create_record(args.collection, data), indent=2))
            
        elif args.action == "update_record":
            if not args.collection or not args.id or not args.data:
                print("Error: --collection, --id, and --data are required", file=sys.stderr)
                sys.exit(1)
            try:
                data = json.loads(args.data)
            except json.JSONDecodeError:
                print("Error: Invalid JSON for --data", file=sys.stderr)
                sys.exit(1)
            print(json.dumps(client.update_record(args.collection, args.id, data), indent=2))
            
        elif args.action == "delete_record":
            if not args.collection or not args.id:
                print("Error: --collection and --id are required", file=sys.stderr)
                sys.exit(1)
            print(json.dumps(client.delete_record(args.collection, args.id), indent=2))
            
        elif args.action == "create_user":
            if not args.data:
                 print("Error: --data is required (must include email, password, passwordConfirm)", file=sys.stderr)
                 sys.exit(1)
            try:
                data = json.loads(args.data)
                email = data.get("email")
                password = data.get("password")
                passwordConfirm = data.get("passwordConfirm")
                name = data.get("name", "")
                if not email or not password or not passwordConfirm:
                     print("Error: email, password, and passwordConfirm are required in data", file=sys.stderr)
                     sys.exit(1)
                print(json.dumps(client.create_user(email, password, passwordConfirm, name, args.collection or "users"), indent=2))
            except json.JSONDecodeError:
                print("Error: Invalid JSON for --data", file=sys.stderr)
                sys.exit(1)

        elif args.action == "backup_database":
            print(json.dumps(client.backup_database(args.name), indent=2))

        else:
            print(f"Unknown action: {args.action}", file=sys.stderr)
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
             print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
