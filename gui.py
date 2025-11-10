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
        '''
        Metodo: __init__
        Costruttore della classe EquityVisionGUI. Inizializza la finestra principale e i dati.
        Parametri formali:
        object db -> Oggetto database per l'interazione con i dati
        Valore di ritorno:
        None -> Nessun valore di ritorno.
        '''
        self.db = db
        self.root = tk.Tk() #creo la finestra principale che contiene tutti i widget
        self.root.title("EquityVision")
        self.root.geometry("1200x700")
        self.current_figure = None #questo attributo mi serve per gestire la chisura del grafico quando voglio aprirne un altro cambiando i filtri
        
        self.filtered_data = []
        
        self.setup_ui()
        self.load_data()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        '''
        Metodo: setup_ui
        Crea e dispone tutti i widget (pulsanti, tabelle, filtri) nell'interfaccia grafica.
        Parametri formali:
        None
        Valore di ritorno:
        None -> Nessun valore di ritorno.
        '''
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
       
        filter_frame = ttk.LabelFrame(main_frame, text="Filtri", padding="10")
        filter_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
     
        ttk.Label(filter_frame, text="Azienda:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar()
        self.name_combo = ttk.Combobox(filter_frame, textvariable=self.name_var, width=30)
        self.name_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        
        ttk.Label(filter_frame, text="Banca:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.bank_var = tk.StringVar()
        self.bank_combo = ttk.Combobox(filter_frame, textvariable=self.bank_var, width=30)
        self.bank_combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        
        ttk.Label(filter_frame, text="Periodo:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_var = tk.StringVar()
        self.date_combo = ttk.Combobox(filter_frame, textvariable=self.date_var, width=30, state='readonly')
        self.date_combo['values'] = ('Tutti', 'Ultimo mese', 'Ultimi 3 mesi', 'Ultimi 6 mesi', 'Ultimo anno')
        self.date_combo.current(0)
        self.date_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
       
        button_frame = ttk.Frame(filter_frame)
        button_frame.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky=tk.E)
        
        ttk.Button(button_frame, text="Applica Filtri", command=self.apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset Filtri", command=self.reset_filters).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Mostra Grafico", command=self.show_chart).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Esporta PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=5)
        
      
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
       
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
       
        columns = ('Azienda', 'Banca', 'Target Price', 'Data', 'Market Price')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                 yscrollcommand=scrollbar_y.set,
                                 xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        
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
        
       
        self.info_label = ttk.Label(main_frame, text="")
        self.info_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def load_data(self):
        '''
        Metodo: load_data
        Carica tutti i dati delle raccomandazioni dal database
        Popola i menu a tendina (Combobox) dei filtri e aggiorna la tabella.
        Parametri formali:
        None
        Valore di ritorno:
        None -> Nessun valore di ritorno.
        '''
        try:
            all_data = self.db.find_recommendations()
            self.filtered_data = all_data
            
            
            companies = sorted(set(row[0] for row in all_data))
            self.name_combo['values'] = ['Tutte'] + companies
            self.name_combo.current(0)
            
           
            banks = sorted(set(row[1] for row in all_data))
            self.bank_combo['values'] = ['Tutte'] + banks
            self.bank_combo.current(0)
            
            self.update_table()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel caricamento dei dati: {str(e)}")
    
    def update_table(self):
        '''
        Metodo: update_table
        Aggiorna la visualizzazione della tabella (Treeview) con i dati contenuti in self.filtered_data.
        Pulisce la tabella e la riempie con i dati filtrati.
        Parametri formali:
        None
        Valore di ritorno:
        None -> Nessun valore di ritorno.
        '''
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for row in self.filtered_data:
            self.tree.insert('', tk.END, values=row)
        
        self.info_label.config(text=f"Totale raccomandazioni visualizzate: {len(self.filtered_data)}")
    
    def apply_filters(self):
        '''
        Metodo: apply_filters
        Filtra i dati in base alle selezioni nei Combobox (Azienda, Banca, Periodo)
        e aggiorna la tabella chiamando self.update_table().
        Parametri formali:
        None
        Valore di ritorno:
        None -> Nessun valore di ritorno.
        '''
        try:
            all_data = self.db.find_recommendations()
            filtered = all_data
            
            selected_company = self.name_var.get()
            if selected_company and selected_company != 'Tutte':
                filtered = [row for row in filtered if row[0] == selected_company]
            
            selected_bank = self.bank_var.get()
            if selected_bank and selected_bank != 'Tutte':
                filtered = [row for row in filtered if row[1] == selected_bank]
            
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
    
    def parse_date(self, date_str) -> date:
        '''
        Funzione: parse_date
        Funzione di utilità per convertire una stringa di data (formato YYYY-MM-DD) in un oggetto 'date'.
        Parametri formali:
        str date_str -> Stringa della data da convertire.
        Valore di ritorno:
        date -> Oggetto 'date' corrispondente. Ritorna la data odierna in caso di errore.
        '''
        try:
            from datetime import datetime
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return date.today()
    
    def reset_filters(self):
        '''
        Metdoo: reset_filters
        Resetta i filtri al loro valore predefinito e ricarica
        tutti i dati chiamando self.load_data().
        Parametri formali:
        None
        Valore di ritorno:
        None -> Nessun valore di ritorno.
        '''
        self.name_combo.current(0)
        self.bank_combo.current(0)
        self.date_combo.current(0)
        self.load_data()
    
    def sort_column(self, col, reverse):
        '''
        Metodo: sort_column
        Ordina i dati nella tabella quando l'intestazione di una colonna viene cliccata.
        Parametri formali:
        str col -> Nome della colonna da ordinare ('Azienda', 'Banca', 'Data').
        bool reverse -> True per ordinamento discendente, False per ascendente.
        Valore di ritorno:
        None -> Nessun valore di ritorno.
        '''
        col_index = {'Azienda': 0, 'Banca': 1, 'Data': 2}
        idx = col_index[col]
         
        try:
            if col == 'Data':
                self.filtered_data.sort(key=lambda x: self.parse_date(x[idx]), reverse=reverse)
            else:
                self.filtered_data.sort(key=lambda x: x[idx], reverse=reverse)
            
            self.update_table()
            
            self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'ordinamento: {str(e)}")
    
    def show_chart(self):
        '''
        Metodo: show_chart
        Genera e visualizza un grafico che confronta i target price medi e il prezzo di mercato
        per una singola azienda selezionata nei filtri.
        Parametri formali:
        None
        Valore di ritorno:
        None -> Nessun valore di ritorno.
        '''
        try:
            if self.current_figure is not None:
                plt.close(self.current_figure)
                self.current_figure = None
            if not self.filtered_data:
                messagebox.showwarning("Attenzione", "Nessun dato da visualizzare. Applicare prima i filtri.")
                return
            
            companies = set(row[0] for row in self.filtered_data)
            if len(companies) > 1:
                messagebox.showwarning("Attenzione", "Selezionare una singola azienda per visualizzare il grafico.")
                return
            
            company_name = list(companies)[0]
            
            date_target_map = defaultdict(list)
            date_market_map = {}
            
            for row in self.filtered_data:
                date_obj = self.parse_date(row[3])
                
                try:
                    target_price = row[2]
                    if target_price is not None:
                        date_target_map[date_obj].append(target_price)
                except (ValueError, AttributeError):
                    pass
                
                try:
                    market_price = float(row[4].replace(',', '.')) if row[4] else None
                    if market_price is not None:
                        date_market_map[date_obj] = market_price
                except (ValueError, AttributeError):
                    pass
            
            dates_target = []
            avg_target_prices = []
            for date_obj in sorted(date_target_map.keys()):
                dates_target.append(date_obj)
                avg_target_prices.append(sum(date_target_map[date_obj]) / len(date_target_map[date_obj]))
            
            dates_market = sorted(date_market_map.keys())
            market_prices = [date_market_map[d] for d in dates_market]
            
            if not dates_target and not dates_market:
                messagebox.showwarning("Attenzione", "Nessun dato numerico valido da visualizzare.")
                return
            
            self.current_figure = plt.figure(figsize=(12, 6))
                
            if dates_target:
                plt.plot(dates_target, avg_target_prices, marker='o', linestyle='-', 
                        linewidth=2, markersize=6, label='Target Price', color='#2E86AB')
            
            if dates_market:
                plt.plot(dates_market, market_prices, linestyle='-', 
                        linewidth=2, markersize=6, label='Market Price', color="#FF0000")
            
            plt.title(f'Confronto prezzo di mercato con raccomandazioni - {company_name}', fontsize=16, fontweight='bold', pad=20)
            plt.ylabel('Euro', fontsize=12, fontweight='bold')
            plt.legend(loc='best', fontsize=10, framealpha=0.9)
            plt.grid(True, alpha=0.3, linestyle='--')
            
            ax = plt.gca()
            date_formatter = DateFormatter('%d/%m/%Y')
            ax.xaxis.set_major_formatter(date_formatter)
            plt.xticks(rotation=45, ha='right')
            
            plt.tight_layout()
            
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella generazione del grafico: {str(e)}")
    
    def export_pdf(self):
        '''
        Metodo: export_pdf
        Esporta i dati attualmente filtrati (self.filtered_data) in un file PDF
        utilizzando la libreria reportlab.
        Parametri formali:
        None
        Valore di ritorno:
        None -> Nessun valore di ritorno.
        '''
        if not self.filtered_data:
            messagebox.showwarning("Attenzione", "Nessun dato da esportare!")
            return
        
        try:
            filename = f"raccomandazioni_{date.today().strftime('%Y%m%d')}.pdf"
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            elements = []
            
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            
            title = Paragraph("Raccomandazioni EquityVision", title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.5*cm))
            
            filter_info = f"Data esportazione: {date.today().strftime('%d/%m/%Y')}<br/>"
            filter_info += f"Totale raccomandazioni: {len(self.filtered_data)}"
            elements.append(Paragraph(filter_info, styles['Normal']))
            elements.append(Spacer(1, 0.5*cm))
            
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
            
            doc.build(elements)
            
            messagebox.showinfo("Successo", f"PDF esportato con successo:\n{os.path.abspath(filename)}")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'esportazione PDF: {str(e)}")
    
    def run(self):
        '''
        Metodo: run
        Avvia il loop principale (mainloop) dell'interfaccia grafica Tkinter.
        L'applicazione attenderà le interazioni dell'utente.
        Parametri formali:
        None
        Valore di ritorno:
        None -> Nessun valore di ritorno.
        '''
        self.root.mainloop()
    
    def on_closing(self):
        '''
        Metodo: on_closing
        Gestisce l'evento di chiusura della finestra (es. click sulla 'X').
        Chiude eventuali grafici aperti e distrugge la finestra principale.
        Parametri formali:
        None
        Valore di ritorno:
        None -> Nessun valore di ritorno.
        '''
        # Chiude il grafico se è aperto
        if self.current_figure is not None:
            plt.close(self.current_figure)
        self.root.destroy()