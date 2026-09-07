#!/usr/bin/env python3
"""
Export Training Data - PSB Chatbot

Script untuk mengexport data feedback ke format CSV yang bisa digunakan
untuk training ulang model intent classifier.

Output Files:
1. training_data_corrected.csv - Data yang sudah dikoreksi (dari feedback)
2. training_data_validated.csv - Data yang dikonfirmasi benar
3. training_data_combined.csv - Gabungan semua data yang bisa digunakan untuk training

Penggunaan:
    python export_training_data.py
    
Options:
    --output-dir <path>     Directory untuk output file (default: data/exports)
    --include-low-conf      Include low confidence questions yang belum direview
    --min-confidence <val>  Minimum confidence untuk auto-include (default: 0.95)
"""

import os
import sys
import csv
import argparse
from datetime import datetime
from typing import List, Dict, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, UserQuestion, IntentFeedback
from sqlalchemy import and_, or_

# ===============================
# CONFIGURATION
# ===============================

DEFAULT_OUTPUT_DIR = "data/exports"
HIGH_CONFIDENCE_THRESHOLD = 0.95  # Auto-include if confidence >= this

# ===============================
# EXPORT FUNCTIONS
# ===============================

def get_corrected_data() -> List[Dict]:
    """
    Get questions that have been corrected via feedback.
    Uses the corrected_intent as the label.
    
    Returns:
        List of dicts with 'text' and 'intent' keys
    """
    session = SessionLocal()
    try:
        # Query feedback with corrected intents
        results = session.query(
            UserQuestion.question_text,
            IntentFeedback.corrected_intent,
            IntentFeedback.feedback_type
        ).join(
            IntentFeedback,
            UserQuestion.id == IntentFeedback.question_id
        ).filter(
            IntentFeedback.feedback_type == "wrong_intent",
            IntentFeedback.corrected_intent.isnot(None)
        ).all()
        
        return [
            {
                "text": r[0],
                "intent": r[1],
                "source": "corrected"
            }
            for r in results
        ]
    finally:
        session.close()


def get_validated_data() -> List[Dict]:
    """
    Get questions that have been validated as correct via feedback.
    Uses the original predicted_intent as the label.
    
    Returns:
        List of dicts with 'text' and 'intent' keys
    """
    session = SessionLocal()
    try:
        # Query feedback marked as helpful
        results = session.query(
            UserQuestion.question_text,
            UserQuestion.predicted_intent
        ).join(
            IntentFeedback,
            UserQuestion.id == IntentFeedback.question_id
        ).filter(
            IntentFeedback.feedback_type == "helpful"
        ).all()
        
        return [
            {
                "text": r[0],
                "intent": r[1],
                "source": "validated"
            }
            for r in results
        ]
    finally:
        session.close()


def get_high_confidence_data(min_confidence: float = HIGH_CONFIDENCE_THRESHOLD) -> List[Dict]:
    """
    Get questions with high confidence that haven't been reviewed.
    These are likely correct and can be auto-included in training.
    
    Args:
        min_confidence: Minimum confidence threshold
        
    Returns:
        List of dicts with 'text' and 'intent' keys
    """
    session = SessionLocal()
    try:
        # Get IDs of reviewed questions using proper select()
        from sqlalchemy import select
        reviewed_ids = select(IntentFeedback.question_id).scalar_subquery()
        
        # Query high-confidence unreviewed questions
        results = session.query(
            UserQuestion.question_text,
            UserQuestion.predicted_intent,
            UserQuestion.confidence_score
        ).filter(
            UserQuestion.confidence_score >= min_confidence,
            ~UserQuestion.id.in_(reviewed_ids)
        ).all()
        
        return [
            {
                "text": r[0],
                "intent": r[1],
                "source": f"high_conf_{r[2]:.2f}"
            }
            for r in results
        ]
    finally:
        session.close()


def get_all_feedback_data() -> List[Dict]:
    """
    Get all feedback entries for analysis.
    
    Returns:
        List of feedback records
    """
    session = SessionLocal()
    try:
        results = session.query(
            IntentFeedback.id,
            IntentFeedback.question_id,
            UserQuestion.question_text,
            IntentFeedback.original_intent,
            IntentFeedback.corrected_intent,
            IntentFeedback.feedback_type,
            IntentFeedback.feedback_text,
            IntentFeedback.created_at
        ).join(
            UserQuestion,
            UserQuestion.id == IntentFeedback.question_id
        ).order_by(
            IntentFeedback.created_at.desc()
        ).all()
        
        return [
            {
                "feedback_id": r[0],
                "question_id": r[1],
                "question_text": r[2],
                "original_intent": r[3],
                "corrected_intent": r[4],
                "feedback_type": r[5],
                "feedback_text": r[6],
                "created_at": r[7].isoformat() if r[7] else None
            }
            for r in results
        ]
    finally:
        session.close()


def export_to_csv(data: List[Dict], filepath: str, fieldnames: List[str] = None):
    """
    Export data to CSV file.
    
    Args:
        data: List of dictionaries to export
        filepath: Output file path
        fieldnames: CSV column names (auto-detect if None)
    """
    if not data:
        print(f"⚠ No data to export for {filepath}")
        return 0
    
    if fieldnames is None:
        fieldnames = list(data[0].keys())
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✓ Exported {len(data)} records to {filepath}")
    return len(data)


def get_export_stats(output_dir: str) -> Dict:
    """Get statistics about the exported data."""
    session = SessionLocal()
    try:
        total_questions = session.query(UserQuestion).count()
        total_feedback = session.query(IntentFeedback).count()
        
        correction_count = session.query(IntentFeedback).filter(
            IntentFeedback.feedback_type == "wrong_intent"
        ).count()
        
        validation_count = session.query(IntentFeedback).filter(
            IntentFeedback.feedback_type == "helpful"
        ).count()
        
        return {
            "total_questions": total_questions,
            "total_feedback": total_feedback,
            "corrections": correction_count,
            "validations": validation_count,
            "output_dir": output_dir
        }
    finally:
        session.close()


# ===============================
# MAIN EXPORT FUNCTION
# ===============================

def run_export(output_dir: str = DEFAULT_OUTPUT_DIR, 
               include_high_conf: bool = True,
               min_confidence: float = HIGH_CONFIDENCE_THRESHOLD):
    """
    Run the complete export process.
    
    Args:
        output_dir: Directory for output files
        include_high_conf: Whether to include high-confidence unreviewed data
        min_confidence: Minimum confidence for auto-include
    """
    print("\n" + "="*60)
    print("  PSB Chatbot - Export Training Data")
    print("="*60 + "\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Export corrected data
    print("📥 Fetching corrected data...")
    corrected_data = get_corrected_data()
    corrected_file = os.path.join(output_dir, f"training_data_corrected_{timestamp}.csv")
    
    # 2. Export validated data
    print("📥 Fetching validated data...")
    validated_data = get_validated_data()
    validated_file = os.path.join(output_dir, f"training_data_validated_{timestamp}.csv")
    
    # 3. Export high-confidence data if requested
    high_conf_data = []
    if include_high_conf:
        print(f"📥 Fetching high-confidence data (>= {min_confidence:.0%})...")
        high_conf_data = get_high_confidence_data(min_confidence)
    
    # 4. Create REVIEWED training data (validated + corrected)
    # This is what the user asked for - all reviewed data combined
    reviewed_data = []
    
    # Add validated data (label was already correct - marked as "helpful")
    for item in validated_data:
        reviewed_data.append({
            "text": item["text"],
            "intent": item["intent"],
            "source": "validated"  # Label asli sudah benar
        })
    
    # Add corrected data (label was wrong - fixed by admin)
    for item in corrected_data:
        reviewed_data.append({
            "text": item["text"],
            "intent": item["intent"],
            "source": "corrected"  # Label sudah dikoreksi
        })
    
    reviewed_file = os.path.join(output_dir, f"training_data_reviewed_{timestamp}.csv")
    
    # 5. Create combined training data (reviewed + high-confidence)
    combined_data = []
    
    for item in reviewed_data:
        combined_data.append({
            "text": item["text"],
            "intent": item["intent"]
        })
    
    # Add high-confidence data (auto-included, not manually reviewed)
    for item in high_conf_data:
        combined_data.append({
            "text": item["text"],
            "intent": item["intent"]
        })
    
    combined_file = os.path.join(output_dir, f"training_data_combined_{timestamp}.csv")
    
    # 6. Export all feedback for analysis
    print("📥 Fetching all feedback records...")
    all_feedback = get_all_feedback_data()
    feedback_file = os.path.join(output_dir, f"all_feedback_{timestamp}.csv")
    
    # Perform exports
    print("\n📤 Exporting files...\n")
    
    total_exported = 0
    
    # Export reviewed data (validated + corrected) - WITH source column
    if reviewed_data:
        total_exported += export_to_csv(
            reviewed_data, 
            reviewed_file,
            ["text", "intent", "source"]
        )
        
        # Also create a "latest" reviewed file
        latest_reviewed_file = os.path.join(output_dir, "training_data_reviewed_latest.csv")
        export_to_csv(reviewed_data, latest_reviewed_file, ["text", "intent", "source"])
    
    # Export combined data for training (without source column)
    if combined_data:
        export_to_csv(
            combined_data,
            combined_file,
            ["text", "intent"]
        )
        
        # Also create a "latest" file for easy access
        latest_file = os.path.join(output_dir, "training_data_latest.csv")
        export_to_csv(combined_data, latest_file, ["text", "intent"])
    
    if all_feedback:
        export_to_csv(
            all_feedback,
            feedback_file,
            ["feedback_id", "question_id", "question_text", 
             "original_intent", "corrected_intent", "feedback_type",
             "feedback_text", "created_at"]
        )

    
    # Print summary
    print("\n" + "="*60)
    print("  EXPORT SUMMARY")
    print("="*60)
    print(f"""
📊 Statistics:
   ┌─────────────────────────────────────────────┐
   │ REVIEWED DATA (Manual Labeling)             │
   ├─────────────────────────────────────────────┤
   │  ✓ Validated (label benar)  : {len(validated_data):4}          │
   │  ✎ Corrected (label diubah) : {len(corrected_data):4}          │
   │  ─────────────────────────────────────      │
   │  Total reviewed             : {len(reviewed_data):4}          │
   └─────────────────────────────────────────────┘
   
   Auto high-confidence (>= 95%) : {len(high_conf_data)}
   Combined (untuk training)     : {len(combined_data)}
   Total feedback records        : {len(all_feedback)}

📁 Output Directory: {output_dir}

📄 Files Created:
   ┌─────────────────────────────────────────────────────────────┐
   │ training_data_reviewed_{timestamp}.csv                     │
   │   → Gabungan validated + corrected (dengan kolom source)   │
   │                                                             │
   │ training_data_reviewed_latest.csv                           │
   │   → Versi terbaru dari reviewed data                        │
   │                                                             │
   │ training_data_combined_{timestamp}.csv                     │
   │   → Data untuk training (reviewed + high-conf)             │
   │                                                             │
   │ training_data_latest.csv                                    │
   │   → Versi terbaru untuk training                           │
   │                                                             │
   │ all_feedback_{timestamp}.csv                               │
   │   → Semua feedback untuk analisis                          │
   └─────────────────────────────────────────────────────────────┘
""")
    
    if reviewed_data:
        print(f"""
💡 File yang Anda butuhkan:
   
   📌 training_data_reviewed_latest.csv
      - Berisi data yang sudah Anda review
      - Kolom: text, intent, source
      - source = 'validated' → label asli sudah benar
      - source = 'corrected' → label sudah dikoreksi
   
   📌 training_data_latest.csv
      - Siap untuk training (tanpa kolom source)
      - Kolom: text, intent
""")
    else:
        print("""
⚠ Belum ada data yang direview!
   Silakan review pertanyaan terlebih dahulu:
   python admin_labeling.py
""")
    

    return {
        "corrected": len(corrected_data),
        "validated": len(validated_data),
        "high_conf": len(high_conf_data),
        "combined": len(combined_data),
        "feedback": len(all_feedback)
    }


# ===============================
# CLI
# ===============================

def main():
    parser = argparse.ArgumentParser(
        description="Export training data from feedback",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python export_training_data.py
  python export_training_data.py --output-dir ./my_exports
  python export_training_data.py --min-confidence 0.9
        """
    )
    
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )
    
    parser.add_argument(
        "--no-high-conf",
        action="store_true",
        help="Exclude high-confidence unreviewed questions"
    )
    
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=HIGH_CONFIDENCE_THRESHOLD,
        help=f"Minimum confidence for auto-include (default: {HIGH_CONFIDENCE_THRESHOLD})"
    )
    
    args = parser.parse_args()
    
    run_export(
        output_dir=args.output_dir,
        include_high_conf=not args.no_high_conf,
        min_confidence=args.min_confidence
    )


if __name__ == "__main__":
    main()
