# Database connections for PSB Chatbot
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, TIMESTAMP, Boolean, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# ===============================
# DATABASE CONFIGURATION
# ===============================

# Railway provides DATABASE_URL directly when PostgreSQL is linked
# This makes deployment seamless across platforms
DATABASE_URL = os.getenv("DATABASE_URL")

# Bila DATABASE_URL mengarah ke internal Railway hostname (hanya bisa
# diakses dari dalam Railway network), fallback ke DATABASE_PUBLIC_URL
# agar script lokal (mis. generate_gd_report.py via `railway run`) bisa
# tetap terhubung via public proxy.
if DATABASE_URL and "railway.internal" in DATABASE_URL:
    DATABASE_URL = os.getenv("DATABASE_PUBLIC_URL", DATABASE_URL)

# Fallback to individual environment variables for local development
if not DATABASE_URL:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "chatbot_psb")
    DB_USER = os.getenv("DB_USER", "chatbot_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "chatbot123")
    
    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

# ===============================
# SQLALCHEMY SETUP
# ===============================

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# ===============================
# ORM MODELS
# ===============================

class UserQuestion(Base):
    """
    Store all user questions and their classification results.
    This is used for logging, analytics, and improving the model.
    """
    __tablename__ = "user_questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True)
    platform = Column(String(20), default="telegram")
    question_text = Column(Text, nullable=False)
    predicted_intent = Column(String(50), index=True)
    confidence_score = Column(Float)
    confidence_threshold = Column(Float, default=0.70)
    confidence_status = Column(String(20), default="low")
    routed_to = Column(String(20))  # llm, fallback, admin
    fallback_triggered = Column(Boolean, default=False)
    response_text = Column(Text)
    fallback_reason = Column(String(50))
    knowledge_base_used = Column(String(100))
    llm_used = Column(Boolean, default=False)
    error_message = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class ConversationLog(Base):
    """
    Store conversation history for context tracking.
    """
    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True)
    platform = Column(String(20), default="telegram")
    session_id = Column(String(100), index=True)
    message_type = Column(String(20))  # user, bot
    message_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class IntentFeedback(Base):
    """
    Store user feedback on intent classification.
    Useful for model improvement.
    """
    __tablename__ = "intent_feedback"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, index=True)  # Reference to user_questions
    user_id = Column(String(50))
    original_intent = Column(String(50))
    corrected_intent = Column(String(50))
    feedback_type = Column(String(20))  # helpful, not_helpful, wrong_intent
    feedback_text = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


# ===============================
# INITIALIZE DATABASE
# ===============================

def ensure_user_question_schema():
    """Synchronize the existing user_questions table with the current ORM schema."""
    try:
        inspector = inspect(engine)
        if "user_questions" not in inspector.get_table_names():
            Base.metadata.create_all(bind=engine)
            return

        existing_columns = {column["name"] for column in inspector.get_columns("user_questions")}
        column_definitions = {
            "confidence_threshold": "DOUBLE PRECISION",
            "confidence_status": "VARCHAR(20)",
            "routed_to": "VARCHAR(20)",
            "fallback_triggered": "BOOLEAN DEFAULT FALSE",
            "response_text": "TEXT",
            "fallback_reason": "VARCHAR(50)",
            "knowledge_base_used": "VARCHAR(100)",
            "llm_used": "BOOLEAN DEFAULT FALSE",
            "error_message": "TEXT",
        }

        with engine.begin() as conn:
            for column_name, column_type in column_definitions.items():
                if column_name not in existing_columns:
                    logger.info(f"Adding missing column {column_name} to user_questions")
                    conn.execute(text(
                        f"ALTER TABLE user_questions ADD COLUMN {column_name} {column_type}"
                    ))

        logger.info("user_questions schema is synchronized")
    except Exception:
        logger.exception("Schema migration for user_questions failed")
        raise


def init_db():
    """
    Create tables if not exist.
    Call this on application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        ensure_user_question_schema()
        logger.info("Database tables and schema are ready")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise e


# ===============================
# HELPER FUNCTIONS
# ===============================

def get_db():
    """
    Get database session.
    Use as a context manager or dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def update_user_question_response(
    question_id: int,
    response_text: str,
    fallback_triggered: bool = None,
    routed_to: str = None,
    confidence_status: str = None,
) -> bool:
    """Update the persisted response payload for a question record."""
    if question_id is None:
        return False

    session = SessionLocal()
    try:
        row = session.query(UserQuestion).filter(UserQuestion.id == question_id).first()
        if row is None:
            logger.warning(f"No user question found with id={question_id} for response update")
            return False

        if response_text is not None:
            row.response_text = response_text
        if fallback_triggered is not None:
            row.fallback_triggered = bool(fallback_triggered)
        if routed_to is not None:
            row.routed_to = routed_to
        if confidence_status is not None:
            row.confidence_status = confidence_status

        session.commit()
        logger.info(
            "Updated final response for question id=%s response_len=%s",
            question_id,
            len(response_text or ""),
        )
        return True
    except Exception:
        session.rollback()
        logger.exception("Failed to update response_text for question id=%s", question_id)
        return False
    finally:
        session.close()


def log_user_question(
    user_id: str,
    question_text: str,
    predicted_intent: str = None,
    confidence_score: float = None,
    routed_to: str = None,
    platform: str = "telegram",
    confidence_threshold: float = 0.30,
    confidence_status: str = None,
    fallback_triggered: bool = False,
    response_text: str = None,
    fallback_reason: str = None,
    knowledge_base_used: str = None,
    llm_used: bool = False,
    error_message: str = None,
    confidence_level: str = None,
) -> int:
    """Persist the complete decision trail for one user question."""
    session = SessionLocal()
    try:
        if confidence_status is None:
            if confidence_score is None:
                confidence_status = "unknown"
            elif confidence_score < 0.30:
                confidence_status = "very_low"
            elif confidence_score < 0.70:
                confidence_status = "medium"
            else:
                confidence_status = "high"

        data = UserQuestion(
            user_id=str(user_id),
            platform=platform,
            question_text=question_text,
            predicted_intent=predicted_intent,
            confidence_score=confidence_score,
            confidence_threshold=confidence_threshold,
            confidence_status=confidence_status,
            routed_to=routed_to,
            fallback_triggered=bool(fallback_triggered),
            response_text=response_text,
            fallback_reason=fallback_reason,
            knowledge_base_used=knowledge_base_used,
            llm_used=bool(llm_used),
            error_message=error_message,
        )
        session.add(data)
        session.commit()
        session.refresh(data)
        logger.info(
            f"Logged question id={data.id} user_id={user_id} "
            f"intent={predicted_intent} confidence={confidence_score} "
            f"route={routed_to} fallback={fallback_triggered} llm={llm_used}"
        )
        return data.id
    except Exception:
        session.rollback()
        # Some production databases may still be missing the newer schema columns.
        # Apply a targeted migration and retry once to avoid losing telemetry.
        try:
            ensure_user_question_schema()
            session = SessionLocal()
            data = UserQuestion(
                user_id=str(user_id),
                platform=platform,
                question_text=question_text,
                predicted_intent=predicted_intent,
                confidence_score=confidence_score,
                confidence_threshold=confidence_threshold,
                confidence_status=confidence_status,
                routed_to=routed_to,
                fallback_triggered=bool(fallback_triggered),
                response_text=response_text,
                fallback_reason=fallback_reason,
                knowledge_base_used=knowledge_base_used,
                llm_used=bool(llm_used),
                error_message=error_message,
            )
            session.add(data)
            session.commit()
            session.refresh(data)
            logger.info(
                "Logged question after schema migration id=%s user_id=%s intent=%s confidence=%s",
                data.id,
                user_id,
                predicted_intent,
                confidence_score,
            )
            return data.id
        except Exception:
            logger.exception("Error logging user question even after schema migration")
            raise
        finally:
            session.close()
    finally:
        session.close()


def get_graceful_degradation_stats(
    start_date=None,
    end_date=None,
    platform: str = None,
    user_id: str = None,
):
    """Return aggregate statistics for graceful degradation experiments."""
    session = SessionLocal()
    try:
        query = session.query(UserQuestion)
        if start_date:
            query = query.filter(UserQuestion.created_at >= start_date)
        if end_date:
            query = query.filter(UserQuestion.created_at <= end_date)
        if platform:
            query = query.filter(UserQuestion.platform == platform)
        if user_id:
            query = query.filter(UserQuestion.user_id == str(user_id))

        all_rows = query.all()
        total_queries = len(all_rows)
        high_confidence_queries = sum(1 for row in all_rows if row.confidence_score is not None and row.confidence_score >= 0.70)
        medium_confidence_queries = sum(1 for row in all_rows if row.confidence_score is not None and 0.30 <= row.confidence_score < 0.70)
        very_low_confidence_queries = sum(1 for row in all_rows if row.confidence_score is not None and row.confidence_score < 0.30)
        low_confidence_queries = medium_confidence_queries + very_low_confidence_queries
        fallback_queries = sum(1 for row in all_rows if row.fallback_triggered is True)

        fallback_percentage = (fallback_queries / total_queries * 100) if total_queries else 0.0
        normal_flow_percentage = 100.0 - fallback_percentage if total_queries else 0.0

        return {
            "total_queries": total_queries,
            "high_confidence_queries": high_confidence_queries,
            "low_confidence_queries": low_confidence_queries,
            "medium_confidence_queries": medium_confidence_queries,
            "very_low_confidence_queries": very_low_confidence_queries,
            "fallback_queries": fallback_queries,
            "fallback_percentage": round(fallback_percentage, 2),
            "normal_flow_percentage": round(normal_flow_percentage, 2),
            "threshold": 0.70,
        }
    finally:
        session.close()


def get_graceful_degradation_samples(
    start_date=None,
    end_date=None,
    platform: str = None,
    user_id: str = None,
):
    """Return samples for Bab IV table generation."""
    session = SessionLocal()
    try:
        query = session.query(UserQuestion)
        if start_date:
            query = query.filter(UserQuestion.created_at >= start_date)
        if end_date:
            query = query.filter(UserQuestion.created_at <= end_date)
        if platform:
            query = query.filter(UserQuestion.platform == platform)
        if user_id:
            query = query.filter(UserQuestion.user_id == str(user_id))

        rows = query.order_by(UserQuestion.created_at.asc()).all()
        return [
            {
                "id": row.id,
                "question": row.question_text,
                "intent": row.predicted_intent,
                "confidence": row.confidence_score,
                "confidence_status": row.confidence_status,
                "fallback": bool(row.fallback_triggered),
                "routed_to": row.routed_to,
                "response": row.response_text,
            }
            for row in rows
        ]
    finally:
        session.close()


def log_conversation(
    user_id: str,
    session_id: str,
    message_type: str,
    message_text: str,
    platform: str = "telegram"
):
    """
    Log conversation messages for history tracking.
    
    Args:
        user_id: User identifier
        session_id: Conversation session identifier
        message_type: 'user' or 'bot'
        message_text: The message content
        platform: Platform source
    """
    session = SessionLocal()
    try:
        data = ConversationLog(
            user_id=str(user_id),
            platform=platform,
            session_id=session_id,
            message_type=message_type,
            message_text=message_text
        )
        session.add(data)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error logging conversation: {str(e)}")
    finally:
        session.close()


def log_feedback(
    question_id: int,
    user_id: str,
    original_intent: str,
    feedback_type: str,
    corrected_intent: str = None,
    feedback_text: str = None
):
    """
    Log user feedback on intent classification.
    
    Args:
        question_id: ID of the original question
        user_id: User identifier
        original_intent: The intent that was predicted
        feedback_type: Type of feedback (helpful/not_helpful/wrong_intent)
        corrected_intent: If wrong_intent, the correct intent
        feedback_text: Additional feedback text
    """
    session = SessionLocal()
    try:
        data = IntentFeedback(
            question_id=question_id,
            user_id=str(user_id),
            original_intent=original_intent,
            corrected_intent=corrected_intent,
            feedback_type=feedback_type,
            feedback_text=feedback_text
        )
        session.add(data)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error logging feedback: {str(e)}")
    finally:
        session.close()


def get_user_question_stats(user_id: str = None) -> dict:
    """
    Get statistics about user questions.
    
    Args:
        user_id: Optional user ID to filter by
        
    Returns:
        dict: Statistics about questions
    """
    session = SessionLocal()
    try:
        from sqlalchemy import func
        
        query = session.query(UserQuestion)
        if user_id:
            query = query.filter(UserQuestion.user_id == str(user_id))
        
        total_questions = query.count()
        
        # Count by intent
        intent_counts = session.query(
            UserQuestion.predicted_intent,
            func.count(UserQuestion.id)
        ).group_by(UserQuestion.predicted_intent).all()
        
        return {
            "total_questions": total_questions,
            "by_intent": {intent: count for intent, count in intent_counts}
        }
    finally:
        session.close()


# ===============================
# HEALTH CHECK
# ===============================

def check_database_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        session = SessionLocal()
        session.execute(text("SELECT 1"))
        session.close()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

