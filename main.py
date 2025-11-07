import streamlit as st
import pandas as pd
import openpyxl
from openpyxl import Workbook
import io
import matplotlib.pyplot as plt

st.set_page_config(page_title="Golf Tournament – Double Peoria", layout="wide")

# ---------------------------------------------
# PAGE STYLE (Dark Blue + White Text)
# ---------------------------------------------
st.markdown("""
    <style>
        body, .stApp {
            background-color: #001F3F !important;
            color: white !important;
        }
        .stButton>button {
            background-color: #004080;
            color: white;
            border-radius: 8px;
            border: 1px solid #1E90FF;
        }
        .stDownloadButton>button {
            background-color: #0066CC;
            color: white;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------
# STABLEFORD CALCULATION
# ---------------------------------------------
def stableford_points(par, net_score):
    diff = net_score - par
    if diff >= 2:
        return 0
    elif diff == 1:
        return 1
    elif diff == 0:
        return 2
    elif diff == -1:
        return 3
    elif diff == -2:
        return 4
    else:
        return 5

# ---------------------------------------------
# DOUBLE PEORIA WITH HANDICAP DISTRIBUTION
# ---------------------------------------------
def double_peoria_calculation(pars, stroke_index, scores, peoria_holes):
    gross = sum(scores)

    # Peoria selected hole adjustments
    adjustments = [(scores[i - 1] - pars[i - 1]) for i in peoria_holes]
    peoria_handicap = round(sum(adjustments) * 1.5, 1)
    total_handicap_strokes = int(round(peoria_handicap))

    # Stroke distribution based on difficulty
    strokes_per_hole = [0] * 15
    idx_sorted = sorted(range(15), key=lambda i: stroke_index[i])

    stroke_count = total_handicap_strokes
    while stroke_count > 0:
        for idx in idx_sorted:
            strokes_per_hole[idx] += 1
            stroke_count -= 1
            if stroke_count == 0:
                break

    # Net scores and Stableford points
    net_scores = [scores[i] - strokes_per_hole[i] for i in range(15)]
    points = [stableford_points(pars[i], net_scores[i]) for i in range(15)]

    return {
        "gross": gross,
        "handicap": peoria_handicap,
        "net_total": gross - peoria_handicap,
        "hole_net_scores": net_scores,
        "hole_points": points,
        "total_points": sum(points),
        "strokes_per_hole": strokes_per_hole
    }


# ---------------------------------------------
# PROCESS WORKBOOK
# ---------------------------------------------
def process_workbook_bytes(xls_bytes, peoria_holes):

    wb = openpyxl.load_workbook(io.BytesIO(xls_bytes))
    ws = wb.active

    hole_numbers = [ws.cell(row=i, column=1).value for i in range(2, 17)]
    pars = [ws.cell(row=i, column=2).value for i in range(2, 17)]
    stroke_idx = [ws.cell(row=i, column=3).value for i in range(2, 17)]

    players = [ws.cell(row=1, col).value for col in range(4, ws.max_column + 1)]
    results = []

    for col_idx, col in enumerate(range(4, ws.max_column + 1)):
        name = players[col_idx]
        scores = [ws.cell(row=i, column=col).value for i in range(2, 17)]

        r = double_peoria_calculation(pars, stroke_idx, scores, peoria_holes)

        results.append({
            "Player": name,
            "Gross": r["gross"],
            "Handicap": r["handicap"],
            "Net_Total": r["net_total"],
            "Total_Stableford": r["total_points"],
            "Raw": r
        })

    # Rankings
    best_gross = min(r["Gross"] for r in results)
    best_gross_players = [r for r in results if r["Gross"] == best_gross]

    group_best = []
    for i in range(0, len(results), 4):
        group = results[i:i+4]
        best = min(r["Gross"] for r in group)
        winners = [r for r in group if r["Gross"] == best]
        group_best.append(winners)

    top_stableford = sorted(results, key=lambda x: x["Total_Stableford"], reverse=True)[:10]
    top_5_net = sorted(results, key=lambda x: x["Net_Total"])[:5]

    # OUTPUT EXCEL
    wb_out = Workbook()
    ws_out = wb_out.active
    ws_out.title = "Results"

    ws_out.append(["Player", "Gross", "Handicap", "Net", "Stableford Points"])
    for r in results:
        ws_out.append([r["Player"], r["Gross"], r["Handicap"], r["Net_Total"], r["Total_Stableford"]])

    ws_out.append([])
    ws_out.append(["Overall Best Gross"])
    for bg in best_gross_players:
        ws_out.append([bg["Player"], bg["Gross"]])

    ws_out.append([])
    ws_out.append(["Best by Group of 4"])
    for g_idx, grp in enumerate(group_best, start=1):
        for p in grp:
            ws_out.append([f"Group {g_idx}", p["Player"], p["Gross"]])

    ws_out.append([])
    ws_out.append(["Top 10 Stableford"])
    for i, p in enumerate(top_stableford, start=1):
        ws_out.append([i, p["Player"], p["Total_Stableford"]])

    ws_out.append([])
    ws_out.append(["Top 5 Net Score"])
    for i, p in enumerate(top_5_net, start=1):
        ws_out.append([i, p["Player"], p["Net_Total"]])

    out_bytes = io.BytesIO()
    wb_out.save(out_bytes)
    out_bytes.seek(0)

    return {
        "results": results,
        "best_gross": best_gross_players,
        "group_best": group_best,
        "top_stableford": top_stableford,
        "top_5_net": top_5_net,
        "excel_bytes": out_bytes
    }


# ---------------------------------------------
# STREAMLIT APP LAYOUT
# ---------------------------------------------
st.title("🏌️ Double Peoria Stableford – 15 Holes Tournament")
st.subheader("Dark Blue Theme • Handicap Distribution • Stableford Charts")

file = st.file_uploader("Upload Score Sheet (Excel – score_card_new.xlsx)", type=["xlsx"])

peoria_holes = st.multiselect(
    "Select 10 Peoria Holes",
    list(range(1, 16)),
    max_selections=10
)

if len(peoria_holes) != 10:
    st.warning("Please select exactly **10 holes**.")
    st.stop()

if file:
    result = process_workbook_bytes(file.read(), peoria_holes)

    st.success("✅ Processing Completed!")

    # -----------------------------
    # SUMMARY TABLE
    # -----------------------------
    df = pd.DataFrame([
        {
            "Player": r["Player"],
            "Gross": r["Gross"],
            "Handicap": r["Handicap"],
            "Net Score": r["Net_Total"],
            "Stableford": r["Total_Stableford"]
        }
        for r in result["results"]
    ])

    st.subheader("📊 Player Summary")
    st.dataframe(df)

    # -----------------------------
    # TOP 5 NET SCORE
    # -----------------------------
    st.subheader("🔵 Top 5 Net Score (Lower is Better)")
    df_net = pd.DataFrame([
        {"Rank": i+1, "Player": p["Player"], "Net Score": p["Net_Total"]}
        for i, p in enumerate(result["top_5_net"])
    ])
    st.table(df_net)

    # -----------------------------
    # SIMPLE CHART – Stableford
    # -----------------------------
    st.subheader("📈 Stableford Points Chart")

    fig, ax = plt.subplots()
    ax.bar(df["Player"], df["Stableford"])
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # -----------------------------
    # DOWNLOAD OUTPUT
    # -----------------------------
    st.download_button(
        "📥 Download Tournament Report (Excel)",
        data=result["excel_bytes"],
        file_name="tournament_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
