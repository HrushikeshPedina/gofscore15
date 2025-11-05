import streamlit as st
import openpyxl
from openpyxl import Workbook
from io import BytesIO
import pandas as pd

# -----------------------------
# FUNCTION DEFINITIONS
# -----------------------------
def stableford_points(par, score):
    """Compute Stableford points based on score vs par."""
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
    """Calculate gross, handicap, and Stableford points."""
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
    """Process the uploaded Excel and calculate tournament results."""
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

    # Rankings
    min_gross = min(p["Gross"] for p in summary)
    best_gross_players = [p for p in summary if p["Gross"] == min_gross]

    group_best = []
    for i in range(0, len(summary), 4):
        group = summary[i:i + 4]
        min_group_gross = min(p["Gross"] for p in group)
        best_in_group = [p for p in group if p["Gross"] == min_group_gross]
        group_best.append(best_in_group)

    top_stableford = sorted(summary, key=lambda x: x["Stableford]()_
