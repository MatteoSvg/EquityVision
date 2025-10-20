import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
import sys
import os

# Aggiungi il percorso della directory principale al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import DatabaseManager


class EquityVisionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EquityVision - Analisi Raccomandazioni")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        # Inizializza il database
        try:
            self.db = DatabaseManager()
        except FileNotFoundError as e:
            messagebox.showerror("Errore", str(e))
            self.root.destroy()
            return
        
        # Configura lo stile
        self.setup_style()
        
        # Crea l'interfaccia
        self.create_widgets()
        
        # Carica i dati iniziali
        self.load_companies()
        self.update_display()
    
    def setup_style(self):
        """Configura lo stile dei widget"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colori personalizzati
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Arial', 10), foreground='#7f8c8d')
        style.configure('Filter.TLabelframe', font=('Arial', 10, 'bold'))
        style.configure('Treeview', rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
    
    def create_widgets(self):
        """Crea tutti i widget dell'interfaccia"""
        
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configura il grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # Filtri
        self.create_filters(main_frame)
        
        # Tabella risultati
        self.create_results_table(main_frame)
        
        # Statistiche
        self.create_statistics(main_frame)
    
    def create_header(self, parent):
        """Crea l'header dell'applicazione"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(header_frame, text="EquityVision", style='Title.TLabel').pack(anchor=tk.W)
        ttk.Label(header_frame, text="Sistema di analisi raccomandazioni FTSE MIB", 
                 style='Subtitle.TLabel').pack(anchor=tk.W)
    
    def create_filters(self, parent):
        """Crea il pannello dei filtri"""
        filter_frame = ttk.LabelFrame(parent, text="Filtri", style='Filter.TLabelframe', padding="10")
        filter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Società
        ttk.Label(filter_frame, text="Società:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.company_var = tk.StringVar(value="Tutte")
        self.company_combo = ttk.Combobox(filter_frame, textvariable=self.company_var, 
                                          state='readonly', width=30)
        self.company_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Periodo
        ttk.Label(filter_frame, text="Periodo:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.period_var = tk.StringVar(value="Ultimo mese")
        period_combo = ttk.Combobox(filter_frame, textvariable=self.period_var, 
                                    state='readonly', width=20)
        period_combo['values'] = ('Ultimo mese', 'Ultimi 3 mesi', 'Ultimi 6 mesi', 
                                   'Ultimi 12 mesi', 'Tutti')
        period_combo.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        # Banca
        ttk.Label(filter_frame, text="Banca:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.bank_var = tk.StringVar(value="Tutte")
        self.bank_combo = ttk.Combobox(filter_frame, textvariable=self.bank_var, 
                                       state='readonly', width=25)
        self.bank_combo.grid(row=0, column=5, sticky=tk.W, padx=(0, 20))
        
        # Pulsante applica filtri
        apply_btn = ttk.Button(filter_frame, text="Applica Filtri", 
                              command=self.apply_filters)
        apply_btn.grid(row=0, column=6, padx=(0, 10))
        
        # Pulsante reset
        reset_btn = ttk.Button(filter_frame, text="Reset", command=self.reset_filters)
        reset_btn.grid(row=0, column=7)
    
    def create_results_table(self, parent):
        """Crea la tabella dei risultati"""
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        columns = ('Società', 'Banca', 'Target Price', 'Data', 'Variazione %')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                yscrollcommand=scrollbar_y.set,
                                xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Configura colonne
        self.tree.heading('Società', text='Società')
        self.tree.heading('Banca', text='Banca')
        self.tree.heading('Target Price', text='Target Price (€)')
        self.tree.heading('Data', text='Data')
        self.tree.heading('Variazione %', text='Variazione %')
        
        self.tree.column('Società', width=200, anchor=tk.W)
        self.tree.column('Banca', width=250, anchor=tk.W)
        self.tree.column('Target Price', width=150, anchor=tk.E)
        self.tree.column('Data', width=120, anchor=tk.CENTER)
        self.tree.column('Variazione %', width=120, anchor=tk.E)
        
        # Grid
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Alternanza colori righe
        self.tree.tag_configure('oddrow', background='#f9f9f9')
        self.tree.tag_configure('evenrow', background='#ffffff')
        self.tree.tag_configure('positive', foreground='#27ae60')
        self.tree.tag_configure('negative', foreground='#e74c3c')
    
    def create_statistics(self, parent):
        """Crea il pannello delle statistiche"""
        stats_frame = ttk.LabelFrame(parent, text="Statistiche", padding="10")
        stats_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        self.stats_label = ttk.Label(stats_frame, text="", font=('Arial', 9))
        self.stats_label.pack(anchor=tk.W)
    
    def load_companies(self):
        """Carica la lista delle società dal database"""
        try:
            self.db.cursor.execute("SELECT DISTINCT name FROM companies ORDER BY name")
            companies = ['Tutte'] + [row[0] for row in self.db.cursor.fetchall()]
            self.company_combo['values'] = companies
            
            # Carica anche le banche
            self.db.cursor.execute("SELECT DISTINCT bank FROM recommendations ORDER BY bank")
            banks = ['Tutte'] + [row[0] for row in self.db.cursor.fetchall()]
            self.bank_combo['values'] = banks
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel caricamento delle società: {e}")
    
    def get_date_range(self, period):
        """Calcola il range di date in base al periodo selezionato"""
        end_date = date.today()
        
        if period == "Ultimo mese":
            start_date = end_date - timedelta(days=30)
        elif period == "Ultimi 3 mesi":
            start_date = end_date - timedelta(days=90)
        elif period == "Ultimi 6 mesi":
            start_date = end_date - timedelta(days=180)
        elif period == "Ultimi 12 mesi":
            start_date = end_date - timedelta(days=365)
        else:  # Tutti
            start_date = date(2000, 1, 1)
        
        return start_date, end_date
    
    def apply_filters(self):
        """Applica i filtri selezionati"""
        self.update_display()
    
    def reset_filters(self):
        """Resetta tutti i filtri"""
        self.company_var.set("Tutte")
        self.period_var.set("Ultimo mese")
        self.bank_var.set("Tutte")
        self.update_display()
    
    def update_display(self):
        """Aggiorna la visualizzazione dei dati"""
        # Pulisci la tabella
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Ottieni i filtri
        company = self.company_var.get()
        period = self.period_var.get()
        bank = self.bank_var.get()
        start_date, end_date = self.get_date_range(period)
        
        # Costruisci la query
        query = """
            SELECT c.name, r.bank, r.target_price, r.date, c.market_price
            FROM recommendations r
            JOIN companies c ON r.company_id = c.id
            WHERE r.date >= ? AND r.date <= ?
        """
        params = [start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")]
        
        if company != "Tutte":
            query += " AND c.name = ?"
            params.append(company)
        
        if bank != "Tutte":
            query += " AND r.bank = ?"
            params.append(bank)
        
        query += " ORDER BY r.date DESC, c.name"
        
        try:
            self.db.cursor.execute(query, params)
            results = self.db.cursor.fetchall()
            
            # Popola la tabella
            for idx, row in enumerate(results):
                name, bank_name, target_price, rec_date, market_price = row
                
                # Calcola la variazione percentuale
                try:
                    target = float(target_price.replace(',', '.'))
                    market = float(str(market_price).replace(',', '.'))
                    variation = ((target - market) / market) * 100
                    variation_str = f"{variation:+.2f}%"
                    tag = 'positive' if variation > 0 else 'negative'
                except:
                    variation_str = "N/A"
                    variation = 0
                    tag = ''
                
                # Alterna i colori delle righe
                row_tag = 'oddrow' if idx % 2 == 0 else 'evenrow'
                tags = (row_tag, tag) if tag else (row_tag,)
                
                self.tree.insert('', tk.END, 
                               values=(name, bank_name, target_price, rec_date, variation_str),
                               tags=tags)
            
            # Aggiorna le statistiche
            self.update_statistics(results)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'applicazione dei filtri: {e}")
    
    def update_statistics(self, results):
        """Aggiorna il pannello delle statistiche"""
        total = len(results)
        
        if total == 0:
            self.stats_label.config(text="Nessun dato disponibile per i filtri selezionati")
            return
        
        # Conta raccomandazioni positive e negative
        positive = 0
        negative = 0
        
        for row in results:
            try:
                target = float(row[2].replace(',', '.'))
                market = float(str(row[4]).replace(',', '.'))
                if target > market:
                    positive += 1
                else:
                    negative += 1
            except:
                pass
        
        stats_text = (f"Totale raccomandazioni: {total} | "
                     f"Rialziste: {positive} ({positive/total*100:.1f}%) | "
                     f"Ribassiste: {negative} ({negative/total*100:.1f}%)")
        
        self.stats_label.config(text=stats_text)
    
    def on_closing(self):
        """Gestisce la chiusura dell'applicazione"""
        self.db.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = EquityVisionGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()