import streamlit as st
import os
import zipfile
import tempfile
import shutil
from file_handler import lade_fragen_aus_ordnern, lade_fragen_aus_upload
from quiz_logic import QuizSession

# Sprachdaten für die Benutzeroberfläche
SPRACHEN = {
    'de': {
        'name': 'Deutsch',
        'title': '🩺 Lernprogramm für die Pflegeausbildung',
        'subtitle': 'Digitales Lernsystem für professionelle Pflegeausbildung',
        'mode_select': 'Wähle einen Lernmodus:',
        'mode_topic': '📚 Themen lernen',
        'mode_exam': '🎯 Prüfungssimulation',
        'mode_upload': '📁 Fragen hochladen',
        'topic_select': 'Wähle ein Thema zum Lernen:',
        'all_topics': 'Alle Themen (gemischt)',
        'start_quiz': 'Quiz starten',
        'question': 'Frage',
        'of': 'von',
        'your_answer': 'Deine Antwort:',
        'submit': 'Antwort absenden',
        'next': 'Nächste Frage',
        'back': 'Zurück',
        'correct': '✅ Richtig!',
        'incorrect': '❌ Falsch.',
        'model_answer': 'Musterlösung:',
        'results_title': '📊 Quiz-Ergebnisse',
        'score': 'Ergebnis',
        'percentage': 'Erfolgsquote',
        'analysis': 'Detailanalyse',
        'weak_topics': 'Schwache Bereiche zum Wiederholen:',
        'perfect': 'Perfekt! Du hast alle Fragen richtig beantwortet! 🎉',
        'restart': 'Neues Quiz starten',
        'back_menu': 'Zurück zum Menü',
        'upload_info': 'Lade eine ZIP-Datei mit der Ordnerstruktur hoch',
        'questions_loaded': 'Fragen erfolgreich geladen',
        'no_questions': 'Keine Fragen gefunden',
        'simulation_start': 'Prüfungssimulation wird gestartet...',
        'simulation_info': 'Fragen aus allen Themen werden in zufälliger Reihenfolge gestellt.'
    },
    'tr': {
        'name': 'Türkçe',
        'title': '🩺 Hemşirelik Eğitimi için Öğrenme Programı',
        'subtitle': 'Profesyonel hemşirelik eğitimi için dijital öğrenme sistemi',
        'mode_select': 'Bir öğrenme modu seçin:',
        'mode_topic': '📚 Konuları öğren',
        'mode_exam': '🎯 Sınav simülasyonu',
        'mode_upload': '📁 Soru yükle',
        'topic_select': 'Öğrenmek için bir konu seçin:',
        'all_topics': 'Tüm konular (karışık)',
        'start_quiz': 'Quiz başlat',
        'question': 'Soru',
        'of': 'den',
        'your_answer': 'Cevabınız:',
        'submit': 'Cevabı gönder',
        'next': 'Sonraki soru',
        'back': 'Geri',
        'correct': '✅ Doğru!',
        'incorrect': '❌ Yanlış.',
        'model_answer': 'Örnek çözüm:',
        'results_title': '📊 Quiz sonuçları',
        'score': 'Sonuç',
        'percentage': 'Başarı oranı',
        'analysis': 'Detaylı analiz',
        'weak_topics': 'Tekrar edilmesi gereken zayıf alanlar:',
        'perfect': 'Mükemmel! Tüm soruları doğru cevapladınız! 🎉',
        'restart': 'Yeni quiz başlat',
        'back_menu': 'Menüye dön',
        'upload_info': 'Klasör yapısıyla bir ZIP dosyası yükleyin',
        'questions_loaded': 'Sorular başarıyla yüklendi',
        'no_questions': 'Soru bulunamadı',
        'simulation_start': 'Sınav simülasyonu başlatılıyor...',
        'simulation_info': 'Tüm konulardan sorular rastgele sırada sorulacak.'
    }
}

def init_session_state():
    """Initialisiert den Session State für die Anwendung."""
    if 'quiz_session' not in st.session_state:
        st.session_state.quiz_session = None
    if 'alle_fragen' not in st.session_state:
        st.session_state.alle_fragen = []
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = 'menu'
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = None
    if 'language' not in st.session_state:
        st.session_state.language = 'de'
    if 'quiz_ergebnisse' not in st.session_state:
        st.session_state.quiz_ergebnisse = None

def cleanup_temp_dir():
    """Bereinigt temporäre Verzeichnisse."""
    if st.session_state.temp_dir and os.path.exists(st.session_state.temp_dir):
        try:
            shutil.rmtree(st.session_state.temp_dir)
            st.session_state.temp_dir = None
        except Exception:
            pass

def load_questions_from_directory():
    """Lädt Fragen aus dem pflegepool-Verzeichnis."""
    fragen = lade_fragen_aus_ordnern()
    if fragen:
        st.session_state.alle_fragen = fragen
        st.success(f"✅ {len(fragen)} Fragen in {len(set(f['thema'] for f in fragen))} Themen erfolgreich geladen!")
        return True
    else:
        st.error("❌ Keine Fragen im 'pflegepool'-Ordner gefunden. Bitte stelle sicher, dass der Ordner existiert und korrekt strukturiert ist.")
        return False

def handle_file_upload():
    """Behandelt den Upload von Fragendateien."""
    st.subheader("📁 Fragensätze hochladen")
    st.info("Lade eine ZIP-Datei mit der Ordnerstruktur: pflegepool/thema/fragen.txt, antworten.txt, synonyme.txt hoch.")
    
    uploaded_file = st.file_uploader(
        "ZIP-Datei mit Fragensätzen auswählen", 
        type=['zip'],
        help="Die ZIP-Datei sollte einen 'pflegepool'-Ordner mit Themen-Unterordnern enthalten."
    )
    
    if uploaded_file is not None:
        try:
            # Cleanup previous temp directory
            cleanup_temp_dir()
            
            # Create new temp directory
            temp_dir = tempfile.mkdtemp()
            st.session_state.temp_dir = temp_dir
            
            # Extract ZIP file
            zip_path = os.path.join(temp_dir, "uploaded.zip")
            with open(zip_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Load questions from extracted files
            fragen = lade_fragen_aus_upload(temp_dir)
            
            if fragen:
                st.session_state.alle_fragen = fragen
                st.success(f"✅ {len(fragen)} Fragen in {len(set(f['thema'] for f in fragen))} Themen aus der hochgeladenen Datei geladen!")
                st.session_state.current_mode = 'menu'
                st.rerun()
            else:
                st.error("❌ Keine gültigen Fragen in der hochgeladenen Datei gefunden.")
                
        except Exception as e:
            st.error(f"❌ Fehler beim Verarbeiten der hochgeladenen Datei: {str(e)}")

def show_main_menu():
    """Zeigt das Hauptmenü der Anwendung."""
    st.title("🎓 Lern- und Prüfungssimulation")
    st.markdown("---")
    
    # Fragen laden Sektion
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📚 Fragen aus Verzeichnis laden")
        if st.button("Fragen aus 'pflegepool'-Ordner laden", use_container_width=True):
            load_questions_from_directory()
    
    with col2:
        st.subheader("📤 Eigene Fragen hochladen")
        if st.button("Fragensätze hochladen", use_container_width=True):
            st.session_state.current_mode = 'upload'
            st.rerun()
    
    # Status anzeigen
    if st.session_state.alle_fragen:
        st.markdown("---")
        st.success(f"📊 **Status:** {len(st.session_state.alle_fragen)} Fragen in {len(set(f['thema'] for f in st.session_state.alle_fragen))} Themen verfügbar")
        
        # Hauptmenü Optionen
        st.subheader("🚀 Lernmodi")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎯 Lernmodus (Thema wählen)", use_container_width=True, type="primary"):
                st.session_state.current_mode = 'lernmodus'
                st.rerun()
        
        with col2:
            if st.button("📝 Prüfungssimulation (Alle Themen)", use_container_width=True, type="secondary"):
                st.session_state.current_mode = 'pruefung'
                st.rerun()
        
        # Themen-Übersicht
        with st.expander("📋 Verfügbare Themen anzeigen"):
            themen = sorted(list(set(f['thema'] for f in st.session_state.alle_fragen)))
            for thema in themen:
                anzahl = len([f for f in st.session_state.alle_fragen if f['thema'] == thema])
                st.write(f"• **{thema}**: {anzahl} Fragen")

def show_lernmodus():
    """Zeigt die Themenauswahl für den Lernmodus."""
    st.title("🎯 Lernmodus - Thema auswählen")
    
    if st.button("← Zurück zum Hauptmenü"):
        st.session_state.current_mode = 'menu'
        st.rerun()
    
    st.markdown("---")
    
    themen = sorted(list(set(f['thema'] for f in st.session_state.alle_fragen)))
    
    if not themen:
        st.warning("Keine Themen verfügbar. Bitte lade zuerst Fragen.")
        return
    
    st.subheader("Wähle ein Thema zum Lernen:")
    
    selected_thema = st.selectbox(
        "Thema auswählen:",
        themen,
        help="Wähle das Thema aus, das du lernen möchtest."
    )
    
    if selected_thema:
        fragen_zum_thema = [f for f in st.session_state.alle_fragen if f['thema'] == selected_thema]
        st.info(f"📚 Thema '{selected_thema}' enthält {len(fragen_zum_thema)} Fragen")
        
        if st.button("🚀 Lernmodus starten", type="primary", use_container_width=True):
            st.session_state.quiz_session = QuizSession(fragen_zum_thema, selected_thema)
            st.session_state.current_mode = 'quiz'
            st.rerun()

def show_pruefungssimulation():
    """Zeigt die Prüfungssimulation."""
    st.title("📝 Prüfungssimulation")
    
    if st.button("← Zurück zum Hauptmenü"):
        st.session_state.current_mode = 'menu'
        st.rerun()
    
    st.markdown("---")
    
    total_fragen = len(st.session_state.alle_fragen)
    themen_anzahl = len(set(f['thema'] for f in st.session_state.alle_fragen))
    
    st.subheader("🎲 Alle Fragen in zufälliger Reihenfolge")
    st.info(f"📊 Insgesamt {total_fragen} Fragen aus {themen_anzahl} verschiedenen Themen")
    
    st.warning("⚠️ **Hinweis:** Die Fragen werden in zufälliger Reihenfolge gestellt. Dies simuliert eine echte Prüfungssituation.")
    
    if st.button("🚀 Prüfungssimulation starten", type="primary", use_container_width=True):
        st.session_state.quiz_session = QuizSession(st.session_state.alle_fragen, "Prüfungssimulation", shuffle=True)
        st.session_state.current_mode = 'quiz'
        st.rerun()

def show_quiz():
    """Zeigt das Quiz-Interface."""
    if not st.session_state.quiz_session:
        st.session_state.current_mode = 'menu'
        st.rerun()
        return
    
    quiz = st.session_state.quiz_session
    
    # Header mit Fortschritt
    st.title(f"📚 {quiz.modus}")
    
    # Fortschrittsbalken
    progress = quiz.current_index / len(quiz.fragen) if quiz.fragen else 0
    st.progress(progress, text=f"Frage {quiz.current_index + 1} von {len(quiz.fragen)}")
    
    # Zwischenergebnis anzeigen
    if quiz.current_index > 0:
        st.metric(
            "Aktueller Stand", 
            f"{quiz.richtige_antworten}/{quiz.current_index}", 
            f"{(quiz.richtige_antworten/quiz.current_index)*100:.1f}%"
        )
    
    st.markdown("---")
    
    # Quiz beendet?
    if quiz.is_finished():
        show_quiz_results(quiz)
        return
    
    # Aktuelle Frage
    current_question = quiz.get_current_question()
    
    st.subheader(f"🏷️ Thema: {current_question['thema']}")
    st.markdown(f"### ❓ {current_question['frage']}")
    
    # Antwort-Eingabe
    user_answer = st.text_area(
        "Deine Antwort:",
        height=100,
        placeholder="Gib hier deine Antwort ein...",
        key=f"answer_{quiz.current_index}"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("✅ Antwort bestätigen", type="primary", use_container_width=True, disabled=not user_answer.strip()):
            result = quiz.submit_answer(user_answer)
            st.session_state.show_result = True
            st.rerun()
    
    # Ergebnis der letzten Frage anzeigen
    if hasattr(st.session_state, 'show_result') and st.session_state.show_result:
        show_answer_feedback(quiz, current_question, user_answer)
        
        if st.button("➡️ Nächste Frage", type="secondary", use_container_width=True):
            quiz.next_question()
            del st.session_state.show_result
            st.rerun()

def show_answer_feedback(quiz, question, user_answer):
    """Zeigt das Feedback zur eingegebenen Antwort."""
    st.markdown("---")
    st.subheader("📊 Bewertung")
    
    # Bewertung der letzten Antwort
    if quiz.current_index > 0:
        last_correct = quiz.antwort_historie[-1]
        if last_correct:
            st.success("✅ **Richtig!** Deine Antwort enthält die richtigen Schlüsselwörter.")
        else:
            st.error("❌ **Falsch.** Deine Antwort scheint nicht die erwarteten Begriffe zu enthalten.")
    
    # Musterlösung anzeigen
    st.info(f"💡 **Musterlösung:** {question['antwort']}")
    
    # Synonyme anzeigen (falls vorhanden)
    if question.get('synonyme') and question['synonyme'][0]:
        st.caption(f"🔍 **Suchbegriffe:** {', '.join(question['synonyme'])}")

def show_quiz_results(quiz):
    """Zeigt die Endergebnisse des Quiz."""
    st.subheader("🎯 Quiz abgeschlossen!")
    
    percentage = (quiz.richtige_antworten / len(quiz.fragen)) * 100
    
    # Ergebnis-Metriken
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Richtige Antworten", quiz.richtige_antworten)
    
    with col2:
        st.metric("Gesamte Fragen", len(quiz.fragen))
    
    with col3:
        st.metric("Erfolgsquote", f"{percentage:.1f}%")
    
    # Bewertung
    if percentage >= 80:
        st.success("🌟 **Ausgezeichnet!** Du hast sehr gut abgeschnitten.")
    elif percentage >= 60:
        st.info("👍 **Gut gemacht!** Du bist auf dem richtigen Weg.")
    else:
        st.warning("📚 **Übung macht den Meister!** Versuche es gerne nochmal.")
    
    # Detaillierte Auswertung
    with st.expander("📋 Detaillierte Auswertung anzeigen"):
        for i, (frage, korrekt) in enumerate(zip(quiz.fragen, quiz.antwort_historie)):
            status = "✅" if korrekt else "❌"
            st.write(f"{status} **Frage {i+1}:** {frage['frage'][:50]}...")
    
    # Aktionen
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Quiz wiederholen", use_container_width=True):
            # Reset quiz session with same questions
            st.session_state.quiz_session = QuizSession(
                quiz.original_fragen, 
                quiz.modus, 
                shuffle=(quiz.modus == "Prüfungssimulation")
            )
            st.rerun()
    
    with col2:
        if st.button("🏠 Zum Hauptmenü", use_container_width=True, type="primary"):
            st.session_state.quiz_session = None
            st.session_state.current_mode = 'menu'
            if hasattr(st.session_state, 'show_result'):
                del st.session_state.show_result
            st.rerun()

def main():
    """Hauptfunktion der Anwendung."""
    # Initialisierung
    init_session_state()
    
    # Routing basierend auf current_mode
    if st.session_state.current_mode == 'menu':
        show_main_menu()
    elif st.session_state.current_mode == 'upload':
        handle_file_upload()
        if st.button("← Zurück zum Hauptmenü"):
            st.session_state.current_mode = 'menu'
            st.rerun()
    elif st.session_state.current_mode == 'lernmodus':
        show_lernmodus()
    elif st.session_state.current_mode == 'pruefung':
        show_pruefungssimulation()
    elif st.session_state.current_mode == 'quiz':
        show_quiz()
    
    # Cleanup bei Seitenende
    if st.session_state.get('temp_dir'):
        # Temporäre Verzeichnisse werden automatisch beim nächsten Lauf bereinigt
        pass

if __name__ == "__main__":
    main()
