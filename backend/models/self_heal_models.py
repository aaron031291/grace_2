from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from .base_models import Base

# Playbooks and steps
class Playbook(Base):
    __tablename__ = "playbooks"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    service = Column(String(128), nullable=True)
    severity = Column(String(16), nullable=True)
    risk_level = Column(String(16), default="medium", nullable=False)  # low, medium, high, critical
    autonomy_tier = Column(String(16), default="tier_1", nullable=False)  # tier_1, tier_2, tier_3, tier_4
    preconditions = Column(Text, nullable=True)  # JSON
    parameters_schema = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PlaybookStep(Base):
    __tablename__ = "playbook_steps"
    id = Column(Integer, primary_key=True)
    playbook_id = Column(Integer, ForeignKey("playbooks.id", ondelete="CASCADE"))
    step_order = Column(Integer, nullable=False)
    action = Column(String(128), nullable=False)
    args = Column(Text, nullable=True)  # JSON
    timeout_s = Column(Integer, nullable=True)
    rollback_action = Column(String(128), nullable=True)
    rollback_args = Column(Text, nullable=True)  # JSON


class VerificationCheck(Base):
    __tablename__ = "verification_checks"
    id = Column(Integer, primary_key=True)
    playbook_id = Column(Integer, ForeignKey("playbooks.id", ondelete="CASCADE"))
    step_id = Column(Integer, nullable=True)  # optional link to a specific step
    scope = Column(String(16), nullable=False, default="post_step")  # post_step | post_plan
    check_type = Column(String(64), nullable=False)  # health_endpoint | metric | script | cli_smoke
    config = Column(Text, nullable=True)  # JSON
    timeout_s = Column(Integer, nullable=True)


class PlaybookRun(Base):
    __tablename__ = "playbook_runs"
    id = Column(Integer, primary_key=True)
    playbook_id = Column(Integer, ForeignKey("playbooks.id", ondelete="SET NULL"))
    service = Column(String(128), nullable=True)
    status = Column(String(16), nullable=False, default="pending")  # pending|running|succeeded|failed|rolled_back|aborted
    requested_by = Column(String(64), nullable=True)
    approval_request_id = Column(Integer, ForeignKey("approval_requests.id", ondelete="SET NULL"), nullable=True)
    parameters = Column(Text, nullable=True)  # JSON
    diagnosis = Column(Text, nullable=True)  # JSON summary of triage reasoning
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)


class PlaybookStepRun(Base):
    __tablename__ = "playbook_step_runs"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("playbook_runs.id", ondelete="CASCADE"))
    step_id = Column(Integer, ForeignKey("playbook_steps.id", ondelete="SET NULL"), nullable=True)
    step_order = Column(Integer, nullable=True)
    status = Column(String(16), nullable=False)
    log = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)


# Incidents and events
class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True)
    service = Column(String(128), nullable=True)
    severity = Column(String(16), nullable=True)
    status = Column(String(16), nullable=False, default="open")  # open|ack|resolved|closed
    title = Column(String(256), nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class IncidentEvent(Base):
    __tablename__ = "incident_events"
    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"))
    event_type = Column(String(64), nullable=False)
    details = Column(Text, nullable=True)  # JSON/text
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Learning log
class LearningLog(Base):
    __tablename__ = "learning_log"
    id = Column(Integer, primary_key=True)
    service = Column(String(128), nullable=True)
    signal_ref = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)  # JSON
    action = Column(Text, nullable=True)  # JSON
    outcome = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
