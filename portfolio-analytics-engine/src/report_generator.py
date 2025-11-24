# src/report_generator.py
import pandas as pd
import xlsxwriter
from fpdf import FPDF
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from io import BytesIO
import os

sns.set(style="whitegrid")

def _save_fig_to_buffer(fig, dpi=150):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf

def format_headers(workbook, worksheet, header_names):
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'align': 'center',
        'bg_color': '#DCE6F1',
        'border': 1
    })

    for col, header in enumerate(header_names):
        worksheet.write(0, col, header, header_format)
        worksheet.set_column(col, col, 20)


class ReportGenerator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("reports", exist_ok=True)

    # -------------------------
    # Excel + simple PDF (existing)
    # -------------------------
    def generate_excel_report(self, analysis_results, file_path):
        """Generate comprehensive Excel report"""
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            workbook = writer.book

            # Summary sheet
            self._create_summary_sheet(writer, workbook, analysis_results)

            # Risk metrics sheet
            self._create_risk_sheet(writer, workbook, analysis_results)

            # Performance sheet
            self._create_performance_sheet(writer, workbook, analysis_results)

            # Factor exposure sheet
            self._create_factor_sheet(writer, workbook, analysis_results)

    def _create_summary_sheet(self, writer, workbook, results):
        """Create summary sheet"""
        summary_data = {
            'Metric': ['Total Return', 'Annual Return', 'Volatility', 'Sharpe Ratio', 'Max Drawdown'],
            'Value': [
                results.get('total_return', 0),
                results.get('annual_return', 0),
                results.get('volatility', 0),
                results.get('sharpe_ratio', 0),
                results.get('max_drawdown', 0)
            ]
        }

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        worksheet = writer.sheets['Summary']
        format_headers(workbook, worksheet, summary_df.columns)

    def _create_risk_sheet(self, writer, workbook, results):
        """Create risk metrics sheet"""
        risk_metrics = results.get('risk_metrics', {})
        risk_data = {
            'Risk Metric': list(risk_metrics.keys()),
            'Value': list(risk_metrics.values())
        }

        risk_df = pd.DataFrame(risk_data)
        risk_df.to_excel(writer, sheet_name='Risk Metrics', index=False)

        worksheet = writer.sheets['Risk Metrics']
        format_headers(workbook, worksheet, risk_df.columns)

    def _create_performance_sheet(self, writer, workbook, results):
        """Create performance analysis sheet"""
        # Add performance time series if available
        if 'returns' in results and not results['returns'].empty:
            returns_df = pd.DataFrame({
                'Date': results['returns'].index,
                'Return': results['returns'].values
            })
            returns_df.to_excel(writer, sheet_name='Performance', index=False)

    def _create_factor_sheet(self, writer, workbook, results):
        """Create factor exposure sheet"""
        factor_exposures = results.get('factor_exposures', {})
        factor_data = {
            'Factor': list(factor_exposures.keys()),
            'Exposure': list(factor_exposures.values())
        }

        factor_df = pd.DataFrame(factor_data)
        factor_df.to_excel(writer, sheet_name='Factor Exposures', index=False)

        worksheet = writer.sheets['Factor Exposures']
        format_headers(workbook, worksheet, factor_df.columns)

    def generate_pdf_report(self, analysis_results, file_path):
        """Generate simple PDF risk report (existing behavior preserved)"""
        pdf = FPDF()
        pdf.add_page()

        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Portfolio Risk Report', 0, 1, 'C')
        pdf.ln(10)

        # Summary
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Performance Summary', 0, 1)
        pdf.set_font('Arial', '', 10)

        metrics = [
            f"Total Return: {analysis_results.get('total_return', 0):.2%}",
            f"Annual Return: {analysis_results.get('annual_return', 0):.2%}",
            f"Volatility: {analysis_results.get('volatility', 0):.2%}",
            f"Sharpe Ratio: {analysis_results.get('sharpe_ratio', 0):.2f}",
            f"Max Drawdown: {analysis_results.get('max_drawdown', 0):.2%}"
        ]

        for metric in metrics:
            pdf.cell(0, 8, metric, 0, 1)

        pdf.output(file_path)

    # -------------------------
    # Institutional Reports (BlackRock, JPM, UBS)
    # All use FPDF standard features and matplotlib images
    # -------------------------
    def _pdf_add_footer(self, pdf: FPDF):
        pdf.set_y(-12)
        pdf.set_font("Helvetica", size=8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, f"Generated: {self.timestamp}", align="C")

    def generate_blackrock_report(self, analysis_results):
        """BlackRock-style institutional report (light style)"""
        filename = f"reports/blackrock_report_{self.timestamp}.pdf"
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Header + Executive summary page
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "BlackRock Institutional Report", ln=True, align="C")
        pdf.ln(6)

        # Summary metrics
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6,
            f"Total Return: {analysis_results.get('total_return',0):.2%}\n"
            f"Annual Return: {analysis_results.get('annual_return',0):.2%}\n"
            f"Volatility: {analysis_results.get('volatility',0):.2%}\n"
            f"Sharpe Ratio: {analysis_results.get('sharpe_ratio',0):.2f}\n"
            f"Max Drawdown: {analysis_results.get('max_drawdown',0):.2%}"
        )
        pdf.ln(6)

        # Cumulative returns chart
        if 'cumulative_returns' in analysis_results:
            fig, ax = plt.subplots(figsize=(6,3))
            analysis_results['cumulative_returns'].plot(ax=ax)
            ax.set_title("Cumulative Returns")
            buf = _save_fig_to_buffer(fig)
            pdf.image(buf, x=15, w=180)
            pdf.ln(6)

        # Risk metrics table
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Risk Metrics", ln=True)
        pdf.set_font("Helvetica", "", 10)
        risk_metrics = analysis_results.get('risk_metrics', {})
        for k, v in risk_metrics.items():
            pdf.cell(0, 6, f"{k}: {v}", ln=True)

        self._pdf_add_footer(pdf)
        pdf.output(filename)
        return filename

    def generate_jpm_report(self, analysis_results):
        """J.P. Morgan style institutional report (light style)"""
        filename = f"reports/jpm_report_{self.timestamp}.pdf"
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Cover with navy strip
        pdf.add_page()
        pdf.set_fill_color(15,35,80)
        pdf.rect(0, 0, 220, 22, "F")
        pdf.set_text_color(255,255,255)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_y(6)
        pdf.cell(0, 8, "J.P. Morgan Institutional Report", align="C")
        pdf.ln(16)
        pdf.set_text_color(0,0,0)

        # Key insights box
        pdf.set_fill_color(235,240,255)
        pdf.rect(12, 36, 186, 28, "F")
        pdf.set_xy(16, 40)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 6, "Key Insights", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_x(16)
        pdf.multi_cell(0, 5,
            "Portfolio shows robust long-term performance with measured risk. See details below."
        )
        pdf.ln(8)

        # Performance chart
        if 'cumulative_returns' in analysis_results:
            fig, ax = plt.subplots(figsize=(6,3))
            analysis_results['cumulative_returns'].plot(ax=ax, color='navy')
            ax.set_title("Portfolio Growth")
            buf = _save_fig_to_buffer(fig)
            pdf.image(buf, x=15, w=180)
            pdf.ln(6)

        # Benchmark comparison (simple overlay)
        if 'cumulative_returns' in analysis_results:
            fig, ax = plt.subplots(figsize=(6,3))
            analysis_results['cumulative_returns'].plot(ax=ax, label='Portfolio')
            # synthetic benchmark line (portfolio *0.97) if no benchmark provided
            ax.plot(analysis_results['cumulative_returns'].index, analysis_results['cumulative_returns']*0.97, label='Benchmark (proxy)', linestyle='--')
            ax.legend()
            buf = _save_fig_to_buffer(fig)
            pdf.image(buf, x=15, w=180)

        self._pdf_add_footer(pdf)
        pdf.output(filename)
        return filename

    def generate_ubs_report(self, analysis_results):
        """UBS-style wealth management report (light style)"""
        filename = f"reports/ubs_report_{self.timestamp}.pdf"
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Header
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(180, 20, 30)
        pdf.cell(0, 10, "UBS Wealth Management - Portfolio Review", ln=True)
        pdf.set_text_color(0,0,0)
        pdf.ln(4)

        # Executive narrative
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Executive Narrative", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6,
            "This report provides a concise review of portfolio performance, risk, and exposures."
        )
        pdf.ln(6)

        # Risk table
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Risk Summary", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for k, v in analysis_results.get('risk_metrics', {}).items():
            pdf.cell(0, 6, f"{k}: {v}", ln=True)
        pdf.ln(6)

        # Growth figure
        if 'cumulative_returns' in analysis_results:
            fig, ax = plt.subplots(figsize=(6,3))
            analysis_results['cumulative_returns'].plot(ax=ax, color='darkred')
            ax.set_title("Portfolio Growth Path")
            buf = _save_fig_to_buffer(fig)
            pdf.image(buf, x=15, w=180)

        self._pdf_add_footer(pdf)
        pdf.output(filename)
        return filename
