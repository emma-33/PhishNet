from typing import Optional, List, Tuple
from sqlalchemy import desc
from app.models.audit_log import AuditLog
from app.repository.base_repository import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self):
        super().__init__(AuditLog)

    def get_by_tenant(
        self,
        tenant_id: int,
        page: int = 1,
        per_page: int = 20,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> Tuple[List[AuditLog], int]:
        """
        Get audit logs for a tenant with pagination and filtering.
        Returns a tuple of (logs, total_count).
        """
        query = self.session.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)

        total_count = query.count()

        logs = (
            query.order_by(desc(AuditLog.created_at))
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return logs, total_count
