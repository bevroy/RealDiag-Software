"""
Role-Based Access Control (RBAC) Service

Implements role and permission management for RealDiag.
"""

from enum import Enum
from typing import List, Set, Optional, Callable
from functools import wraps
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """User roles in the system"""
    ADMIN = "admin"  # Full system access
    PROVIDER = "provider"  # Healthcare provider (can view/edit patient data)
    USER = "user"  # Regular user (limited access)
    GUEST = "guest"  # Unauthenticated user (read-only public data)


class Permission(str, Enum):
    """Granular permissions"""
    # User management
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    
    # Patient data
    PATIENT_READ = "patient:read"
    PATIENT_WRITE = "patient:write"
    PATIENT_DELETE = "patient:delete"
    
    # Diagnostic data
    DIAGNOSIS_READ = "diagnosis:read"
    DIAGNOSIS_WRITE = "diagnosis:write"
    DIAGNOSIS_EXPORT = "diagnosis:export"
    
    # System management
    SYSTEM_CONFIG = "system:config"
    SYSTEM_LOGS = "system:logs"
    SYSTEM_BACKUP = "system:backup"
    
    # API access
    API_KEY_CREATE = "api:key:create"
    API_KEY_DELETE = "api:key:delete"
    
    # Integration
    EHR_READ = "ehr:read"
    EHR_WRITE = "ehr:write"
    
    # Subscription
    SUBSCRIPTION_MANAGE = "subscription:manage"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # Admin has all permissions
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.PATIENT_READ,
        Permission.PATIENT_WRITE,
        Permission.PATIENT_DELETE,
        Permission.DIAGNOSIS_READ,
        Permission.DIAGNOSIS_WRITE,
        Permission.DIAGNOSIS_EXPORT,
        Permission.SYSTEM_CONFIG,
        Permission.SYSTEM_LOGS,
        Permission.SYSTEM_BACKUP,
        Permission.API_KEY_CREATE,
        Permission.API_KEY_DELETE,
        Permission.EHR_READ,
        Permission.EHR_WRITE,
        Permission.SUBSCRIPTION_MANAGE,
    },
    
    Role.PROVIDER: {
        # Provider can manage patient data and diagnostics
        Permission.USER_READ,
        Permission.PATIENT_READ,
        Permission.PATIENT_WRITE,
        Permission.DIAGNOSIS_READ,
        Permission.DIAGNOSIS_WRITE,
        Permission.DIAGNOSIS_EXPORT,
        Permission.EHR_READ,
        Permission.EHR_WRITE,
    },
    
    Role.USER: {
        # Regular user can read their own data
        Permission.USER_READ,
        Permission.DIAGNOSIS_READ,
        Permission.DIAGNOSIS_EXPORT,
    },
    
    Role.GUEST: {
        # Guest can only read public diagnostic rules
        Permission.DIAGNOSIS_READ,
    }
}


class RBACService:
    """
    Service for role-based access control.
    """
    
    def __init__(self):
        self.role_permissions = ROLE_PERMISSIONS
    
    def get_permissions(self, role: Role) -> Set[Permission]:
        """
        Get all permissions for a role.
        
        Args:
            role: User role
            
        Returns:
            Set of permissions
        """
        return self.role_permissions.get(role, set())
    
    def has_permission(self, role: Role, permission: Permission) -> bool:
        """
        Check if a role has a specific permission.
        
        Args:
            role: User role
            permission: Required permission
            
        Returns:
            True if role has permission
        """
        permissions = self.get_permissions(role)
        return permission in permissions
    
    def has_any_permission(self, role: Role, permissions: List[Permission]) -> bool:
        """
        Check if role has any of the given permissions.
        
        Args:
            role: User role
            permissions: List of permissions to check
            
        Returns:
            True if role has at least one permission
        """
        role_permissions = self.get_permissions(role)
        return any(p in role_permissions for p in permissions)
    
    def has_all_permissions(self, role: Role, permissions: List[Permission]) -> bool:
        """
        Check if role has all of the given permissions.
        
        Args:
            role: User role
            permissions: List of permissions to check
            
        Returns:
            True if role has all permissions
        """
        role_permissions = self.get_permissions(role)
        return all(p in role_permissions for p in permissions)
    
    def get_user_role(self, user: dict) -> Role:
        """
        Get role from user object.
        
        Args:
            user: User dictionary
            
        Returns:
            User's role
        """
        role_str = user.get('role', 'user')
        try:
            return Role(role_str)
        except ValueError:
            logger.warning(f"Invalid role '{role_str}', defaulting to USER")
            return Role.USER
    
    def check_permission(self, user: dict, permission: Permission) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user: User dictionary
            permission: Required permission
            
        Returns:
            True if user has permission
        """
        role = self.get_user_role(user)
        return self.has_permission(role, permission)
    
    def require_permission(self, user: dict, permission: Permission):
        """
        Raise exception if user doesn't have permission.
        
        Args:
            user: User dictionary
            permission: Required permission
            
        Raises:
            HTTPException: If permission denied
        """
        if not self.check_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value} required"
            )
    
    def require_role(self, user: dict, required_role: Role):
        """
        Raise exception if user doesn't have required role.
        
        Args:
            user: User dictionary
            required_role: Required role
            
        Raises:
            HTTPException: If role mismatch
        """
        role = self.get_user_role(user)
        if role != required_role and role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {required_role.value} required"
            )


# Global RBAC service instance
_rbac_service = None

def get_rbac_service() -> RBACService:
    """Get global RBAC service instance (singleton)"""
    global _rbac_service
    if _rbac_service is None:
        _rbac_service = RBACService()
    return _rbac_service


# Decorator for permission-based endpoint protection
def require_permission(permission: Permission):
    """
    Decorator to require specific permission for an endpoint.
    
    Usage:
        @router.get("/admin/users")
        @require_permission(Permission.USER_READ)
        async def list_users(current_user: dict = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: dict = None, **kwargs):
            if current_user is None:
                # Try to extract from kwargs
                current_user = kwargs.get('current_user')
            
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            rbac = get_rbac_service()
            rbac.require_permission(current_user, permission)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: Role):
    """
    Decorator to require specific role for an endpoint.
    
    Usage:
        @router.delete("/admin/user/{user_id}")
        @require_role(Role.ADMIN)
        async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: dict = None, **kwargs):
            if current_user is None:
                current_user = kwargs.get('current_user')
            
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            rbac = get_rbac_service()
            rbac.require_role(current_user, role)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


if __name__ == '__main__':
    # Test RBAC functionality
    rbac = RBACService()
    
    print("=== Role Permissions ===")
    for role in Role:
        perms = rbac.get_permissions(role)
        print(f"\n{role.value.upper()}:")
        for perm in sorted(perms, key=lambda p: p.value):
            print(f"  - {perm.value}")
    
    print("\n=== Permission Checks ===")
    print(f"Admin can delete users: {rbac.has_permission(Role.ADMIN, Permission.USER_DELETE)}")
    print(f"Provider can delete users: {rbac.has_permission(Role.PROVIDER, Permission.USER_DELETE)}")
    print(f"User can read diagnoses: {rbac.has_permission(Role.USER, Permission.DIAGNOSIS_READ)}")
    print(f"Guest can write patients: {rbac.has_permission(Role.GUEST, Permission.PATIENT_WRITE)}")
