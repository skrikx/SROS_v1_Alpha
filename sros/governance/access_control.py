from typing import Dict, List, Set

class AccessControl:
    """
    Role-Based Access Control (RBAC).
    """
    def __init__(self):
        self.roles: Dict[str, Set[str]] = {
            "admin": {"*"},
            "user": {"run_demo", "read_memory"},
            "viewer": {"read_memory"}
        }
        self.user_roles: Dict[str, str] = {}

    def assign_role(self, user_id: str, role: str):
        if role not in self.roles:
            raise ValueError(f"Unknown role: {role}")
        self.user_roles[user_id] = role

    def check_permission(self, user_id: str, permission: str) -> bool:
        role = self.user_roles.get(user_id, "viewer") # Default to viewer
        allowed_perms = self.roles.get(role, set())
        
        if "*" in allowed_perms:
            return True
        return permission in allowed_perms
