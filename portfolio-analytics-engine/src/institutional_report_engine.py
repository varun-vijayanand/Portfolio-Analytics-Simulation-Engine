import os
from fpdf import FPDF
import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd

from .llm_narrative import NarrativeGenerator
from .sql_engine import SQLMetadataLogger

def _to_buf(fig, dpi=150):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf

class InstitutionalReportEngine:
    """Creates a blended institutional report with 3 sections."""

    def __init__(self, outdir="reports"):
        os.makedirs(outdir, exist_ok=True)
        os.makedirs("governance", exist_ok=True)
        self.outdir = outdir
        self.ts = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        self.narr = NarrativeGenerator()
        self.db = SQLMetadataLogger()

    def generate(self, results):
        outpath = f"{self.outdir}/institutional_blended_{self.ts}.pdf"

        # Log run
        run_id = self.db.log_run(
            report_name=outpath,
            total_return=results.get("total_return"),
            annual_return=results.get("annual_return"),
            volatility=results.get("volatility")
        )

        # Generate narratives
        exec_text = self.narr.generate_executive(results)
        mkt_text  = self.narr.generate_market(results)
        risk_text = self.narr.generate_risk(results)

        # Store in DB
        self.db.log_narrative(run_id, "executive", exec_text)
        self.db.log_narrative(run_id, "market", mkt_text)
        self.db.log_narrative(run_id, "risk", risk_text)

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        # ================= BLACKROCK =====================
        pdf.add_page()
        pdf.set_font("Helvetica","B",16)
        pdf.cell(0, 10, "BlackRock Institutional Section", ln=True, align="C")
        pdf.ln(4)

        pdf.set_font("Helvetica","",11)
        pdf.multi_cell(0, 6, exec_text)
        pdf.ln(4)

        if "cumulative_returns" in results:
            fig, ax = plt.subplots(figsize=(6,3))
            results["cumulative_returns"].plot(ax=ax)
            ax.set_title("Cumulative Returns")
            pdf.image(_to_buf(fig), x=15, w=180)

        # ================= JP MORGAN =====================
        pdf.add_page()
        pdf.set_fill_color(15,35,80)
        pdf.rect(0, 0, 220, 18, "F")
        pdf.set_text_color(255,255,255)
        pdf.set_font("Helvetica","B",16)
        pdf.set_y(4)
        pdf.cell(0, 10, "J.P. Morgan Section", align="C")
        pdf.set_text_color(0,0,0)
        pdf.ln(20)

        pdf.set_font("Helvetica","B",12)
        pdf.cell(0, 8, "Market Commentary", ln=True)
        pdf.set_font("Helvetica","",10)
        pdf.multi_cell(0, 6, mkt_text)

        if "cumulative_returns" in results:
            fig, ax = plt.subplots(figsize=(6,3))
            results["cumulative_returns"].plot(ax=ax, label="Portfolio")
            ax.plot(results["cumulative_returns"].index,
                    results["cumulative_returns"]*0.97,
                    linestyle="--", label="Benchmark Proxy")
            ax.legend()
            ax.set_title("Portfolio vs Benchmark")
            pdf.image(_to_buf(fig), x=15, w=180)

        # ================= UBS =====================
        pdf.add_page()
        pdf.set_font("Helvetica","B",16)
        pdf.set_text_color(180,20,30)
        pdf.cell(0, 10, "UBS Wealth Management Section", ln=True)
        pdf.set_text_color(0,0,0)
        pdf.ln(4)

        pdf.set_font("Helvetica","B",12)
        pdf.cell(0, 8, "Risk Commentary", ln=True)
        pdf.set_font("Helvetica","",10)
        pdf.multi_cell(0, 6, risk_text)

        if "cumulative_returns" in results:
            fig, ax = plt.subplots(figsize=(6,3))
            results["cumulative_returns"].plot(ax=ax, color="darkred")
            ax.set_title("Portfolio Growth Path")
            pdf.image(_to_buf(fig), x=15, w=180)

        # Footer
        pdf.set_y(-12)
        pdf.set_font("Helvetica", size=8)
        pdf.set_text_color(100,100,100)
        pdf.cell(0,8, f"Generated: {self.ts}", align="C")

        pdf.output(outpath)
        return outpath
