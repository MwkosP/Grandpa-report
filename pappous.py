import os
import time
import smtplib
import pytz
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# --------- ΡΥΘΜΙΣΕΙΣ ---------
TIMEZONE = "Europe/Athens"
TICKER_MAP = {
    "GD.AT": "Γενικός Δείκτης",
    "ELPE.AT": "Ελληνικά Πετρέλαια",
}
GREEK_DAYS = {
    0: "Δευτέρα",
    1: "Τρίτη",
    2: "Τετάρτη",
    3: "Πέμπτη",
    4: "Παρασκευή",
    5: "Σάββατο",
    6: "Κυριακή",
}
EMAIL_SENDER = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")
RECEIVER_EMAIL = "georgakvagel@gmail.com"  # ΣΤΑΘΕΡΟΣ ΠΑΡΑΛΗΠΤΗΣ
# -----------------------------


def greek_day_name(dt):
    return GREEK_DAYS[dt.weekday()]


def get_history(symbol, start, end, interval="1d"):
    """
    Fetch OHLCV data from Yahoo Finance JSON API.
    Returns DataFrame με στήλες Open, High, Low, Close, Volume.
    """
    period1 = int(time.mktime(datetime.combine(start, datetime.min.time()).timetuple()))
    period2 = int(time.mktime(datetime.combine(end, datetime.min.time()).timetuple()))

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"interval": interval, "period1": period1, "period2": period2}

    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    data = r.json()["chart"]["result"][0]

    timestamps = data["timestamp"]
    quotes = data["indicators"]["quote"][0]

    df = pd.DataFrame({
        "Date": [datetime.fromtimestamp(ts).date() for ts in timestamps],
        "Open": quotes["open"],
        "High": quotes["high"],
        "Low": quotes["low"],
        "Close": quotes["close"],
        "Volume": quotes["volume"],
    })
    df.set_index("Date", inplace=True)
    return df


def weekly_report_with_plot(ticker_symbol):
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)

    # Εβδομάδα που πέρασε (Δευτέρα→Παρασκευή)
    last_monday = now - timedelta(days=now.weekday() + 7)
    last_saturday = last_monday + timedelta(days=6)
    start = last_monday.date()
    end = (last_saturday + timedelta(days=1)).date()

    df = get_history(ticker_symbol, start=start, end=end, interval="1d")
    if df.empty:
        print(f"Δεν βρέθηκαν δεδομένα για {TICKER_MAP[ticker_symbol]}")
        return None

    rows = []
    for date, row in df.iterrows():
        rows.append({
            "Ημερομηνία": date,
            "Ημέρα": greek_day_name(datetime.combine(date, datetime.min.time())),
            "Close": float(row["Close"])
        })

    part = pd.DataFrame(rows).sort_values("Ημερομηνία")
    day_order = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή"]
    present_days = [d for d in day_order if d in part["Ημέρα"].unique()]

    close_row = part.set_index("Ημέρα")["Close"].reindex(present_days)

    report = pd.DataFrame(
        [close_row.values],
        index=["Τιμή Κλεισίματος"],
        columns=present_days
    )

    def fmt(x):
        if pd.isna(x):
            return ""
        return f"{x:.2f}"

    report_fmt = report.map(fmt)
    last_close = part["Close"].iloc[-1]

    # Δημιουργία figure
    fig, (ax_table, ax_plot) = plt.subplots(
        nrows=2, figsize=(10, 6), gridspec_kw={"height_ratios": [1, 2]}
    )

    ax_table.axis("off")
    table = ax_table.table(
        cellText=report_fmt.values,
        colLabels=report_fmt.columns,
        rowLabels=report_fmt.index,
        cellLoc="center",
        loc="center"
    )
    table.scale(1.2, 1.8)
    for key, cell in table.get_celld().items():
        cell.set_fontsize(12)
        cell.set_text_props(weight='bold')

    ax_table.set_title(
        f"Εβδομαδιαίο Report — {TICKER_MAP[ticker_symbol]} ({last_close:.2f}€)",
        fontsize=16, fontweight='bold', pad=10
    )

    labels = [f"{d} ({day})" for d, day in zip(part["Ημερομηνία"].astype(str), part["Ημέρα"])]
    ax_plot.plot(labels, part["Close"], marker="o")
    ax_plot.set_title(f"{TICKER_MAP[ticker_symbol]} — Τιμή Κλεισίματος (Εβδομάδα)",
                      fontsize=14, fontweight='bold')
    ax_plot.set_xlabel("Ημερομηνία (Ημέρα)")
    ax_plot.set_ylabel("Τιμή Κλεισίματος (€)")
    ax_plot.grid(True)
    ax_plot.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax_plot.yaxis.set_major_locator(mticker.MaxNLocator(nbins=8))
    plt.setp(ax_plot.get_xticklabels(), rotation=45, ha="right")

    plt.tight_layout()

    os.makedirs("weekly_reports", exist_ok=True)
    filename = f"weekly_reports/{TICKER_MAP[ticker_symbol].replace(' ', '_')}_report.jpg"
    plt.savefig(filename, dpi=300, bbox_inches="tight", format="jpeg")
    plt.close(fig)

    print(f"💾 Αποθηκεύτηκε JPEG: {filename}")
    return filename


def send_email_with_reports(files):
    now = datetime.now()
    subject = "📊 Εβδομαδιαία Reports — Γενικός Δείκτης & Ελληνικά Πετρέλαια"
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    for file_path in files:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                img_data = f.read()
            part = MIMEImage(img_data, _subtype="jpeg")
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
            msg.attach(part)
        else:
            print(f"⚠️ Δεν βρέθηκε το αρχείο: {file_path}")

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.sendmail(EMAIL_SENDER, RECEIVER_EMAIL, msg.as_string())
    server.quit()

    print(f"📩 Email στάλθηκε στο {RECEIVER_EMAIL} στις {now.strftime('%H:%M:%S')}")


def main_loop():
    tz = pytz.timezone(TIMEZONE)
    
    now = datetime.now(tz)
    print(f"[{now}] Checking...")

    print("📌 Δημιουργία εβδομαδιαίων reports...")
    file1 = weekly_report_with_plot("GD.AT")
    file2 = weekly_report_with_plot("ELPE.AT")
    if file1 and file2:
        send_email_with_reports([file1, file2])
    else:
        print("⚠️ Δεν δημιουργήθηκαν τα reports.")

    


if __name__ == "__main__":
    main_loop()



