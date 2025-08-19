import os
import sys

def lade_fragen_aus_ordnern():
    """
    Sucht intelligent nach dem 'pflegepool'-Ordner, der sich neben dem Skript befinden muss.
    Angepasst für Streamlit-Umgebung.
    """
    try:
        # Finde heraus, wo das Skript ausgeführt wird (funktioniert als .py und als .exe)
        if getattr(sys, 'frozen', False):
            # Wenn das Skript als .exe ausgeführt wird (mit PyInstaller)
            skript_ordner = os.path.dirname(sys.executable)
        else:
            # Wenn das Skript als normale .py-Datei ausgeführt wird
            skript_ordner = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # Fallback für einige Umgebungen
        skript_ordner = os.getcwd()

    # Baue den Pfad zum 'pflegepool'-Ordner relativ zum Skript-Standort zusammen
    haupt_ordner_pfad = os.path.join(skript_ordner, 'pflegepool')
    
    return lade_fragen_aus_pfad(haupt_ordner_pfad)

def lade_fragen_aus_upload(temp_dir):
    """
    Lädt Fragen aus einem hochgeladenen und extrahierten Verzeichnis.
    """
    # Suche nach 'pflegepool'-Ordner im extrahierten Verzeichnis
    pflegepool_pfad = None
    
    # Direkt im temp_dir schauen
    if os.path.isdir(os.path.join(temp_dir, 'pflegepool')):
        pflegepool_pfad = os.path.join(temp_dir, 'pflegepool')
    else:
        # In Unterordnern suchen
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path):
                pflegepool_subpath = os.path.join(item_path, 'pflegepool')
                if os.path.isdir(pflegepool_subpath):
                    pflegepool_pfad = pflegepool_subpath
                    break
    
    if not pflegepool_pfad:
        return None
    
    return lade_fragen_aus_pfad(pflegepool_pfad)

def lade_fragen_aus_pfad(haupt_ordner_pfad):
    """
    Lädt Fragen aus einem gegebenen Pflegepool-Ordner.
    """
    gesamter_fragenkatalog = []
    
    if not os.path.isdir(haupt_ordner_pfad):
        return None

    try:
        for themen_name in os.listdir(haupt_ordner_pfad):
            themen_pfad = os.path.join(haupt_ordner_pfad, themen_name)
            if os.path.isdir(themen_pfad):
                # Dateipfade für das aktuelle Thema
                fragen_datei = os.path.join(themen_pfad, 'fragen.txt')
                antworten_datei = os.path.join(themen_pfad, 'antworten.txt')
                synonyme_datei = os.path.join(themen_pfad, 'synonyme.txt')
                
                if os.path.exists(fragen_datei) and os.path.exists(antworten_datei):
                    try:
                        # Fragen laden
                        with open(fragen_datei, 'r', encoding='utf-8') as f:
                            fragen_zeilen = f.readlines()
                        
                        # Antworten laden
                        with open(antworten_datei, 'r', encoding='utf-8') as f:
                            antworten_zeilen = f.readlines()
                        
                        # Synonyme laden (optional)
                        synonyme_zeilen = []
                        if os.path.exists(synonyme_datei):
                            with open(synonyme_datei, 'r', encoding='utf-8') as f:
                                synonyme_zeilen = f.readlines()
                        
                        # Prüfen ob Fragen und Antworten gleiche Länge haben
                        if len(fragen_zeilen) == len(antworten_zeilen):
                            for i in range(len(fragen_zeilen)):
                                # Synonyme für diese Zeile verarbeiten
                                synonyme_text = synonyme_zeilen[i].strip() if i < len(synonyme_zeilen) else ""
                                synonyme_liste = [syn.strip().lower() for syn in synonyme_text.split(',') if syn.strip()]
                                
                                frage_objekt = {
                                    "frage": fragen_zeilen[i].strip(),
                                    "antwort": antworten_zeilen[i].strip(),
                                    "synonyme": synonyme_liste,
                                    "thema": themen_name
                                }
                                gesamter_fragenkatalog.append(frage_objekt)
                        else:
                            print(f"Warnung: In '{themen_name}' haben die Dateien eine unterschiedliche Zeilenanzahl. Block wird übersprungen.")
                    except Exception as e:
                        print(f"Fehler beim Lesen der Dateien im Ordner {themen_name}: {e}")
    except Exception as e:
        print(f"Fehler beim Durchsuchen des Hauptordners: {e}")
        return None
    
    return gesamter_fragenkatalog

def validiere_antwort(user_antwort, korrekte_antwort, synonyme):
    """
    Validiert eine Benutzerantwort basierend auf Synonymen.
    
    Args:
        user_antwort (str): Die Antwort des Benutzers
        korrekte_antwort (str): Die korrekte Antwort (für Referenz)
        synonyme (list): Liste der Synonym-Schlüsselwörter
    
    Returns:
        bool: True wenn die Antwort als korrekt bewertet wird, False sonst
    """
    if not user_antwort or not isinstance(user_antwort, str):
        return False
    
    user_antwort_lower = user_antwort.lower().strip()
    
    # Wenn keine Synonyme definiert sind, einfache Textübereinstimmung
    if not synonyme or not synonyme[0]:
        # Fallback: Prüfe ob ein Teil der korrekten Antwort enthalten ist
        korrekte_antwort_lower = korrekte_antwort.lower()
        return any(word in user_antwort_lower for word in korrekte_antwort_lower.split() if len(word) > 2)
    
    # Prüfe Synonyme
    for synonym in synonyme:
        if synonym and synonym.strip() and synonym.strip().lower() in user_antwort_lower:
            return True
    
    return False
