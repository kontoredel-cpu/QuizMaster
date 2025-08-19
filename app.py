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
        'topic_overview': 'Themenübersicht',
        'main_page': 'Startseite',
        'navigation_help': '(a) Antwort eingeben, (z) Zurück, (ü) Themenübersicht, (s) Startseite',
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
        'simulation_info': 'Fragen aus allen Themen werden in zufälliger Reihenfolge gestellt.',
        'available_topics': 'Verfügbare Themen',
        'total_questions': 'Gesamte Fragen',
        'avg_per_topic': 'Ø Fragen pro Thema',
        'main_menu': 'Hauptmenü',
        'load_from_folder': 'Fragen aus Ordner laden',
        'upload_new': 'Neue Fragen hochladen',
        'reload_questions': 'Fragen neu laden',
        'further_options': 'Weitere Optionen',
        'topic_learning_help': 'Lerne gezielt einzelne Themen',
        'exam_help': 'Simulation einer echten Prüfung mit gemischten Fragen',
        'current_status': 'Aktueller Stand',
        'topic_label': 'Thema:',
        'confirm_answer': 'Antwort bestätigen',
        'next_question': 'Nächste Frage',
        'evaluation': 'Bewertung',
        'excellent': 'Ausgezeichnet! Du hast sehr gut abgeschnitten.',
        'good': 'Gut gemacht! Du bist auf dem richtigen Weg.',
        'practice': 'Übung macht den Meister! Versuche es gerne nochmal.',
        'detailed_evaluation': 'Detaillierte Auswertung anzeigen',
        'repeat_quiz': 'Quiz wiederholen',
        'to_main_menu': 'Zum Hauptmenü'
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
        'topic_overview': 'Konu genel bakışı',
        'main_page': 'Ana sayfa',
        'navigation_help': '(a) Cevap gir, (z) Geri, (ü) Konu genel bakışı, (s) Ana sayfa',
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
        'simulation_info': 'Tüm konulardan sorular rastgele sırada sorulacak.',
        'available_topics': 'Mevcut Konular',
        'total_questions': 'Toplam Sorular',
        'avg_per_topic': 'Ø Konu başına soru',
        'main_menu': 'Ana Menü',
        'load_from_folder': 'Klasörden soru yükle',
        'upload_new': 'Yeni sorular yükle',
        'reload_questions': 'Soruları yeniden yükle',
        'further_options': 'Diğer Seçenekler',
        'topic_learning_help': 'Belirli konuları hedefli olarak öğren',
        'exam_help': 'Karışık sorularla gerçek sınav simülasyonu',
        'current_status': 'Mevcut Durum',
        'topic_label': 'Konu:',
        'confirm_answer': 'Cevabı onayla',
        'next_question': 'Sonraki soru',
        'evaluation': 'Değerlendirme',
        'excellent': 'Mükemmel! Çok iyi bir performans sergiledingiz.',
        'good': 'İyi iş çıkardınız! Doğru yoldasınız.',
        'practice': 'Pratik mükemmelleştirir! Tekrar deneyebilirsiniz.',
        'detailed_evaluation': 'Detaylı değerlendirmeyi göster',
        'repeat_quiz': 'Quiz\'i tekrarla',
        'to_main_menu': 'Ana menüye'
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

def get_text(key):
    """Hilfsfunktion zum Abrufen von lokalisierten Texten."""
    return SPRACHEN[st.session_state.language].get(key, key)

def show_language_selector():
    """Zeigt die Sprachauswahl in der Sidebar."""
    st.sidebar.header("🌐 Sprache / Dil")
    
    language_options = {lang: data['name'] for lang, data in SPRACHEN.items()}
    current_lang = st.sidebar.selectbox(
        "Sprache wählen / Dil seçin:",
        options=list(language_options.keys()),
        format_func=lambda x: language_options[x],
        index=list(language_options.keys()).index(st.session_state.language)
    )
    
    if current_lang != st.session_state.language:
        st.session_state.language = current_lang
        st.rerun()

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
        st.success(f"✅ {len(fragen)} {get_text('questions_loaded')} - {len(set(f['thema'] for f in fragen))} {get_text('available_topics').lower()}")
        return True
    else:
        st.error(f"❌ {get_text('no_questions')}")
        return False

def analyze_quiz_results(quiz_session):
    """Analysiert die Quiz-Ergebnisse für detailliertes Feedback."""
    if not quiz_session or not quiz_session.antwort_historie:
        return None
    
    results = {
        'total_questions': len(quiz_session.antwort_historie),
        'correct_answers': quiz_session.richtige_antworten,
        'percentage': (quiz_session.richtige_antworten / len(quiz_session.antwort_historie)) * 100,
        'topic_analysis': {}
    }
    
    # Themen-spezifische Analyse
    for i, (correct, question) in enumerate(zip(quiz_session.antwort_historie, quiz_session.fragen)):
        thema = question['thema']
        if thema not in results['topic_analysis']:
            results['topic_analysis'][thema] = {'total': 0, 'correct': 0}
        
        results['topic_analysis'][thema]['total'] += 1
        if correct:
            results['topic_analysis'][thema]['correct'] += 1
    
    # Schwache Bereiche identifizieren
    weak_topics = []
    for thema, stats in results['topic_analysis'].items():
        percentage = (stats['correct'] / stats['total']) * 100
        if percentage < 70:  # Weniger als 70% richtig
            weak_topics.append((thema, percentage, stats['total'] - stats['correct']))
    
    results['weak_topics'] = sorted(weak_topics, key=lambda x: x[1])  # Sortiert nach Prozentsatz
    
    return results

def handle_file_upload():
    """Behandelt den Upload von Fragendateien."""
    st.subheader(f"📁 {get_text('mode_upload')}")
    st.info(get_text('upload_info'))
    
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
                st.success(f"✅ {len(fragen)} {get_text('questions_loaded')}")
                st.session_state.current_mode = 'menu'
                st.rerun()
            else:
                st.error(f"❌ {get_text('no_questions')}")
                
        except Exception as e:
            st.error(f"❌ Fehler beim Verarbeiten der Datei: {str(e)}")

def show_main_menu():
    """Zeigt das Hauptmenü der Anwendung."""
    st.header(f"📋 {get_text('main_menu')}")
    
    if not st.session_state.alle_fragen:
        st.warning(f"⚠️ {get_text('no_questions')}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🔄 {get_text('load_from_folder')}", use_container_width=True):
                load_questions_from_directory()
        with col2:
            if st.button(get_text('mode_upload'), use_container_width=True):
                st.session_state.current_mode = 'upload'
                st.rerun()
        return
    
    # Statistiken anzeigen
    themen = list(set(f['thema'] for f in st.session_state.alle_fragen))
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"📚 {get_text('available_topics')}", len(themen))
    with col2:
        st.metric(f"❓ {get_text('total_questions')}", len(st.session_state.alle_fragen))
    with col3:
        durchschnitt = len(st.session_state.alle_fragen) / len(themen) if themen else 0
        st.metric(f"📊 {get_text('avg_per_topic')}", f"{durchschnitt:.1f}")
    
    st.header(f"🎯 {get_text('mode_select')}")
    
    # Lernmodi
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(get_text('mode_topic'), use_container_width=True, help=get_text('topic_learning_help')):
            st.session_state.current_mode = 'lernmodus'
            st.rerun()
    
    with col2:
        if st.button(get_text('mode_exam'), use_container_width=True, help=get_text('exam_help')):
            st.session_state.current_mode = 'pruefung'
            st.rerun()
    
    # Zusätzliche Optionen
    st.header(f"⚙️ {get_text('further_options')}")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"📁 {get_text('upload_new')}", use_container_width=True):
            st.session_state.current_mode = 'upload'
            st.rerun()
    
    with col2:
        if st.button(f"🔄 {get_text('reload_questions')}", use_container_width=True):
            load_questions_from_directory()

def show_lernmodus():
    """Zeigt die Themenauswahl für den Lernmodus."""
    st.title(f"🎯 {get_text('mode_topic')} - {get_text('topic_overview')}")
    
    if st.button(f"← {get_text('back')} {get_text('main_menu')}"):
        st.session_state.current_mode = 'menu'
        st.rerun()
    
    st.markdown("---")
    
    themen = sorted(list(set(f['thema'] for f in st.session_state.alle_fragen)))
    
    if not themen:
        st.warning(get_text('no_questions'))
        return
    
    st.subheader(get_text('topic_select'))
    
    # Verbesserte Themen-Anzeige mit Details
    for i, thema in enumerate(themen, 1):
        fragen_zum_thema = [f for f in st.session_state.alle_fragen if f['thema'] == thema]
        
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{i}. {thema}**")
            
            with col2:
                st.write(f"📚 {len(fragen_zum_thema)} Fragen")
            
            with col3:
                if st.button(f"🚀 Starten", key=f"start_{i}", use_container_width=True):
                    st.session_state.quiz_session = QuizSession(fragen_zum_thema, thema)
                    st.session_state.current_mode = 'quiz'
                    st.rerun()
            
            st.markdown("---")
    
    # Alternative: Dropdown-Auswahl (falls gewünscht)
    with st.expander("📋 Alternative: Thema aus Liste auswählen"):
        selected_thema = st.selectbox(
            f"{get_text('topic_select')}",
            themen,
            help="Wähle das Thema aus, das du lernen möchtest."
        )
        
        if selected_thema:
            fragen_zum_thema = [f for f in st.session_state.alle_fragen if f['thema'] == selected_thema]
            st.info(f"📚 {selected_thema}: {len(fragen_zum_thema)} {get_text('question').lower()}")
            
            if st.button(f"🚀 {get_text('start_quiz')}", type="primary", use_container_width=True):
                st.session_state.quiz_session = QuizSession(fragen_zum_thema, selected_thema)
                st.session_state.current_mode = 'quiz'
                st.rerun()

def show_pruefungssimulation():
    """Zeigt die Prüfungssimulation."""
    st.title(f"📝 {get_text('mode_exam')}")
    
    if st.button(f"← {get_text('back')} {get_text('main_menu')}"):
        st.session_state.current_mode = 'menu'
        st.rerun()
    
    st.markdown("---")
    
    total_fragen = len(st.session_state.alle_fragen)
    themen_anzahl = len(set(f['thema'] for f in st.session_state.alle_fragen))
    
    st.subheader(f"🎲 {get_text('all_topics')}")
    st.info(f"📊 {total_fragen} {get_text('question').lower()} - {themen_anzahl} {get_text('available_topics').lower()}")
    
    st.warning(f"⚠️ **{get_text('simulation_info')}**")
    
    if st.button(f"🚀 {get_text('start_quiz')}", type="primary", use_container_width=True):
        st.session_state.quiz_session = QuizSession(st.session_state.alle_fragen, get_text('mode_exam'), shuffle=True)
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
    
    # Navigation Buttons (erweitert)
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    
    with nav_col1:
        if st.button(f"🏠 {get_text('main_page')}", use_container_width=True):
            st.session_state.current_mode = 'menu'
            st.session_state.quiz_session = None
            if hasattr(st.session_state, 'show_result'):
                del st.session_state.show_result
            st.rerun()
    
    with nav_col2:
        if quiz.modus != get_text('mode_exam'):  # Nur im Lernmodus verfügbar
            if st.button(f"📋 {get_text('topic_overview')}", use_container_width=True):
                st.session_state.current_mode = 'lernmodus'
                st.session_state.quiz_session = None
                if hasattr(st.session_state, 'show_result'):
                    del st.session_state.show_result
                st.rerun()
    
    with nav_col3:
        if quiz.current_index > 0:
            if st.button(f"⬅️ {get_text('back')}", use_container_width=True):
                quiz.current_index -= 1
                if quiz.antwort_historie:
                    quiz.antwort_historie.pop()
                    quiz.user_antworten.pop()
                    # Richtige Antworten entsprechend anpassen
                    if len(quiz.antwort_historie) > 0 and quiz.antwort_historie[-1]:
                        quiz.richtige_antworten = sum(quiz.antwort_historie)
                    else:
                        quiz.richtige_antworten = max(0, quiz.richtige_antworten - 1)
                if hasattr(st.session_state, 'show_result'):
                    del st.session_state.show_result
                st.rerun()
    
    with nav_col4:
        # Platzhalter für Balance
        st.write("")
    
    # Navigationshilfe anzeigen (nur im Lernmodus)
    if quiz.modus != get_text('mode_exam'):
        st.info(f"💡 {get_text('navigation_help')}")
    
    # Fortschrittsbalken
    progress = quiz.current_index / len(quiz.fragen) if quiz.fragen else 0
    st.progress(progress, text=f"{get_text('question')} {quiz.current_index + 1} {get_text('of')} {len(quiz.fragen)}")
    
    # Zwischenergebnis anzeigen
    if quiz.current_index > 0:
        st.metric(
            get_text('current_status'), 
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
    
    st.subheader(f"🏷️ {get_text('topic_label')} {current_question['thema']}")
    st.markdown(f"### ❓ {current_question['frage']}")
    
    # Antwort-Eingabe
    user_answer = st.text_area(
        get_text('your_answer'),
        height=100,
        placeholder="Gib hier deine Antwort ein...",
        key=f"answer_{quiz.current_index}"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button(f"✅ {get_text('confirm_answer')}", type="primary", use_container_width=True, disabled=not user_answer.strip()):
            result = quiz.submit_answer(user_answer)
            st.session_state.show_result = True
            st.rerun()
    
    # Ergebnis der letzten Frage anzeigen
    if hasattr(st.session_state, 'show_result') and st.session_state.show_result:
        show_answer_feedback(quiz, current_question, user_answer)
        
        if st.button(f"➡️ {get_text('next_question')}", type="secondary", use_container_width=True):
            quiz.next_question()
            del st.session_state.show_result
            st.rerun()

def show_answer_feedback(quiz, question, user_answer):
    """Zeigt das Feedback zur eingegebenen Antwort."""
    st.markdown("---")
    st.subheader(f"📊 {get_text('evaluation')}")
    
    last_result = quiz.antwort_historie[-1] if quiz.antwort_historie else False
    
    if last_result:
        st.success(get_text('correct'))
    else:
        st.error(get_text('incorrect'))
        st.info(f"**{get_text('model_answer')}** {question['antwort']}")

def show_quiz_results(quiz):
    """Zeigt die finalen Quiz-Ergebnisse."""
    st.title(get_text('results_title'))
    
    total_questions = len(quiz.fragen)
    correct_answers = quiz.richtige_antworten
    percentage = (correct_answers / total_questions) * 100
    
    # Hauptstatistiken
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(f"{get_text('score')}", f"{correct_answers}/{total_questions}")
    
    with col2:
        st.metric(f"{get_text('total_questions')}", len(quiz.fragen))
    
    with col3:
        st.metric(f"{get_text('percentage')}", f"{percentage:.1f}%")
    
    # Bewertung
    if percentage >= 80:
        st.success(f"🌟 **{get_text('excellent')}**")
    elif percentage >= 60:
        st.info(f"👍 **{get_text('good')}**")
    else:
        st.warning(f"📚 **{get_text('practice')}**")
    
    # Detaillierte Auswertung
    results = analyze_quiz_results(quiz)
    if results and results['weak_topics']:
        st.subheader(get_text('weak_topics'))
        for thema, percentage, errors in results['weak_topics']:
            st.write(f"• **{thema}**: {percentage:.1f}% ({errors} Fehler)")
    
    # Detaillierte Auswertung
    with st.expander(f"📋 {get_text('detailed_evaluation')}"):
        for i, (frage, korrekt) in enumerate(zip(quiz.fragen, quiz.antwort_historie)):
            status = "✅" if korrekt else "❌"
            st.write(f"{status} **{get_text('question')} {i+1}:** {frage['frage'][:50]}...")
    
    # Aktionen
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"🔄 {get_text('repeat_quiz')}", use_container_width=True):
            # Reset quiz session with same questions
            st.session_state.quiz_session = QuizSession(
                quiz.original_fragen, 
                quiz.modus, 
                shuffle=(get_text('mode_exam') in quiz.modus)
            )
            st.rerun()
    
    with col2:
        if st.button(f"🏠 {get_text('to_main_menu')}", use_container_width=True, type="primary"):
            st.session_state.quiz_session = None
            st.session_state.current_mode = 'menu'
            if hasattr(st.session_state, 'show_result'):
                del st.session_state.show_result
            st.rerun()

def main():
    """Hauptfunktion der Anwendung."""
    init_session_state()
    
    # Sprachauswahl in der Sidebar
    show_language_selector()
    
    # Aufräumen von temp-Ordnern beim Exit
    cleanup_temp_dir()
    
    # Automatisches Laden von Fragen beim Start
    if not st.session_state.alle_fragen:
        load_questions_from_directory()
    
    # Titel und Beschreibung (lokalisiert)
    st.title(get_text('title'))
    st.markdown(f"**{get_text('subtitle')}**")
    
    # Navigation je nach Modus
    if st.session_state.current_mode == 'menu':
        show_main_menu()
    elif st.session_state.current_mode == 'upload':
        handle_file_upload()
        if st.button(f"← {get_text('back')} {get_text('main_menu')}"):
            st.session_state.current_mode = 'menu'
            st.rerun()
    elif st.session_state.current_mode == 'lernmodus':
        show_lernmodus()
    elif st.session_state.current_mode == 'pruefung':
        show_pruefungssimulation()
    elif st.session_state.current_mode == 'quiz':
        show_quiz()

if __name__ == "__main__":
    main()