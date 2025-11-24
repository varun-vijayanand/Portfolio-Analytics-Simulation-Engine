# src/report_generator.py
import pandas as pd
import xlsxwriter
from fpdf import FPDF
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
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
        format_headers(workbook, worksheet, len(summary_df.columns))
    
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
        format_headers(workbook, worksheet, len(risk_df.columns))
    
    def _create_performance_sheet(self, writer, workbook, results):
        """Create performance analysis sheet"""
        # Add performance time series if available
        if 'returns' in results:
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
        format_headers(workbook, worksheet, len(factor_df.columns))
    
    def generate_pdf_report(self, analysis_results, file_path):
        """Generate PDF risk report"""
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

def format_headers(workbook, worksheet, num_cols):
    """Format Excel worksheet headers"""
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1
    })
    
    for col in range(num_cols):
        worksheet.write(0, col, worksheet.cell(0, col).value, header_format)