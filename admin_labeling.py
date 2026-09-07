#!/usr/bin/env python3
"""
Admin Labeling Tool - PSB Chatbot

Tool interaktif untuk admin melakukan:
1. Review pertanyaan dengan confidence rendah
2. Koreksi intent yang salah
3. Melihat statistik pertanyaan

Penggunaan:
    python admin_labeling.py

Commands:
    review     - Review pertanyaan dengan confidence rendah
    stats      - Lihat statistik pertanyaan
    export     - Export data feedback ke CSV
    intents    - Lihat daftar intent yang tersedia
    search     - Cari pertanyaan berdasarkan keyword
    help       - Tampilkan bantuan
    quit       - Keluar
"""

import os
import sys
from datetime import datetime
from typing import List, Optional, Tuple
from tabulate import tabulate
from colorama import init, Fore, Style, Back

# Initialize colorama for colored terminal output
init()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import (
    SessionLocal, 
    UserQuestion, 
    IntentFeedback,
    log_feedback,
    init_db
)
from intent_classifier import get_intent_classifier

# ===============================
# CONFIGURATION
# ===============================

# Threshold for "low confidence" questions to review
LOW_CONFIDENCE_THRESHOLD = 0.7

# Number of questions to show per page
PAGE_SIZE = 10

# ===============================
# HELPER FUNCTIONS
# ===============================

def print_header(text: str):
    """Print a styled header."""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}  {text}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")


def print_error(text: str):
    """Print error message."""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")


def print_info(text: str):
    """Print info message."""
    print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")


def get_confidence_color(confidence: float) -> str:
    """Get color based on confidence level."""
    if confidence is None:
        return Fore.WHITE
    if confidence >= 0.8:
        return Fore.GREEN
    elif confidence >= 0.5:
        return Fore.YELLOW
    else:
        return Fore.RED


def format_confidence(confidence: float) -> str:
    """Format confidence score with color."""
    if confidence is None:
        return f"{Fore.WHITE}N/A{Style.RESET_ALL}"
    color = get_confidence_color(confidence)
    return f"{color}{confidence:.2%}{Style.RESET_ALL}"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


# ===============================
# DATABASE QUERIES
# ===============================

def get_low_confidence_questions(
    threshold: float = LOW_CONFIDENCE_THRESHOLD,
    limit: int = PAGE_SIZE,
    offset: int = 0,
    only_unreviewed: bool = True
) -> Tuple[List[UserQuestion], int]:
    """
    Get questions with low confidence scores.
    
    Args:
        threshold: Confidence threshold (questions below this are returned)
        limit: Maximum number of results
        offset: Pagination offset
        only_unreviewed: If True, exclude already reviewed questions
        
    Returns:
        Tuple of (questions list, total count)
    """
    session = SessionLocal()
    try:
        query = session.query(UserQuestion).filter(
            UserQuestion.confidence_score < threshold
        )
        
        if only_unreviewed:
            # Get IDs of already reviewed questions using proper select()
            from sqlalchemy import select
            reviewed_ids = select(IntentFeedback.question_id).scalar_subquery()
            query = query.filter(~UserQuestion.id.in_(reviewed_ids))
        
        total = query.count()
        questions = query.order_by(
            UserQuestion.confidence_score.asc(),
            UserQuestion.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return questions, total
    finally:
        session.close()


def get_question_by_id(question_id: int) -> Optional[UserQuestion]:
    """Get a specific question by ID."""
    session = SessionLocal()
    try:
        return session.query(UserQuestion).filter(
            UserQuestion.id == question_id
        ).first()
    finally:
        session.close()


def search_questions(keyword: str, limit: int = 20) -> List[UserQuestion]:
    """Search questions by keyword."""
    session = SessionLocal()
    try:
        return session.query(UserQuestion).filter(
            UserQuestion.question_text.ilike(f"%{keyword}%")
        ).order_by(
            UserQuestion.created_at.desc()
        ).limit(limit).all()
    finally:
        session.close()


def get_question_stats() -> dict:
    """Get statistics about questions."""
    session = SessionLocal()
    try:
        from sqlalchemy import func
        
        total_questions = session.query(UserQuestion).count()
        
        low_confidence = session.query(UserQuestion).filter(
            UserQuestion.confidence_score < LOW_CONFIDENCE_THRESHOLD
        ).count()
        
        # Get already reviewed count
        reviewed = session.query(IntentFeedback).count()
        
        # Count by intent
        intent_counts = session.query(
            UserQuestion.predicted_intent,
            func.count(UserQuestion.id),
            func.avg(UserQuestion.confidence_score)
        ).group_by(UserQuestion.predicted_intent).all()
        
        # Count by routed_to
        route_counts = session.query(
            UserQuestion.routed_to,
            func.count(UserQuestion.id)
        ).group_by(UserQuestion.routed_to).all()
        
        # Feedback types count
        feedback_counts = session.query(
            IntentFeedback.feedback_type,
            func.count(IntentFeedback.id)
        ).group_by(IntentFeedback.feedback_type).all()
        
        return {
            "total_questions": total_questions,
            "low_confidence": low_confidence,
            "reviewed": reviewed,
            "pending_review": low_confidence - reviewed if low_confidence > reviewed else 0,
            "by_intent": intent_counts,
            "by_route": route_counts,
            "by_feedback": feedback_counts
        }
    finally:
        session.close()


def get_feedback_for_question(question_id: int) -> Optional[IntentFeedback]:
    """Get feedback for a specific question if exists."""
    session = SessionLocal()
    try:
        return session.query(IntentFeedback).filter(
            IntentFeedback.question_id == question_id
        ).first()
    finally:
        session.close()


# ===============================
# COMMAND HANDLERS
# ===============================

def show_available_intents():
    """Show all available intents."""
    print_header("DAFTAR INTENT")
    
    try:
        classifier = get_intent_classifier()
        intents = classifier.get_all_intents()
        
        if not intents:
            print_warning("Tidak ada intent yang tersedia (model mungkin belum dilatih)")
            return
        
        print(f"Total: {len(intents)} intent\n")
        
        for i, intent in enumerate(intents, 1):
            print(f"  {Fore.CYAN}{i:2}.{Style.RESET_ALL} {intent}")
        
        print()
    except Exception as e:
        print_error(f"Gagal memuat intent: {str(e)}")


def show_stats():
    """Show question statistics."""
    print_header("STATISTIK PERTANYAAN")
    
    try:
        stats = get_question_stats()
        
        # General stats
        print(f"{Fore.CYAN}📊 Ringkasan:{Style.RESET_ALL}")
        print(f"   Total pertanyaan     : {stats['total_questions']}")
        print(f"   Confidence rendah    : {stats['low_confidence']}")
        print(f"   Sudah direview       : {stats['reviewed']}")
        print(f"   Menunggu review      : {Fore.YELLOW}{stats['pending_review']}{Style.RESET_ALL}")
        
        # By intent
        print(f"\n{Fore.CYAN}📁 Per Intent:{Style.RESET_ALL}")
        if stats['by_intent']:
            table_data = []
            for intent, count, avg_conf in stats['by_intent']:
                avg_conf_str = f"{avg_conf:.2%}" if avg_conf else "N/A"
                table_data.append([intent or "N/A", count, avg_conf_str])
            
            print(tabulate(
                table_data,
                headers=["Intent", "Jumlah", "Avg Confidence"],
                tablefmt="simple"
            ))
        else:
            print("   (tidak ada data)")
        
        # By route
        print(f"\n{Fore.CYAN}🔀 Per Route:{Style.RESET_ALL}")
        if stats['by_route']:
            for route, count in stats['by_route']:
                print(f"   {route or 'N/A':15} : {count}")
        else:
            print("   (tidak ada data)")
        
        # By feedback type
        print(f"\n{Fore.CYAN}📝 Feedback:{Style.RESET_ALL}")
        if stats['by_feedback']:
            for fb_type, count in stats['by_feedback']:
                emoji = "👍" if fb_type == "helpful" else "👎" if fb_type == "not_helpful" else "❌"
                print(f"   {emoji} {fb_type or 'N/A':15} : {count}")
        else:
            print("   (belum ada feedback)")
        
        print()
    except Exception as e:
        print_error(f"Gagal memuat statistik: {str(e)}")


def review_questions():
    """Interactive review of low-confidence questions."""
    print_header("REVIEW PERTANYAAN (Confidence Rendah)")
    
    try:
        # Get available intents for correction
        classifier = get_intent_classifier()
        available_intents = classifier.get_all_intents()
        
        offset = 0
        while True:
            questions, total = get_low_confidence_questions(
                threshold=LOW_CONFIDENCE_THRESHOLD,
                limit=PAGE_SIZE,
                offset=offset,
                only_unreviewed=True
            )
            
            if not questions:
                print_success("Tidak ada pertanyaan yang perlu direview! 🎉")
                break
            
            print(f"📋 Menampilkan {offset + 1}-{offset + len(questions)} dari {total} pertanyaan\n")
            
            # Display questions in table
            table_data = []
            for q in questions:
                table_data.append([
                    q.id,
                    truncate_text(q.question_text, 40),
                    q.predicted_intent or "N/A",
                    format_confidence(q.confidence_score),
                    q.routed_to or "N/A"
                ])
            
            print(tabulate(
                table_data,
                headers=["ID", "Pertanyaan", "Intent", "Confidence", "Route"],
                tablefmt="simple"
            ))
            
            print(f"\n{Fore.CYAN}Commands:{Style.RESET_ALL}")
            print("  [ID]     - Review pertanyaan dengan ID tersebut")
            print("  n        - Halaman berikutnya")
            print("  p        - Halaman sebelumnya")
            print("  q        - Kembali ke menu utama")
            
            choice = input(f"\n{Fore.GREEN}Pilihan: {Style.RESET_ALL}").strip().lower()
            
            if choice == 'q':
                break
            elif choice == 'n':
                if offset + PAGE_SIZE < total:
                    offset += PAGE_SIZE
                else:
                    print_warning("Sudah di halaman terakhir")
            elif choice == 'p':
                if offset >= PAGE_SIZE:
                    offset -= PAGE_SIZE
                else:
                    print_warning("Sudah di halaman pertama")
            elif choice.isdigit():
                question_id = int(choice)
                review_single_question(question_id, available_intents)
            else:
                print_warning("Pilihan tidak valid")
                
    except Exception as e:
        print_error(f"Error saat review: {str(e)}")


def review_single_question(question_id: int, available_intents: List[str]):
    """Review and potentially correct a single question."""
    question = get_question_by_id(question_id)
    
    if not question:
        print_error(f"Pertanyaan dengan ID {question_id} tidak ditemukan")
        return
    
    # Check if already reviewed
    existing_feedback = get_feedback_for_question(question_id)
    
    print(f"\n{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📝 REVIEW PERTANYAAN #{question_id}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}Pertanyaan:{Style.RESET_ALL}")
    print(f"  \"{question.question_text}\"")
    
    print(f"\n{Fore.WHITE}Prediksi Sistem:{Style.RESET_ALL}")
    print(f"  Intent     : {Fore.YELLOW}{question.predicted_intent}{Style.RESET_ALL}")
    print(f"  Confidence : {format_confidence(question.confidence_score)}")
    print(f"  Route      : {question.routed_to}")
    print(f"  Waktu      : {question.created_at}")
    
    if existing_feedback:
        print(f"\n{Fore.YELLOW}⚠ Pertanyaan ini sudah direview:{Style.RESET_ALL}")
        print(f"  Feedback      : {existing_feedback.feedback_type}")
        print(f"  Koreksi       : {existing_feedback.corrected_intent or 'N/A'}")
        print(f"  Catatan       : {existing_feedback.feedback_text or 'N/A'}")
        
        confirm = input(f"\nLanjut review ulang? (y/n): ").strip().lower()
        if confirm != 'y':
            return
    
    print(f"\n{Fore.CYAN}Intent yang tersedia:{Style.RESET_ALL}")
    for i, intent in enumerate(available_intents, 1):
        marker = "→" if intent == question.predicted_intent else " "
        print(f"  {marker} {i}. {intent}")
    
    print(f"\n{Fore.CYAN}Pilihan:{Style.RESET_ALL}")
    print("  1. ✓ Intent sudah benar (helpful)")
    print("  2. ✗ Intent salah, koreksi")
    print("  3. ? Tidak yakin (skip)")
    print("  0. Kembali")
    
    choice = input(f"\n{Fore.GREEN}Pilihan (0-3): {Style.RESET_ALL}").strip()
    
    if choice == '0':
        return
    elif choice == '1':
        # Intent is correct
        log_feedback(
            question_id=question_id,
            user_id="admin",
            original_intent=question.predicted_intent,
            feedback_type="helpful",
            feedback_text="Intent sudah benar"
        )
        print_success("Feedback 'helpful' disimpan!")
        
    elif choice == '2':
        # Wrong intent - need correction
        print(f"\n{Fore.CYAN}Pilih intent yang benar (1-{len(available_intents)}):{Style.RESET_ALL}")
        intent_choice = input("Nomor intent: ").strip()
        
        if intent_choice.isdigit() and 1 <= int(intent_choice) <= len(available_intents):
            corrected_intent = available_intents[int(intent_choice) - 1]
            
            feedback_text = input("Catatan (opsional): ").strip()
            
            log_feedback(
                question_id=question_id,
                user_id="admin",
                original_intent=question.predicted_intent,
                feedback_type="wrong_intent",
                corrected_intent=corrected_intent,
                feedback_text=feedback_text if feedback_text else None
            )
            print_success(f"Intent dikoreksi ke '{corrected_intent}'!")
        else:
            print_error("Pilihan tidak valid")
            
    elif choice == '3':
        # Uncertain - skip
        log_feedback(
            question_id=question_id,
            user_id="admin",
            original_intent=question.predicted_intent,
            feedback_type="not_helpful",
            feedback_text="Admin tidak yakin dengan intent"
        )
        print_info("Pertanyaan diskip, ditandai untuk review lanjutan")
    else:
        print_warning("Pilihan tidak valid")


def search_and_review():
    """Search questions by keyword."""
    print_header("CARI PERTANYAAN")
    
    keyword = input("Masukkan keyword: ").strip()
    
    if not keyword:
        print_warning("Keyword tidak boleh kosong")
        return
    
    questions = search_questions(keyword)
    
    if not questions:
        print_info(f"Tidak ditemukan pertanyaan dengan keyword '{keyword}'")
        return
    
    print(f"\n📋 Ditemukan {len(questions)} pertanyaan:\n")
    
    table_data = []
    for q in questions:
        table_data.append([
            q.id,
            truncate_text(q.question_text, 50),
            q.predicted_intent or "N/A",
            format_confidence(q.confidence_score)
        ])
    
    print(tabulate(
        table_data,
        headers=["ID", "Pertanyaan", "Intent", "Confidence"],
        tablefmt="simple"
    ))
    
    print(f"\n{Fore.CYAN}Masukkan ID untuk review, atau 'q' untuk kembali:{Style.RESET_ALL}")
    choice = input("ID: ").strip()
    
    if choice.isdigit():
        classifier = get_intent_classifier()
        review_single_question(int(choice), classifier.get_all_intents())


def export_data():
    """Export feedback data to CSV."""
    print_header("EXPORT DATA")
    
    print("Menjalankan export script...")
    os.system("python export_training_data.py")


def show_help():
    """Show help information."""
    print_header("BANTUAN")
    
    print(f"""
{Fore.CYAN}Admin Labeling Tool{Style.RESET_ALL} adalah tool untuk membantu admin
dalam melakukan pelabelan intent secara manual.

{Fore.CYAN}Commands:{Style.RESET_ALL}
  review   - Review pertanyaan dengan confidence rendah
  stats    - Lihat statistik pertanyaan dan feedback
  export   - Export data feedback ke CSV untuk training ulang
  intents  - Lihat daftar intent yang tersedia
  search   - Cari pertanyaan berdasarkan keyword
  help     - Tampilkan bantuan ini
  quit     - Keluar dari program

{Fore.CYAN}Workflow Pelabelan:{Style.RESET_ALL}
  1. Gunakan 'stats' untuk melihat berapa pertanyaan perlu direview
  2. Gunakan 'review' untuk mulai mereview pertanyaan satu per satu
  3. Untuk setiap pertanyaan, tentukan apakah intent sudah benar atau salah
  4. Jika salah, pilih intent yang benar dari daftar
  5. Setelah selesai, gunakan 'export' untuk menghasilkan data training baru

{Fore.CYAN}Tips:{Style.RESET_ALL}
  - Pertanyaan ditampilkan dari confidence terendah
  - Fokus pada pertanyaan dengan confidence < {LOW_CONFIDENCE_THRESHOLD:.0%}
  - Konsisten dalam memilih intent untuk kasus serupa
""")


# ===============================
# MAIN LOOP
# ===============================

def main():
    """Main entry point."""
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   {Fore.WHITE}🏫 PSB Chatbot - Admin Labeling Tool{Fore.CYAN}                  ║
║                                                          ║
║   Tool untuk pelabelan intent manual                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """)
    
    # Initialize database
    try:
        init_db()
        print_success("Database terhubung")
    except Exception as e:
        print_error(f"Gagal terhubung ke database: {str(e)}")
        print_info("Pastikan PostgreSQL berjalan dan konfigurasi .env sudah benar")
        return
    
    # Command loop
    commands = {
        'review': review_questions,
        'stats': show_stats,
        'export': export_data,
        'intents': show_available_intents,
        'search': search_and_review,
        'help': show_help,
        '?': show_help,
    }
    
    while True:
        print(f"\n{Fore.CYAN}Commands:{Style.RESET_ALL} review | stats | export | intents | search | help | quit")
        command = input(f"{Fore.GREEN}➜ {Style.RESET_ALL}").strip().lower()
        
        if command in ['quit', 'q', 'exit']:
            print_info("Terima kasih! 👋")
            break
        elif command in commands:
            commands[command]()
        elif command == '':
            continue
        else:
            print_warning(f"Command '{command}' tidak dikenali. Ketik 'help' untuk bantuan.")


if __name__ == "__main__":
    main()
