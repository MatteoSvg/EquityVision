import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
import os
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from collections import defaultdict
from datetime import datetime


class EquityVisionGUI:
    def __init__(self, db):
        self.db = db
        self.root = tk.Tk()
        self.root.title("EquityVision")
        self.root.geometry("1200x700")
        self.current_figure = None
        
        self.filtered_data = []
        
        self.setup_ui()
        self.load_data()
        
        # Gestisce la chiusura
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurazione grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # ===== FRAME FILTRI =====
        filter_frame = ttk.LabelFrame(main_frame, text="Filtri", padding="10")
        filter_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Filtro per Nome
        ttk.Label(filter_frame, text="Azienda:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar()
        self.name_combo = ttk.Combobox(filter_frame, textvariable=self.name_var, width=30)
        self.name_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Filtro per Banca
        ttk.Label(filter_frame, text="Banca:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.bank_var = tk.StringVar()
        self.bank_combo = ttk.Combobox(filter_frame, textvariable=self.bank_var, width=30)
        self.bank_combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Filtro per Data
        ttk.Label(filter_frame, text="Periodo:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_var = tk.StringVar()
        self.date_combo = ttk.Combobox(filter_frame, textvariable=self.date_var, width=30, state='readonly')
        self.date_combo['values'] = ('Tutti', 'Ultimo mese', 'Ultimi 3 mesi', 'Ultimi 6 mesi', 'Ultimo anno')
        self.date_combo.current(0)
        self.date_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Pulsanti
        button_frame = ttk.Frame(filter_frame)
        button_frame.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky=tk.E)
        
        ttk.Button(button_frame, text="Applica Filtri", command=self.apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset Filtri", command=self.reset_filters).pack(side=tk.LEFT, padx=5)
        # --- Pulsante Aggiunto ---
        ttk.Button(button_frame, text="Mostra Grafico", command=self.show_chart).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Esporta PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=5)
        
        # ===== FRAME TABELLA =====
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Treeview
        columns = ('Azienda', 'Banca', 'Target Price', 'Data', 'Market Price')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                 yscrollcommand=scrollbar_y.set,
                                 xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Configurazione colonne
        self.tree.heading('Azienda', text='Azienda', command=lambda: self.sort_column('Azienda', False))
        self.tree.heading('Banca', text='Banca', command=lambda: self.sort_column('Banca', False))
        self.tree.heading('Target Price', text='Target Price')
        self.tree.heading('Data', text='Data', command=lambda: self.sort_column('Data', False))
        self.tree.heading('Market Price', text='Market Price')
        
        self.tree.column('Azienda', width=300)
        self.tree.column('Banca', width=250)
        self.tree.column('Target Price', width=150)
        self.tree.column('Data', width=150)
        self.tree.column('Market Price', width=150)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ===== LABEL INFO =====
        self.info_label = ttk.Label(main_frame, text="")
        self.info_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def load_data(self):
        """Carica tutti i dati dal database"""
        try:
            all_data = self.db.find_recommendations()
            self.filtered_data = all_data
            
            # Popola combobox aziende
            companies = sorted(set(row[0] for row in all_data))
            self.name_combo['values'] = ['Tutte'] + companies
            self.name_combo.current(0)
            
            # Popola combobox banche
            banks = sorted(set(row[1] for row in all_data))
            self.bank_combo['values'] = ['Tutte'] + banks
            self.bank_combo.current(0)
            
            self.update_table()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel caricamento dei dati: {str(e)}")
    
    def update_table(self):
        """Aggiorna la visualizzazione della tabella"""
        # Pulisce la tabella
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Inserisce i dati filtrati
        for row in self.filtered_data:
            self.tree.insert('', tk.END, values=row)
        
        # Aggiorna label info
        self.info_label.config(text=f"Totale raccomandazioni visualizzate: {len(self.filtered_data)}")
    
    def apply_filters(self):
        """Applica i filtri selezionati"""
        try:
            all_data = self.db.find_recommendations()
            filtered = all_data
            
            # Filtro per azienda
            selected_company = self.name_var.get()
            if selected_company and selected_company != 'Tutte':
                filtered = [row for row in filtered if row[0] == selected_company]
            
            # Filtro per banca
            selected_bank = self.bank_var.get()
            if selected_bank and selected_bank != 'Tutte':
                filtered = [row for row in filtered if row[1] == selected_bank]
            
            # Filtro per data
            selected_period = self.date_var.get()
            if selected_period != 'Tutti':
                today = date.today()
                
                if selected_period == 'Ultimo mese':
                    start_date = today - timedelta(days=30)
                elif selected_period == 'Ultimi 3 mesi':
                    start_date = today - timedelta(days=90)
                elif selected_period == 'Ultimi 6 mesi':
                    start_date = today - timedelta(days=180)
                elif selected_period == 'Ultimo anno':
                    start_date = today - timedelta(days=365)
                
                filtered = [row for row in filtered 
                           if self.parse_date(row[3]) >= start_date]
            
            self.filtered_data = filtered
            self.update_table()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'applicazione dei filtri: {str(e)}")
    
    def parse_date(self, date_str):
        """Converte una stringa data in oggetto date"""
        try:
            from datetime import datetime
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return date.today()
    
    def reset_filters(self):
        """Resetta tutti i filtri"""
        self.name_combo.current(0)
        self.bank_combo.current(0)
        self.date_combo.current(0)
        self.load_data()
    
    def sort_column(self, col, reverse):
        """Ordina la tabella per colonna"""
        col_index = {'Azienda': 0, 'Banca': 1, 'Data': 2}
        idx = col_index[col]
         
        try:
            # Ordina i dati
            if col == 'Data':
                self.filtered_data.sort(key=lambda x: self.parse_date(x[idx]), reverse=reverse)
            else:
                self.filtered_data.sort(key=lambda x: x[idx], reverse=reverse)
            
            self.update_table()
            
            # Aggiorna il comando per invertire l'ordine al prossimo click
            self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'ordinamento: {str(e)}")
    
    def show_chart(self):
        """Visualizza il grafico con target price e market price"""
        try:
            # Chiude il grafico precedente se esiste
            if self.current_figure is not None:
                plt.close(self.current_figure)
                self.current_figure = None
            if not self.filtered_data:
                messagebox.showwarning("Attenzione", "Nessun dato da visualizzare. Applicare prima i filtri.")
                return
            
            # Verifica se è selezionata una singola azienda
            companies = set(row[0] for row in self.filtered_data)
            if len(companies) > 1:
                messagebox.showwarning("Attenzione", "Selezionare una singola azienda per visualizzare il grafico.")
                return
            
            company_name = list(companies)[0]
            
            # Raggruppa i dati per data e calcola la media dei target price
            date_target_map = defaultdict(list)
            date_market_map = {}
            
            for row in self.filtered_data:
                date_obj = self.parse_date(row[3])
                
                # Target Price (indice 2)
                try:
                    target_price = row[2]
                    if target_price is not None:
                        date_target_map[date_obj].append(target_price)
                except (ValueError, AttributeError):
                    pass
                
                # Market Price (indice 4)
                try:
                    market_price = float(row[4].replace(',', '.')) if row[4] else None
                    if market_price is not None:
                        date_market_map[date_obj] = market_price
                except (ValueError, AttributeError):
                    pass
            
            # Calcola le medie dei target price per ogni data
            dates_target = []
            avg_target_prices = []
            for date_obj in sorted(date_target_map.keys()):
                dates_target.append(date_obj)
                avg_target_prices.append(sum(date_target_map[date_obj]) / len(date_target_map[date_obj]))
            
            # Prepara i dati per market price
            dates_market = sorted(date_market_map.keys())
            market_prices = [date_market_map[d] for d in dates_market]
            
            # Verifica che ci siano dati da visualizzare
            if not dates_target and not dates_market:
                messagebox.showwarning("Attenzione", "Nessun dato numerico valido da visualizzare.")
                return
            
            # Crea il nuovo grafico e memorizza il riferimento
            self.current_figure = plt.figure(figsize=(12, 6))
                
            # Plot target price
            if dates_target:
                plt.plot(dates_target, avg_target_prices, marker='o', linestyle='-', 
                        linewidth=2, markersize=6, label='Target Price', color='#2E86AB')
            
            # Plot market price
            if dates_market:
                plt.plot(dates_market, market_prices, linestyle='-', 
                        linewidth=2, markersize=6, label='Market Price', color="#FF0000")
            
            # Configurazione del grafico
            plt.title(f'Confronto prezzo di mercato con raccomandazioni - {company_name}', fontsize=16, fontweight='bold', pad=20)
            plt.ylabel('Euro', fontsize=12, fontweight='bold')
            plt.legend(loc='best', fontsize=10, framealpha=0.9)
            plt.grid(True, alpha=0.3, linestyle='--')
            
            # Formatta l'asse x per le date
            ax = plt.gca()
            date_formatter = DateFormatter('%d/%m/%Y')
            ax.xaxis.set_major_formatter(date_formatter)
            plt.xticks(rotation=45, ha='right')
            
            # Layout ottimizzato
            plt.tight_layout()
            
            # Mostra il grafico
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella generazione del grafico: {str(e)}")
    
    def export_pdf(self):
        """Esporta i dati filtrati in PDF"""
        if not self.filtered_data:
            messagebox.showwarning("Attenzione", "Nessun dato da esportare!")
            return
        
        try:
            # Nome file
            filename = f"raccomandazioni_{date.today().strftime('%Y%m%d')}.pdf"
            
            # Crea il PDF
            doc = SimpleDocTemplate(filename, pagesize=A4)
            elements = []
            
            # Stile
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            
            # Titolo
            title = Paragraph("Raccomandazioni EquityVision", title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.5*cm))
            
            # Info filtri applicati
            filter_info = f"Data esportazione: {date.today().strftime('%d/%m/%Y')}<br/>"
            filter_info += f"Totale raccomandazioni: {len(self.filtered_data)}"
            elements.append(Paragraph(filter_info, styles['Normal']))
            elements.append(Spacer(1, 0.5*cm))
            
            # Tabella dati
            data = [['Azienda', 'Banca', 'Target Price', 'Data']]
            for row in self.filtered_data:
                data.append(list(row))
            
            table = Table(data, colWidths=[5*cm, 4*cm, 3*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            elements.append(table)
            
            # Genera PDF
            doc.build(elements)
            
            messagebox.showinfo("Successo", f"PDF esportato con successo:\n{os.path.abspath(filename)}")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'esportazione PDF: {str(e)}")
    
    def run(self):
        """Avvia il loop principale dell'interfaccia"""
        self.root.mainloop()
    
    def on_closing(self):
        """Gestisce la chiusura dell'applicazione"""
        # Chiude il grafico se è aperto
        if self.current_figure is not None:
            plt.close(self.current_figure)
        self.root.destroy()