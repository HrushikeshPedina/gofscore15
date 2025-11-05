# import streamlit as st
# import openpyxl
# from openpyxl import Workbook
# from io import BytesIO
# import pandas as pd

# # -----------------------------
# # FUNCTION DEFINITIONS
# # -----------------------------
# def stableford_points(par, score):
#     """Compute Stableford points based on score vs par."""
#     diff = score - par
#     if diff >= 2:
#         return 0
#     elif diff == 1:
#         return 1
#     elif diff == 0:
#         return 2
#     elif diff == -1:
#         return 3
#     elif diff == -2:
#         return 4
#     else:
#         return 5


# def double_peoria_15(pars, scores, ref_holes):
#     """Calculate gross, handicap, and Stableford points."""
#     gross = sum(scores)
#     selected_adjustments = [scores[i - 1] - pars[i - 1] for i in ref_holes]
#     peoria_handicap = sum(selected_adjustments) * 1.5
#     handicap = round(peoria_handicap, 1)
#     hole_points = [stableford_points(par, score) for par, score in zip(pars, scores)]
#     total_points = sum(hole_points)
#     return {
#         "gross": gross,
#         "handicap": handicap,
#         "net": gross - handicap,
#         "hole_points": hole_points,
#         "total_points": total_points,
#     }


# def process_excel(file_bytes, ref_holes):
#     """Process the uploaded Excel and calculate tournament results."""
#     wb_in = openpyxl.load_workbook(BytesIO(file_bytes))
#     ws_in = wb_in.active

#     hole_numbers = [ws_in.cell(row=i, column=1).value for i in range(2, 17)]
#     pars = [ws_in.cell(row=i, column=2).value for i in range(2, 17)]
#     player_names = [ws_in.cell(row=1, column=j).value for j in range(3, ws_in.max_column + 1)]

#     wb_out = Workbook()
#     ws_out = wb_out.active
#     ws_out.title = "Results"

#     summary = []
#     row = 1

#     for idx, col in enumerate(range(3, ws_in.max_column + 1)):
#         name = player_names[idx]
#         scores = [ws_in.cell(row=i, column=col).value for i in range(2, 17)]
#         result = double_peoria_15(pars, scores, ref_holes)

#         ws_out.cell(row=row, column=1, value=name)
#         row += 1
#         ws_out.append(["Hole", "Par", "Score", "Stableford Points"])
#         for i in range(15):
#             ws_out.append([
#                 hole_numbers[i],
#                 pars[i],
#                 scores[i],
#                 result["hole_points"][i],
#             ])
#         row = ws_out.max_row + 1
#         ws_out.append(["Gross Score", result["gross"]])
#         ws_out.append(["Handicap (Double Peoria)", result["handicap"]])
#         ws_out.append(["Net Score", result["net"]])
#         ws_out.append(["Total Stableford Points", result["total_points"]])
#         row = ws_out.max_row + 2

#         summary.append({
#             "Player": name,
#             "Gross": result["gross"],
#             "Handicap": result["handicap"],
#             "Net": result["net"],
#             "Stableford Points": result["total_points"]
#         })

#     # Rankings
#     min_gross = min(p["Gross"] for p in summary)
#     best_gross_players = [p for p in summary if p["Gross"] == min_gross]

#     group_best = []
#     for i in range(0, len(summary), 4):
#         group = summary[i:i + 4]
#         min_group_gross = min(p["Gross"] for p in group)
#         best_in_group = [p for p in group if p["Gross"] == min_group_gross]
#         group_best.append(best_in_group)

#     top_stableford = sorted(summary, key=lambda x: x["Stableford Points"], reverse=True)[:10]

#     # Summary sheet
#     ws_out.append(["🏁 Tournament Summary"])
#     ws_out.append(["Player", "Gross", "Handicap", "Net", "Stableford Points"])
#     for s in summary:
#         ws_out.append([s["Player"], s["Gross"], s["Handicap"], s["Net"], s["Stableford Points"]])

#     ws_out.append([])
#     ws_out.append(["🏆 Overall Best Gross Score"])
#     for p in best_gross_players:
#         ws_out.append([p["Player"], p["Gross"]])

#     ws_out.append([])
#     ws_out.append(["🥇 Best Gross from Each Group of 4"])
#     for idx, group in enumerate(group_best, start=1):
#         for g in group:
#             ws_out.append([f"Group {idx}", g["Player"], g["Gross"]])

#     ws_out.append([])
#     ws_out.append(["🏅 Top 10 Stableford Players"])
#     for idx, t in enumerate(top_stableford, start=1):
#         ws_out.append([f"#{idx}", t["Player"], t["Stableford Points"]])

#     output = BytesIO()
#     wb_out.save(output)
#     output.seek(0)

#     return summary, best_gross_players, group_best, top_stableford, output


# # -----------------------------
# # STREAMLIT UI
# # -----------------------------
# st.set_page_config(page_title="Golf Tournament Calculator", layout="wide")

# st.title("🏌️‍♂️ Double Peoria Stableford Calculator (15 Holes)")

# uploaded_file = st.file_uploader("📤 Upload Scorecard Excel File", type=["xlsx"])

# if uploaded_file:
#     st.success("✅ File uploaded successfully!")
#     st.markdown("### 🎯 Select 10 Peoria Holes")

#     cols = st.columns(5)
#     selected_holes = []
#     for i in range(15):
#         with cols[i % 5]:
#             if st.checkbox(f"Hole {i + 1}", value=False):
#                 selected_holes.append(i + 1)

#     if st.button("🚀 Calculate Results"):
#         if len(selected_holes) != 10:
#             st.error("❌ Please select exactly 10 Peoria holes.")
#         else:
#             with st.spinner("Processing..."):
#                 summary, best_gross_players, group_best, top_stableford, output = process_excel(
#                     uploaded_file.read(), selected_holes
#                 )

#             st.success("✅ Results calculated successfully!")

#             st.subheader("🏁 Tournament Summary")
#             df_summary = pd.DataFrame(summary)
#             st.dataframe(df_summary, use_container_width=True)

#             st.subheader("🏆 Overall Best Gross Score")
#             for p in best_gross_players:
#                 st.write(f"- **{p['Player']}** — {p['Gross']}")

#             st.subheader("🥇 Best Gross from Each Group of 4")
#             for idx, group in enumerate(group_best, start=1):
#                 st.write(f"**Group {idx}:** " + ", ".join(f"{g['Player']} ({g['Gross']})" for g in group))

#             st.subheader("🏅 Top 10 Stableford Players")
#             df_top10 = pd.DataFrame(top_stableford)
#             st.table(df_top10)

#             st.download_button(
#                 label="📥 Download Results Excel File",
#                 data=output,
#                 file_name="golf_results.xlsx",
#                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             )

# else:
#     st.info("Please upload your scorecard to continue.")






import streamlit as st
import openpyxl
from openpyxl import Workbook
from io import BytesIO
import pandas as pd
import plotly.express as px

# -----------------------------
# FUNCTIONS
# -----------------------------
def stableford_points(par, score):
    diff = score - par
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


def double_peoria_15(pars, scores, ref_holes):
    gross = sum(scores)
    selected_adjustments = [scores[i - 1] - pars[i - 1] for i in ref_holes]
    peoria_handicap = sum(selected_adjustments) * 1.5
    handicap = round(peoria_handicap, 1)
    hole_points = [stableford_points(par, score) for par, score in zip(pars, scores)]
    total_points = sum(hole_points)
    return {
        "gross": gross,
        "handicap": handicap,
        "net": gross - handicap,
        "hole_points": hole_points,
        "total_points": total_points,
    }


def process_excel(file_bytes, ref_holes):
    wb_in = openpyxl.load_workbook(BytesIO(file_bytes))
    ws_in = wb_in.active

    hole_numbers = [ws_in.cell(row=i, column=1).value for i in range(2, 17)]
    pars = [ws_in.cell(row=i, column=2).value for i in range(2, 17)]
    player_names = [ws_in.cell(row=1, column=j).value for j in range(3, ws_in.max_column + 1)]

    wb_out = Workbook()
    ws_out = wb_out.active
    ws_out.title = "Results"

    summary = []
    row = 1

    for idx, col in enumerate(range(3, ws_in.max_column + 1)):
        name = player_names[idx]
        scores = [ws_in.cell(row=i, column=col).value for i in range(2, 17)]
        result = double_peoria_15(pars, scores, ref_holes)

        ws_out.cell(row=row, column=1, value=name)
        row += 1
        ws_out.append(["Hole", "Par", "Score", "Stableford Points"])
        for i in range(15):
            ws_out.append([
                hole_numbers[i],
                pars[i],
                scores[i],
                result["hole_points"][i],
            ])
        row = ws_out.max_row + 1
        ws_out.append(["Gross Score", result["gross"]])
        ws_out.append(["Handicap (Double Peoria)", result["handicap"]])
        ws_out.append(["Net Score", result["net"]])
        ws_out.append(["Total Stableford Points", result["total_points"]])
        row = ws_out.max_row + 2

        summary.append({
            "Player": name,
            "Gross": result["gross"],
            "Handicap": result["handicap"],
            "Net": result["net"],
            "Stableford Points": result["total_points"]
        })

    min_gross = min(p["Gross"] for p in summary)
    best_gross_players = [p for p in summary if p["Gross"] == min_gross]

    group_best = []
    for i in range(0, len(summary), 4):
        group = summary[i:i + 4]
        min_group_gross = min(p["Gross"] for p in group)
        best_in_group = [p for p in group if p["Gross"] == min_group_gross]
        group_best.append(best_in_group)

    top_stableford = sorted(summary, key=lambda x: x["Stableford Points"], reverse=True)[:10]

    ws_out.append(["🏁 Tournament Summary"])
    ws_out.append(["Player", "Gross", "Handicap", "Net", "Stableford Points"])
    for s in summary:
        ws_out.append([s["Player"], s["Gross"], s["Handicap"], s["Net"], s["Stableford Points"]])

    ws_out.append([])
    ws_out.append(["🏆 Overall Best Gross Score"])
    for p in best_gross_players:
        ws_out.append([p["Player"], p["Gross"]])

    ws_out.append([])
    ws_out.append(["🥇 Best Gross from Each Group of 4"])
    for idx, group in enumerate(group_best, start=1):
        for g in group:
            ws_out.append([f"Group {idx}", g["Player"], g["Gross"]])

    ws_out.append([])
    ws_out.append(["🏅 Top 10 Stableford Players"])
    for idx, t in enumerate(top_stableford, start=1):
        ws_out.append([f"#{idx}", t["Player"], t["Stableford Points"]])

    output = BytesIO()
    wb_out.save(output)
    output.seek(0)

    return summary, best_gross_players, group_best, top_stableford, output


# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Golf Tournament Calculator", layout="wide")

# Background & style
st.markdown("""
    <style>
    .main {
        background-image: url("https://images.unsplash.com/photo-1590411842264-749b748b570e?auto=format&fit=crop&w=1600&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .block-container {
        background-color: rgba(255, 255, 255, 0.92);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #14532d;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⛳ Double Peoria Stableford Calculator (15 Holes)")
st.write("Upload your scorecard, select 10 Peoria holes, and get instant results, charts, and downloadable reports!")

uploaded_file = st.file_uploader("📤 Upload Scorecard Excel File", type=["xlsx"])

if uploaded_file:
    st.success("✅ File uploaded successfully!")
    st.markdown("### 🎯 Select 10 Peoria Holes")

    cols = st.columns(5)
    selected_holes = []
    for i in range(15):
        with cols[i % 5]:
            if st.checkbox(f"Hole {i + 1}", value=False):
                selected_holes.append(i + 1)

    if st.button("🚀 Calculate Results"):
        if len(selected_holes) != 10:
            st.error("❌ Please select exactly 10 Peoria holes.")
        else:
            with st.spinner("Processing tournament results..."):
                summary, best_gross_players, group_best, top_stableford, output = process_excel(
                    uploaded_file.read(), selected_holes
                )

            st.balloons()
            st.success("✅ Results calculated successfully!")

            # Display results
            df_summary = pd.DataFrame(summary)
            st.subheader("🏁 Tournament Summary")
            st.dataframe(df_summary, use_container_width=True)

            # Charts
            st.subheader("📊 Visual Analysis")
            col1, col2 = st.columns(2)

            with col1:
                fig_gross = px.bar(df_summary, x="Player", y="Gross", color="Gross",
                                   title="Gross Scores by Player", text="Gross")
                st.plotly_chart(fig_gross, use_container_width=True)

            with col2:
                fig_stableford = px.bar(df_summary, x="Player", y="Stableford Points", color="Stableford Points",
                                        title="Stableford Points by Player", text="Stableford Points")
                st.plotly_chart(fig_stableford, use_container_width=True)

            # Best Gross
            st.subheader("🏆 Overall Best Gross Score")
            for p in best_gross_players:
                st.write(f"- **{p['Player']}** — {p['Gross']}")

            # Group bests
            st.subheader("🥇 Best Gross from Each Group of 4")
            for idx, group in enumerate(group_best, start=1):
                st.write(f"**Group {idx}:** " + ", ".join(f"{g['Player']} ({g['Gross']})" for g in group))

            # Top Stableford
            st.subheader("🏅 Top 10 Stableford Players")
            df_top10 = pd.DataFrame(top_stableford)
            st.table(df_top10)

            # Download
            st.download_button(
                label="📥 Download Full Results (Excel)",
                data=output,
                file_name="golf_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

else:
    st.info("Please upload your scorecard Excel file to continue.")

