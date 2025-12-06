"""
PDF Report Generator
Creates professional PDF reports for model results
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Dict, List, Any
import io


class PDFReportGenerator:
    """Generate professional PDF reports for quant model results"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles - safely add only if they don't exist"""
        # Helper function to safely add a style
        def safe_add_style(style_name, style_params):
            try:
                # Check if style already exists
                _ = self.styles[style_name]
                # If we get here, style exists - skip adding
            except KeyError:
                # Style doesn't exist, add it
                try:
                    self.styles.add(ParagraphStyle(name=style_name, **style_params))
                except Exception:
                    # If add fails (e.g., style was added between check and add), that's okay
                    pass
        
        safe_add_style('CustomTitle', {
            'parent': self.styles['Title'],
            'fontSize': 24,
            'spaceAfter': 30,
            'textColor': colors.HexColor('#1a1a2e')
        })
        
        safe_add_style('SectionHeader', {
            'parent': self.styles['Heading2'],
            'fontSize': 14,
            'spaceBefore': 20,
            'spaceAfter': 10,
            'textColor': colors.HexColor('#4a90d9')
        })
        
        safe_add_style('SubHeader', {
            'parent': self.styles['Heading3'],
            'fontSize': 12,
            'spaceBefore': 15,
            'spaceAfter': 8
        })
        
        safe_add_style('BodyText', {
            'parent': self.styles['Normal'],
            'fontSize': 10,
            'spaceAfter': 8,
            'leading': 14
        })
        
        safe_add_style('SmallText', {
            'parent': self.styles['Normal'],
            'fontSize': 8,
            'textColor': colors.grey
        })
    
    def generate_model_report(
        self,
        model_name: str,
        category: str,
        universe: str,
        buy_signals: List[Dict],
        sell_signals: List[Dict],
        total_analyzed: int,
        stocks_with_data: int,
        parameters: Dict,
        description: str = "",
        run_timestamp: str = None
    ) -> bytes:
        """
        Generate a PDF report for model results
        Returns PDF as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Title
        story.append(Paragraph(f"📊 {model_name}", self.styles['CustomTitle']))
        story.append(Paragraph(
            f"Signal Report • {category} Model",
            self.styles['BodyText']
        ))
        
        # Metadata
        if run_timestamp:
            # Parse ISO format timestamp and format it nicely
            try:
                if 'T' in run_timestamp:
                    dt = datetime.fromisoformat(run_timestamp.replace('Z', '+00:00'))
                    timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    timestamp = run_timestamp
            except (ValueError, AttributeError):
                timestamp = run_timestamp
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        meta_text = f"""
        <b>Generated:</b> {timestamp}<br/>
        <b>Universe:</b> {universe.upper()}<br/>
        <b>Stocks Analyzed:</b> {stocks_with_data} / {total_analyzed}
        """
        story.append(Paragraph(meta_text, self.styles['SmallText']))
        story.append(Spacer(1, 20))
        
        # Horizontal line
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        story.append(Spacer(1, 15))
        
        # Model Description
        if description:
            story.append(Paragraph("Model Description", self.styles['SectionHeader']))
            story.append(Paragraph(description, self.styles['BodyText']))
            story.append(Spacer(1, 10))
        
        # Parameters
        if parameters:
            story.append(Paragraph("Parameters", self.styles['SubHeader']))
            param_data = [[k, str(v)] for k, v in parameters.items()]
            param_table = Table(param_data, colWidths=[2*inch, 3*inch])
            param_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('RIGHTPADDING', (0, 0), (0, -1), 15),
            ]))
            story.append(param_table)
            story.append(Spacer(1, 15))
        
        # Summary Stats
        story.append(Paragraph("Summary", self.styles['SectionHeader']))
        summary_data = [
            ['Metric', 'Value'],
            ['Buy Signals', str(len(buy_signals))],
            ['Sell Signals', str(len(sell_signals))],
            ['Stocks with Data', f"{stocks_with_data} / {total_analyzed}"],
            ['Data Coverage', f"{stocks_with_data/total_analyzed*100:.1f}%" if total_analyzed > 0 else "N/A"]
        ]
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90d9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Buy Signals Table
        if buy_signals:
            story.append(Paragraph("🟢 Buy Signals", self.styles['SectionHeader']))
            buy_data = [['Rank', 'Ticker', 'Score', 'Price']]
            for i, signal in enumerate(buy_signals[:15], 1):
                buy_data.append([
                    str(i),
                    signal.get('ticker', '').replace('.BK', ''),
                    f"{signal.get('score', 0):.1f}",
                    f"${signal.get('price_at_signal', 0):.2f}"
                ])
            
            buy_table = Table(buy_data, colWidths=[0.7*inch, 1.5*inch, 1*inch, 1.2*inch])
            buy_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fff4')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(buy_table)
            story.append(Spacer(1, 20))
        
        # Sell Signals Table
        if sell_signals:
            story.append(Paragraph("🔴 Sell Signals", self.styles['SectionHeader']))
            sell_data = [['Rank', 'Ticker', 'Score', 'Price']]
            for i, signal in enumerate(sell_signals[:15], 1):
                sell_data.append([
                    str(i),
                    signal.get('ticker', '').replace('.BK', ''),
                    f"{signal.get('score', 0):.1f}",
                    f"${signal.get('price_at_signal', 0):.2f}"
                ])
            
            sell_table = Table(sell_data, colWidths=[0.7*inch, 1.5*inch, 1*inch, 1.2*inch])
            sell_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc3545')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5f5')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(sell_table)
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "Generated by Quant Stock Analysis Platform • For institutional use only",
            self.styles['SmallText']
        ))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_backtest_report(
        self,
        model_name: str,
        universe: str,
        period: str,
        performance: Dict,
        trades: Dict,
        equity_curve: List[Dict],
        recent_trades: List[Dict],
        parameters: Dict = None
    ) -> bytes:
        """
        Generate a PDF report for backtest results
        Returns PDF as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Title
        story.append(Paragraph(f"📊 Backtest Report: {model_name}", self.styles['CustomTitle']))
        story.append(Paragraph(
            f"Performance Analysis • {universe.upper()}",
            self.styles['BodyText']
        ))
        
        # Metadata
        meta_text = f"""
        <b>Period:</b> {period}<br/>
        <b>Universe:</b> {universe.upper()}<br/>
        <b>Initial Capital:</b> ${performance.get('initial_capital', 0):,.2f}<br/>
        <b>Final Value:</b> ${performance.get('final_value', 0):,.2f}
        """
        story.append(Paragraph(meta_text, self.styles['SmallText']))
        story.append(Spacer(1, 20))
        
        # Horizontal line
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        story.append(Spacer(1, 15))
        
        # Performance Summary
        story.append(Paragraph("Performance Summary", self.styles['SectionHeader']))
        perf_data = [
            ['Metric', 'Value'],
            ['Total Return', f"{performance.get('total_return_pct', 0):.2f}%"],
            ['Annualized Return', f"{performance.get('annualized_return_pct', 0):.2f}%"],
            ['Sharpe Ratio', f"{performance.get('sharpe_ratio', 0):.2f}"],
            ['Max Drawdown', f"{performance.get('max_drawdown_pct', 0):.2f}%"],
            ['Initial Capital', f"${performance.get('initial_capital', 0):,.2f}"],
            ['Final Value', f"${performance.get('final_value', 0):,.2f}"]
        ]
        perf_table = Table(perf_data, colWidths=[2.5*inch, 2*inch])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90d9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(perf_table)
        story.append(Spacer(1, 20))
        
        # Trade Statistics
        story.append(Paragraph("Trade Statistics", self.styles['SectionHeader']))
        trade_data = [
            ['Metric', 'Value'],
            ['Total Trades', str(trades.get('total', 0))],
            ['Winning Trades', str(trades.get('winning', 0))],
            ['Losing Trades', str(trades.get('losing', 0))],
            ['Win Rate', f"{trades.get('win_rate_pct', 0):.1f}%"],
            ['Avg Win', f"{trades.get('avg_win_pct', 0):.2f}%"],
            ['Avg Loss', f"{trades.get('avg_loss_pct', 0):.2f}%"],
            ['Profit Factor', f"{trades.get('profit_factor', 0):.2f}"]
        ]
        trade_table = Table(trade_data, colWidths=[2.5*inch, 2*inch])
        trade_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fff4')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(trade_table)
        story.append(Spacer(1, 20))
        
        # Recent Trades
        if recent_trades and len(recent_trades) > 0:
            story.append(Paragraph(f"All Trades ({len(recent_trades)} total)", self.styles['SectionHeader']))
            trades_data = [['Entry Date', 'Exit Date', 'Ticker', 'Entry', 'Exit', 'Return %', 'P&L']]
            for trade in recent_trades:  # Show all trades, not just 20
                entry_date = trade.get('entry_date', '')
                exit_date = trade.get('exit_date', '')
                # Format dates to be shorter for PDF
                entry_str = entry_date[:10] if entry_date and len(entry_date) >= 10 else entry_date
                exit_str = exit_date[:10] if exit_date and len(exit_date) >= 10 else exit_date
                
                trades_data.append([
                    entry_str,
                    exit_str,
                    trade.get('ticker', '').replace('.BK', ''),
                    f"${trade.get('entry_price', 0):.2f}",
                    f"${trade.get('exit_price', 0):.2f}",
                    f"{trade.get('return_pct', 0):.2f}%",
                    f"${trade.get('pnl', 0):.2f}"
                ])
            
            # Adjust column widths for 7 columns instead of 6
            trades_table = Table(trades_data, colWidths=[0.9*inch, 0.9*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch])
            trades_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc3545')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(trades_table)
            story.append(Spacer(1, 20))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "Generated by Quant Stock Analysis Platform • Backtest results are indicative only",
            self.styles['SmallText']
        ))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_signal_combiner_report(
        self,
        universe: str,
        total_models: int,
        min_confirmation: int,
        strong_buy_signals: List[Dict],
        moderate_buy_signals: List[Dict],
        strong_sell_signals: List[Dict],
        timestamp: str = None
    ) -> bytes:
        """Generate PDF report for signal combiner results"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Title
        story.append(Paragraph("🔗 Signal Combiner Report", self.styles['CustomTitle']))
        story.append(Paragraph(
            f"Multi-Model Consensus Analysis • {universe.upper()}",
            self.styles['BodyText']
        ))
        
        # Metadata
        meta_text = f"""
        <b>Generated:</b> {timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Universe:</b> {universe.upper()}<br/>
        <b>Models Analyzed:</b> {total_models}<br/>
        <b>Min Confirmation:</b> {min_confirmation} models
        """
        story.append(Paragraph(meta_text, self.styles['SmallText']))
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        story.append(Spacer(1, 15))
        
        # Strong Buy Signals
        if strong_buy_signals:
            story.append(Paragraph("🟢 Strong Buy Signals", self.styles['SectionHeader']))
            buy_data = [['Ticker', 'Confirmations', 'Avg Score', 'Models']]
            for signal in strong_buy_signals[:30]:
                models_str = ', '.join(signal.get('models', [])[:3])
                if len(signal.get('models', [])) > 3:
                    models_str += f" (+{len(signal.get('models', [])) - 3})"
                buy_data.append([
                    signal.get('ticker', '').replace('.BK', ''),
                    str(signal.get('confirmations', 0)),
                    f"{signal.get('avg_score', 0):.1f}",
                    models_str[:40]  # Truncate long model lists
                ])
            
            buy_table = Table(buy_data, colWidths=[1.2*inch, 1*inch, 1*inch, 2.3*inch])
            buy_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (3, 1), (3, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fff4')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(buy_table)
            story.append(Spacer(1, 20))
        
        # Moderate Buy Signals
        if moderate_buy_signals:
            story.append(Paragraph("🟡 Moderate Buy Signals", self.styles['SectionHeader']))
            mod_data = [['Ticker', 'Confirmations', 'Avg Score']]
            for signal in moderate_buy_signals[:20]:
                mod_data.append([
                    signal.get('ticker', '').replace('.BK', ''),
                    str(signal.get('confirmations', 0)),
                    f"{signal.get('avg_score', 0):.1f}"
                ])
            
            mod_table = Table(mod_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            mod_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ffc107')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fffbf0')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(mod_table)
            story.append(Spacer(1, 20))
        
        # Strong Sell Signals
        if strong_sell_signals:
            story.append(Paragraph("🔴 Strong Sell Signals", self.styles['SectionHeader']))
            sell_data = [['Ticker', 'Confirmations', 'Avg Score', 'Models']]
            for signal in strong_sell_signals[:30]:
                models_str = ', '.join(signal.get('models', [])[:3])
                if len(signal.get('models', [])) > 3:
                    models_str += f" (+{len(signal.get('models', [])) - 3})"
                sell_data.append([
                    signal.get('ticker', '').replace('.BK', ''),
                    str(signal.get('confirmations', 0)),
                    f"{signal.get('avg_score', 0):.1f}",
                    models_str[:40]
                ])
            
            sell_table = Table(sell_data, colWidths=[1.2*inch, 1*inch, 1*inch, 2.3*inch])
            sell_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc3545')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (3, 1), (3, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5f5')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(sell_table)
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "Generated by Quant Stock Analysis Platform • Multi-model consensus signals",
            self.styles['SmallText']
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_sector_rotation_report(
        self,
        universe: str,
        sector_rankings: List[Dict],
        rotation_recommendation: Dict,
        timestamp: str = None
    ) -> bytes:
        """Generate PDF report for sector rotation analysis"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Title
        story.append(Paragraph("🔄 Sector Rotation Analysis", self.styles['CustomTitle']))
        story.append(Paragraph(
            f"Sector Performance Rankings • {universe.upper()}",
            self.styles['BodyText']
        ))
        
        # Metadata
        meta_text = f"""
        <b>Generated:</b> {timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Universe:</b> {universe.upper()}<br/>
        <b>Total Sectors:</b> {len(sector_rankings)}
        """
        story.append(Paragraph(meta_text, self.styles['SmallText']))
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        story.append(Spacer(1, 15))
        
        # Rotation Recommendation
        if rotation_recommendation:
            story.append(Paragraph("💡 Rotation Recommendation", self.styles['SectionHeader']))
            rec_text = f"""
            <b>Summary:</b> {rotation_recommendation.get('summary', 'N/A')}<br/><br/>
            <b>Overweight Sectors:</b> {', '.join(rotation_recommendation.get('overweight', [])) or 'None'}<br/>
            <b>Underweight Sectors:</b> {', '.join(rotation_recommendation.get('underweight', [])) or 'None'}
            """
            story.append(Paragraph(rec_text, self.styles['BodyText']))
            story.append(Spacer(1, 20))
        
        # Sector Rankings
        story.append(Paragraph("Sector Rankings", self.styles['SectionHeader']))
        sector_data = [['Rank', 'Sector', 'Momentum', '1W %', '1M %', '3M %', 'Signal']]
        for sector in sector_rankings:
            sector_data.append([
                f"#{sector.get('rank', 0)}",
                sector.get('sector', ''),
                f"{sector.get('momentum_score', 0):.2f}",
                f"{sector.get('return_1w', 0):.2f}%",
                f"{sector.get('return_1m', 0):.2f}%",
                f"{sector.get('return_3m', 0):.2f}%",
                sector.get('signal', 'HOLD')
            ])
        
        sector_table = Table(sector_data, colWidths=[0.6*inch, 1.5*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        sector_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90d9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(sector_table)
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "Generated by Quant Stock Analysis Platform • Sector rotation analysis",
            self.styles['SmallText']
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_market_regime_report(
        self,
        index: str,
        regime: Dict,
        timestamp: str = None
    ) -> bytes:
        """Generate PDF report for market regime detection"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Title
        story.append(Paragraph("📈 Market Regime Detection", self.styles['CustomTitle']))
        story.append(Paragraph(
            f"Market Condition Analysis • {index}",
            self.styles['BodyText']
        ))
        
        # Metadata
        meta_text = f"""
        <b>Generated:</b> {timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Index:</b> {index}
        """
        story.append(Paragraph(meta_text, self.styles['SmallText']))
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        story.append(Spacer(1, 15))
        
        # Regime Summary
        story.append(Paragraph("Market Regime Assessment", self.styles['SectionHeader']))
        regime_color = '#28a745' if regime.get('regime') == 'BULL' else '#dc3545' if regime.get('regime') == 'BEAR' else '#ffc107'
        summary_data = [
            ['Metric', 'Value'],
            ['Regime', regime.get('regime', 'UNKNOWN')],
            ['Trend Strength', regime.get('trend_strength', 'UNKNOWN')],
            ['Volatility Regime', regime.get('volatility_regime', 'UNKNOWN')],
            ['Risk Level', regime.get('risk_level', 'UNKNOWN')],
            ['Recommended Exposure', f"{regime.get('recommended_exposure', 0)}%"]
        ]
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(regime_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Recommendation
        story.append(Paragraph("💡 Recommendation", self.styles['SectionHeader']))
        story.append(Paragraph(regime.get('recommendation', 'No recommendation available'), self.styles['BodyText']))
        story.append(Spacer(1, 20))
        
        # Market Metrics
        if regime.get('metrics'):
            story.append(Paragraph("Market Metrics", self.styles['SectionHeader']))
            metrics = regime.get('metrics', {})
            metrics_data = [
                ['Metric', 'Value'],
                ['Price', f"${metrics.get('price', 0):.2f}"],
                ['SMA 50', f"${metrics.get('sma_50', 0):.2f}"],
                ['SMA 200', f"${metrics.get('sma_200', 0):.2f}"],
                ['Distance from 200MA', f"{metrics.get('distance_from_200ma_pct', 0):.2f}%"],
                ['20-Day ROC', f"{metrics.get('roc_20d', 0):.2f}%"],
                ['Volatility (Annualized)', f"{metrics.get('volatility_annualized', 0):.2f}%"],
                ['Volatility Ratio', f"{metrics.get('volatility_ratio', 0):.2f}"],
                ['Bullish Signals', f"{metrics.get('bullish_signals', 0)}/{metrics.get('total_signals', 0)}"],
                ['Bullish %', f"{metrics.get('bullish_pct', 0):.1f}%"],
                ['Breadth Score', f"{metrics.get('breadth_score', 0):.1f}"]
            ]
            metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90d9')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(metrics_table)
            story.append(Spacer(1, 20))
        
        # Signals
        if regime.get('signals'):
            story.append(Paragraph("Market Signals", self.styles['SectionHeader']))
            signals = regime.get('signals', {})
            signals_data = [['Signal', 'Status']]
            for key, value in signals.items():
                signals_data.append([
                    key.replace('_', ' ').title(),
                    '✓' if value else '✗'
                ])
            
            signals_table = Table(signals_data, colWidths=[3*inch, 1.5*inch])
            signals_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c757d')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(signals_table)
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "Generated by Quant Stock Analysis Platform • Market regime analysis",
            self.styles['SmallText']
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()


# Singleton instance
_pdf_generator = None

def get_pdf_generator() -> PDFReportGenerator:
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = PDFReportGenerator()
    return _pdf_generator
