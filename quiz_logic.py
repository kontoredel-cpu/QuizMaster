import random
from file_handler import validiere_antwort

class QuizSession:
    """
    Verwaltet eine Quiz-Sitzung mit Fortschritt, Bewertung und Zustand.
    """
    
    def __init__(self, fragen_liste, modus, shuffle=False):
        """
        Initialisiert eine neue Quiz-Sitzung.
        
        Args:
            fragen_liste (list): Liste der Fragen für das Quiz
            modus (str): Name des Quiz-Modus (z.B. "Lernmodus" oder "Prüfungssimulation")
            shuffle (bool): Ob die Fragen gemischt werden sollen
        """
        self.original_fragen = fragen_liste.copy()
        self.modus = modus
        self.fragen = fragen_liste.copy()
        
        if shuffle:
            random.shuffle(self.fragen)
        
        self.current_index = 0
        self.richtige_antworten = 0
        self.antwort_historie = []
        self.user_antworten = []
    
    def get_current_question(self):
        """
        Gibt die aktuelle Frage zurück.
        
        Returns:
            dict: Das aktuelle Fragen-Objekt oder None wenn das Quiz beendet ist
        """
        if self.current_index < len(self.fragen):
            return self.fragen[self.current_index]
        return None
    
    def submit_answer(self, user_antwort):
        """
        Übermittelt eine Antwort und bewertet sie.
        
        Args:
            user_antwort (str): Die Antwort des Benutzers
            
        Returns:
            bool: True wenn die Antwort korrekt war, False sonst
        """
        if self.current_index >= len(self.fragen):
            return False
        
        current_question = self.fragen[self.current_index]
        
        # Antwort validieren
        is_correct = validiere_antwort(
            user_antwort, 
            current_question['antwort'], 
            current_question['synonyme']
        )
        
        # Ergebnisse speichern
        self.antwort_historie.append(is_correct)
        self.user_antworten.append(user_antwort)
        
        if is_correct:
            self.richtige_antworten += 1
        
        return is_correct
    
    def next_question(self):
        """
        Geht zur nächsten Frage über.
        """
        self.current_index += 1
    
    def is_finished(self):
        """
        Prüft ob das Quiz beendet ist.
        
        Returns:
            bool: True wenn alle Fragen bearbeitet wurden
        """
        return self.current_index >= len(self.fragen)
    
    def get_progress(self):
        """
        Gibt den aktuellen Fortschritt zurück.
        
        Returns:
            dict: Dictionary mit Fortschrittsinformationen
        """
        return {
            'current': self.current_index,
            'total': len(self.fragen),
            'percentage': (self.current_index / len(self.fragen)) * 100 if self.fragen else 0,
            'correct': self.richtige_antworten,
            'accuracy': (self.richtige_antworten / self.current_index) * 100 if self.current_index > 0 else 0
        }
    
    def get_results(self):
        """
        Gibt die finalen Ergebnisse zurück.
        
        Returns:
            dict: Dictionary mit Endergebnissen
        """
        total_questions = len(self.fragen)
        percentage = (self.richtige_antworten / total_questions) * 100 if total_questions > 0 else 0
        
        return {
            'total_questions': total_questions,
            'correct_answers': self.richtige_antworten,
            'wrong_answers': total_questions - self.richtige_antworten,
            'percentage': percentage,
            'grade': self.calculate_grade(percentage),
            'modus': self.modus
        }
    
    def calculate_grade(self, percentage):
        """
        Berechnet eine Bewertung basierend auf dem Prozentsatz.
        
        Args:
            percentage (float): Prozentsatz der richtigen Antworten
            
        Returns:
            str: Bewertungstext
        """
        if percentage >= 90:
            return "Ausgezeichnet"
        elif percentage >= 80:
            return "Sehr gut"
        elif percentage >= 70:
            return "Gut"
        elif percentage >= 60:
            return "Befriedigend"
        elif percentage >= 50:
            return "Ausreichend"
        else:
            return "Nicht bestanden"
    
    def reset(self):
        """
        Setzt das Quiz zurück auf den Anfang.
        """
        self.current_index = 0
        self.richtige_antworten = 0
        self.antwort_historie = []
        self.user_antworten = []
        
        # Fragen erneut mischen wenn es eine Prüfungssimulation ist
        if self.modus == "Prüfungssimulation":
            self.fragen = self.original_fragen.copy()
            random.shuffle(self.fragen)
    
    def get_question_details(self, question_index):
        """
        Gibt Details zu einer spezifischen Frage zurück.
        
        Args:
            question_index (int): Index der Frage
            
        Returns:
            dict: Details zur Frage inkl. Benutzerantwort und Bewertung
        """
        if 0 <= question_index < len(self.fragen) and question_index < len(self.antwort_historie):
            question = self.fragen[question_index]
            return {
                'question': question,
                'user_answer': self.user_antworten[question_index] if question_index < len(self.user_antworten) else "",
                'was_correct': self.antwort_historie[question_index],
                'correct_answer': question['antwort']
            }
        return None
