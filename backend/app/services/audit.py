import json
import datetime
from ..utils.encryption import encrypt_data, decrypt_data
import os

# Config mock
ENCRYPTION_KEY = os.environ.get("AUDIT_ENCRYPTION_KEY", "your-32-byte-secret-key-base64==")

class AuditLogger:
    def log(self, case_id: str | None, action: str, actor: str, details: dict, session) -> None:
        """Encrypts details as JSON and stores in AuditLog table."""
        details_json = json.dumps(details)
        encrypted_details = encrypt_data(details_json, ENCRYPTION_KEY)
        
        # Mock database insertion
        # audit_log = AuditLog(case_id=case_id, action=action, actor=actor, details=encrypted_details, timestamp=datetime.datetime.utcnow())
        # session.add(audit_log)
        # session.commit()
        pass

    def get_logs(self, case_id: str, session) -> list:
        """Retrieves and decrypts audit logs for a case."""
        # Mock database query
        # logs = session.query(AuditLog).filter_by(case_id=case_id).all()
        logs = []
        result = []
        for log in logs:
            decrypted_details = json.loads(decrypt_data(log.details, ENCRYPTION_KEY))
            result.append({
                "action": log.action,
                "actor": log.actor,
                "timestamp": log.timestamp,
                "details": decrypted_details
            })
        return result
