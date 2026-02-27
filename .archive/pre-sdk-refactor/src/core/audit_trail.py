"""
Business-Specific Audit Trail for Business Infinity

NOTE: After AOS migration, this file should be refactored to extend
AgentOperatingSystem.audit_trail.AuditTrailManager base class.

See /temp/aos_migration/audit_trail.py for the generic infrastructure
that should be moved to AOS.

TODO Post-AOS Migration:
1. Import base classes from AOS: AuditTrailManager, AuditEvent, AuditSeverity
2. Keep business-specific AuditEventType enum
3. Extend AuditTrailManager to add business-specific log methods
4. Remove generic infrastructure code duplicated in AOS

Current Implementation:
Provides rigorous audit logging for:
- Boardroom agent actions and decisions
- MCP server interactions (LinkedIn, Reddit, ERPNext, etc.)
- Social media statements and business actions
- Decision-making rationales and justifications
- Both qualitative and quantitative audit data

Supports compliance requirements (SOX, GDPR, HIPAA) and audit trail integrity.
"""

import json
import logging
import hashlib
import uuid
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import threading
from contextlib import contextmanager


class AuditEventType(Enum):
    """Types of events that can be audited"""
    # Boardroom events
    BOARDROOM_DECISION = "boardroom_decision"
    AGENT_VOTE = "agent_vote"
    AGENT_PROPOSAL = "agent_proposal"
    AGENT_EVIDENCE = "agent_evidence"
    LORA_ADAPTER_SWAP = "lora_adapter_swap"
    
    # MCP interactions
    MCP_REQUEST = "mcp_request"
    MCP_RESPONSE = "mcp_response"
    MCP_ERROR = "mcp_error"
    MCP_ACCESS_DENIED = "mcp_access_denied"
    
    # Social media actions
    SOCIAL_MEDIA_POST = "social_media_post"
    SOCIAL_MEDIA_COMMENT = "social_media_comment"
    SOCIAL_MEDIA_ENGAGEMENT = "social_media_engagement"
    
    # Business system actions
    BUSINESS_TRANSACTION = "business_transaction"
    BUSINESS_DATA_ACCESS = "business_data_access"
    BUSINESS_CONFIGURATION = "business_configuration"
    
    # Conversation events
    CONVERSATION_CREATED = "conversation_created"
    CONVERSATION_SIGNED = "conversation_signed"
    A2A_COMMUNICATION = "a2a_communication"
    CONVERSATION_FLAGGED = "conversation_flagged"
    HUMAN_GATE_REQUIRED = "human_gate_required"
    
    # Security events
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    ACCESS_CONTROL = "access_control"
    PERMISSION_CHANGE = "permission_change"
    
    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_ERROR = "system_error"


class AuditSeverity(Enum):
    """Severity levels for audit events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Represents a single audit event with comprehensive metadata"""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    severity: AuditSeverity
    
    # Subject information
    subject_id: str  # Agent ID, User ID, System ID
    subject_type: str  # "agent", "user", "system"
    action: str  # What was done
    
    # Optional fields
    subject_role: Optional[str] = None  # Role or function
    target: Optional[str] = None  # What was acted upon
    mcp_server: Optional[str] = None  # Which MCP server was involved
    
    # Context and metadata
    context: Dict[str, Any] = field(default_factory=dict)
    rationale: Optional[str] = None  # Reasoning behind the action
    evidence: List[str] = field(default_factory=list)  # Supporting evidence
    
    # Quantitative data
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # Integrity protection
    checksum: Optional[str] = None
    signature: Optional[str] = None
    
    # Compliance and retention
    compliance_tags: Set[str] = field(default_factory=set)
    retention_until: Optional[datetime] = None
    
    def __post_init__(self):
        """Calculate checksum for integrity protection"""
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate SHA-256 checksum for tamper detection"""
        # Create a copy without checksum and signature for hashing
        data = asdict(self)
        data.pop('checksum', None)
        data.pop('signature', None)
        
        # Convert sets to lists for JSON serialization
        if 'compliance_tags' in data:
            data['compliance_tags'] = list(data['compliance_tags'])
        
        # Serialize to JSON string with deterministic ordering
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify the integrity of this audit event"""
        expected_checksum = self._calculate_checksum()
        return self.checksum == expected_checksum


@dataclass 
class AuditQuery:
    """Query parameters for audit log searches"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: Optional[List[AuditEventType]] = None
    subject_ids: Optional[List[str]] = None
    subject_types: Optional[List[str]] = None
    mcp_servers: Optional[List[str]] = None
    severities: Optional[List[AuditSeverity]] = None
    compliance_tags: Optional[List[str]] = None
    limit: int = 1000
    offset: int = 0


class AuditTrailManager:
    """
    Comprehensive audit trail management with integrity protection and compliance support
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path or "audit_logs")
        self.storage_path.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self._event_buffer: List[AuditEvent] = []
        self._buffer_lock = threading.Lock()
        self._buffer_max_size = 100
        
        # Compliance retention policies (in days)
        self._retention_policies = {
            "sox": 2555,  # 7 years for SOX
            "gdpr": 2555,  # Up to 7 years for GDPR  
            "hipaa": 2190,  # 6 years for HIPAA
            "default": 365  # 1 year default
        }
        
        self.logger.info("AuditTrailManager initialized")
    
    def log_event(self, 
                  event_type: AuditEventType,
                  subject_id: str,
                  subject_type: str,
                  action: str,
                  severity: AuditSeverity = AuditSeverity.MEDIUM,
                  **kwargs) -> str:
        """
        Log a single audit event
        
        Args:
            event_type: Type of event being logged
            subject_id: ID of the subject performing the action
            subject_type: Type of subject (agent, user, system)  
            action: Description of the action taken
            severity: Severity level of the event
            **kwargs: Additional event data (context, rationale, evidence, etc.)
            
        Returns:
            The event ID of the logged event
        """
        event_id = str(uuid.uuid4())
        
        # Calculate retention based on compliance tags
        compliance_tags = set(kwargs.get('compliance_tags', []))
        retention_until = self._calculate_retention(compliance_tags)
        
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            severity=severity,
            subject_id=subject_id,
            subject_type=subject_type,
            subject_role=kwargs.get('subject_role'),
            action=action,
            target=kwargs.get('target'),
            mcp_server=kwargs.get('mcp_server'),
            context=kwargs.get('context', {}),
            rationale=kwargs.get('rationale'),
            evidence=kwargs.get('evidence', []),
            metrics=kwargs.get('metrics', {}),
            compliance_tags=compliance_tags,
            retention_until=retention_until
        )
        
        self._add_to_buffer(event)
        
        # Log to standard logging as well
        log_message = f"AUDIT: {event_type.value} by {subject_id} ({subject_type}): {action}"
        if event.severity == AuditSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif event.severity == AuditSeverity.HIGH:
            self.logger.error(log_message)
        elif event.severity == AuditSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
            
        return event_id
    
    def log_boardroom_decision(self, 
                              decision_id: str,
                              decision_type: str,
                              proposed_by: str,
                              final_decision: str,
                              rationale: str,
                              votes: List[Dict[str, Any]],
                              confidence_score: float,
                              consensus_score: float) -> str:
        """Log a boardroom decision with comprehensive details"""
        return self.log_event(
            event_type=AuditEventType.BOARDROOM_DECISION,
            subject_id=decision_id,
            subject_type="boardroom",
            action=f"Made decision: {decision_type}",
            severity=AuditSeverity.HIGH,
            context={
                "decision_type": decision_type,
                "proposed_by": proposed_by,
                "final_decision": final_decision,
                "votes": votes,
                "vote_count": len(votes)
            },
            rationale=rationale,
            metrics={
                "confidence_score": confidence_score,
                "consensus_score": consensus_score
            },
            compliance_tags={"sox", "business_governance"}
        )
    
    def log_agent_vote(self,
                       voter_id: str,
                       voter_role: str, 
                       decision_id: str,
                       vote_value: float,
                       rationale: str,
                       evidence: List[str],
                       confidence: float) -> str:
        """Log an individual agent vote"""
        return self.log_event(
            event_type=AuditEventType.AGENT_VOTE,
            subject_id=voter_id,
            subject_type="agent",
            subject_role=voter_role,
            action=f"Voted on decision {decision_id}",
            target=decision_id,
            context={
                "decision_id": decision_id,
                "vote_value": vote_value
            },
            rationale=rationale,
            evidence=evidence,
            metrics={
                "vote_value": vote_value,
                "confidence": confidence
            },
            compliance_tags={"business_governance"}
        )
    
    def log_mcp_interaction(self,
                           mcp_server: str,
                           operation: str,
                           subject_id: str,
                           subject_type: str,
                           success: bool,
                           request_data: Optional[Dict[str, Any]] = None,
                           response_data: Optional[Dict[str, Any]] = None,
                           error_details: Optional[str] = None) -> str:
        """Log MCP server interactions"""
        event_type = AuditEventType.MCP_ERROR if not success else AuditEventType.MCP_REQUEST
        severity = AuditSeverity.HIGH if not success else AuditSeverity.MEDIUM
        
        context = {
            "operation": operation,
            "success": success,
            "mcp_server": mcp_server
        }
        
        if request_data:
            context["request_data"] = request_data
        if response_data:
            context["response_data"] = response_data
        if error_details:
            context["error_details"] = error_details
            
        return self.log_event(
            event_type=event_type,
            subject_id=subject_id,
            subject_type=subject_type,
            action=f"MCP {operation} on {mcp_server}",
            mcp_server=mcp_server,
            severity=severity,
            context=context,
            compliance_tags={"data_access", "integration"}
        )
    
    def log_social_media_action(self,
                               platform: str,
                               action_type: str,
                               agent_id: str,
                               content: str,
                               target_audience: Optional[str] = None,
                               engagement_metrics: Optional[Dict[str, Any]] = None) -> str:
        """Log social media actions taken by agents"""
        return self.log_event(
            event_type=AuditEventType.SOCIAL_MEDIA_POST,
            subject_id=agent_id,
            subject_type="agent",
            action=f"Social media {action_type} on {platform}",
            mcp_server=platform,
            context={
                "platform": platform,
                "action_type": action_type,
                "content_preview": content[:100] + "..." if len(content) > 100 else content,
                "target_audience": target_audience,
                "engagement_metrics": engagement_metrics or {}
            },
            compliance_tags={"social_media", "public_communication"}
        )
    
    def log_business_action(self,
                           system: str,
                           operation: str,
                           agent_id: str,
                           business_entity: str,
                           transaction_data: Optional[Dict[str, Any]] = None) -> str:
        """Log business system actions (ERP, CRM, etc.)"""
        return self.log_event(
            event_type=AuditEventType.BUSINESS_TRANSACTION,
            subject_id=agent_id,
            subject_type="agent", 
            action=f"Business {operation} in {system}",
            target=business_entity,
            mcp_server=system,
            severity=AuditSeverity.HIGH,
            context={
                "system": system,
                "operation": operation,
                "business_entity": business_entity,
                "transaction_data": transaction_data or {}
            },
            compliance_tags={"sox", "business_transaction", "financial"}
        )
    
    def query_events(self, query: AuditQuery) -> List[AuditEvent]:
        """
        Query audit events based on specified criteria
        
        Args:
            query: Query parameters
            
        Returns:
            List of matching audit events
        """
        # Flush buffer to ensure we have latest events
        self._flush_buffer()
        
        # Load and filter events from storage
        events = self._load_events_from_storage(query)
        
        return events
    
    def export_audit_trail(self, 
                          query: AuditQuery,
                          format: str = "json",
                          include_integrity_check: bool = True) -> str:
        """
        Export audit trail data for compliance or analysis
        
        Args:
            query: Query parameters to filter events
            format: Export format ("json", "csv", "xml")
            include_integrity_check: Whether to verify event integrity
            
        Returns:
            Formatted audit trail data
        """
        events = self.query_events(query)
        
        if include_integrity_check:
            # Verify integrity of all events
            integrity_results = []
            for event in events:
                is_valid = event.verify_integrity()
                integrity_results.append({
                    "event_id": event.event_id,
                    "integrity_valid": is_valid
                })
        
        if format == "json":
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "query_parameters": asdict(query),
                "total_events": len(events),
                "events": [asdict(event) for event in events]
            }
            
            if include_integrity_check:
                export_data["integrity_check"] = integrity_results
                
            return json.dumps(export_data, indent=2, default=str)
        
        elif format == "csv":
            # Implement CSV export
            raise NotImplementedError("CSV export not yet implemented")
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    @contextmanager
    def audit_context(self, 
                     operation: str,
                     subject_id: str, 
                     subject_type: str,
                     **kwargs):
        """
        Context manager for auditing operations with automatic success/failure logging
        """
        start_time = datetime.utcnow()
        context_id = str(uuid.uuid4())
        
        # Log operation start
        self.log_event(
            event_type=AuditEventType.SYSTEM_STARTUP,
            subject_id=subject_id,
            subject_type=subject_type,
            action=f"Started {operation}",
            context={"operation": operation, "context_id": context_id, **kwargs}
        )
        
        try:
            yield context_id
            
            # Log successful completion
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.log_event(
                event_type=AuditEventType.SYSTEM_STARTUP,
                subject_id=subject_id,
                subject_type=subject_type,
                action=f"Completed {operation}",
                context={"operation": operation, "context_id": context_id, **kwargs},
                metrics={"duration_seconds": duration}
            )
            
        except Exception as e:
            # Log operation failure
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                subject_id=subject_id,
                subject_type=subject_type,
                action=f"Failed {operation}",
                severity=AuditSeverity.HIGH,
                context={
                    "operation": operation, 
                    "context_id": context_id,
                    "error": str(e),
                    **kwargs
                },
                metrics={"duration_seconds": duration}
            )
            raise
    
    def _calculate_retention(self, compliance_tags: Set[str]) -> datetime:
        """Calculate retention period based on compliance requirements"""
        max_retention_days = self._retention_policies["default"]
        
        for tag in compliance_tags:
            if tag in self._retention_policies:
                max_retention_days = max(max_retention_days, self._retention_policies[tag])
        
        return datetime.utcnow() + timedelta(days=max_retention_days)
    
    def _add_to_buffer(self, event: AuditEvent):
        """Add event to buffer and flush if necessary"""
        with self._buffer_lock:
            self._event_buffer.append(event)
            
            if len(self._event_buffer) >= self._buffer_max_size:
                self._flush_buffer()
    
    def _flush_buffer(self):
        """Flush buffered events to persistent storage"""
        with self._buffer_lock:
            if not self._event_buffer:
                return
                
            # Write events to daily log file
            today = datetime.utcnow().date()
            log_file = self.storage_path / f"audit_log_{today}.jsonl"
            
            try:
                with open(log_file, 'a') as f:
                    for event in self._event_buffer:
                        # Convert to dict and handle datetime/enum serialization
                        event_dict = asdict(event)
                        event_dict['timestamp'] = event.timestamp.isoformat()
                        if event_dict['retention_until']:
                            event_dict['retention_until'] = event.retention_until.isoformat()
                        event_dict['compliance_tags'] = list(event.compliance_tags)
                        
                        # Convert enums to string values
                        event_dict['event_type'] = event.event_type.value
                        event_dict['severity'] = event.severity.value
                        
                        f.write(json.dumps(event_dict) + '\n')
                
                self.logger.debug(f"Flushed {len(self._event_buffer)} audit events to {log_file}")
                self._event_buffer.clear()
                
            except Exception as e:
                self.logger.error(f"Failed to flush audit events: {e}")
                # Keep events in buffer for retry
    
    def _load_events_from_storage(self, query: AuditQuery) -> List[AuditEvent]:
        """Load events from storage based on query parameters"""
        events = []
        
        # Determine which log files to read based on time range
        log_files = self._get_relevant_log_files(query.start_time, query.end_time)
        
        for log_file in log_files:
            if not log_file.exists():
                continue
                
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        event_dict = json.loads(line.strip())
                        
                        # Convert back to AuditEvent
                        event = self._dict_to_audit_event(event_dict)
                        
                        # Apply filters
                        if self._matches_query(event, query):
                            events.append(event)
                            
            except Exception as e:
                self.logger.error(f"Failed to load events from {log_file}: {e}")
        
        # Sort by timestamp and apply limit/offset
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[query.offset:query.offset + query.limit]
    
    def _get_relevant_log_files(self, start_time: Optional[datetime], end_time: Optional[datetime]) -> List[Path]:
        """Get list of log files that might contain events in the time range"""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(days=30)  # Default to last 30 days
        if not end_time:
            end_time = datetime.utcnow()
            
        log_files = []
        current_date = start_time.date()
        end_date = end_time.date()
        
        while current_date <= end_date:
            log_file = self.storage_path / f"audit_log_{current_date}.jsonl"
            log_files.append(log_file)
            current_date += timedelta(days=1)
            
        return log_files
    
    def _dict_to_audit_event(self, event_dict: Dict[str, Any]) -> AuditEvent:
        """Convert dictionary to AuditEvent object"""
        # Handle datetime fields
        event_dict['timestamp'] = datetime.fromisoformat(event_dict['timestamp'])
        if event_dict.get('retention_until'):
            event_dict['retention_until'] = datetime.fromisoformat(event_dict['retention_until'])
        
        # Handle enum fields
        event_dict['event_type'] = AuditEventType(event_dict['event_type'])
        event_dict['severity'] = AuditSeverity(event_dict['severity'])
        
        # Handle set fields
        event_dict['compliance_tags'] = set(event_dict.get('compliance_tags', []))
        
        return AuditEvent(**event_dict)
    
    def _matches_query(self, event: AuditEvent, query: AuditQuery) -> bool:
        """Check if an event matches query criteria"""
        # Time range filter
        if query.start_time and event.timestamp < query.start_time:
            return False
        if query.end_time and event.timestamp > query.end_time:
            return False
            
        # Event type filter
        if query.event_types and event.event_type not in query.event_types:
            return False
            
        # Subject filters
        if query.subject_ids and event.subject_id not in query.subject_ids:
            return False
        if query.subject_types and event.subject_type not in query.subject_types:
            return False
            
        # MCP server filter
        if query.mcp_servers and event.mcp_server not in query.mcp_servers:
            return False
            
        # Severity filter
        if query.severities and event.severity not in query.severities:
            return False
            
        # Compliance tags filter
        if query.compliance_tags:
            if not any(tag in event.compliance_tags for tag in query.compliance_tags):
                return False
        
        return True


# Global audit trail manager instance
_audit_manager: Optional[AuditTrailManager] = None

def get_audit_manager() -> AuditTrailManager:
    """Get the global audit trail manager instance"""
    global _audit_manager
    if _audit_manager is None:
        _audit_manager = AuditTrailManager()
    return _audit_manager


def audit_log(event_type: AuditEventType,
              subject_id: str,
              subject_type: str, 
              action: str,
              **kwargs) -> str:
    """Convenience function for logging audit events"""
    return get_audit_manager().log_event(event_type, subject_id, subject_type, action, **kwargs)