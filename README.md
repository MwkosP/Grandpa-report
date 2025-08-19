# 📊 Pappous Weekly Stock Reports

Αυτό το project δημιουργεί **εβδομαδιαία reports** (πίνακα + γράφημα) για τον Γενικό Δείκτη (GD.AT) και τα Ελληνικά Πετρέλαια (ELPE.AT), και τα στέλνει με email αυτόματα.

## 🚀 Πώς δουλεύει
- Το script `pappous.py` τραβάει δεδομένα από **Yahoo Finance** μεσω reverse engineering.
- Φτιάχνει εικόνες (πίνακα με τιμές κλεισίματος + γραφική παράσταση).
- Στέλνει τις εικόνες με email στον παραλήπτη που έχεις ορίσει.
- Τρέχει αυτόματα κάθε εβδομάδα με **GitHub Actions**.

## 📅 Προγραμματισμός (GitHub Actions)
Το workflow (`.github/workflows/report.yml`) είναι ρυθμισμένο να τρέχει:
- **Κάθε Τρίτη 04:07 ώρα Ελλάδας (01:07 UTC)**  
- Μπορείς επίσης να το τρέξεις χειροκίνητα από το GitHub → *Actions* → *Run workflow*.
<img width="2906" height="1766" alt="Ελληνικά_Πετρέλαια_report (1)" src="https://github.com/user-attachments/assets/f2dc6b1b-b34f-404a-a5c5-251894705578" />
