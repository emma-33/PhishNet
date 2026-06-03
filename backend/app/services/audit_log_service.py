from flask import request
from app.models.audit_log import AuditLog
from app.repository.audit_log_repository import AuditLogRepository

class AuditLogService:
    def __init__(self):
        self.repository = AuditLogRepository()

    def log_action(
        self,
        tenant_id: int,
        action: str,
        user_id: int = None,
        resource_type: str = None,
        resource_id: str = None,
        details: dict = None
    ):
        """
        Create a new audit log entry.
        """
        # Try to get IP address from request
        ip_address = None
        try:
            if request:
                if request.headers.get('X-Forwarded-For'):
                    ip_address = request.headers.get('X-Forwarded-For').split(',')[0]
                else:
                    ip_address = request.remote_addr
        except (RuntimeError, AttributeError):
            # Not in a request context
            pass

        log = AuditLog(
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address
        )

        return self.repository.create(log)

# Global instance for easy use
audit_service = AuditLogService()
