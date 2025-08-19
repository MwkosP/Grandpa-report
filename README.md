# 📊 Pappous Weekly Stock Reports

Αυτό το project δημιουργεί **εβδομαδιαία reports** (πίνακα + γράφημα) για τον Γενικό Δείκτη (GD.AT) και τα Ελληνικά Πετρέλαια (ELPE.AT), και τα στέλνει με email αυτόματα.

## 🚀 Πώς δουλεύει
- Το script `pappous.py` τραβάει δεδομένα από **Yahoo Finance** μεσω reverse engineering.
- Φτιάχνει εικόνες (πίνακα με τιμές κλεισίματος + γραφική παράσταση).
- Στέλνει τις εικόνες με email στον παραλήπτη που έχεις ορίσει.
- Τρέχει αυτόματα κάθε εβδομάδα με **GitHub Actions**.

## 📅 Προγραμματισμός (GitHub Actions)
Το workflow είναι ρυθμισμένο να τρέχει:
- **Κάθε Σάββατο 12.00 ώρα Ελλάδας **  
<img width="2906" height="1766" alt="Ελληνικά_Πετρέλαια_report (1)" src="https://github.com/user-attachments/assets/f2dc6b1b-b34f-404a-a5c5-251894705578" />
