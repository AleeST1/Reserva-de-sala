import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import mysql.connector
from datetime import datetime, timedelta
import os
import sys
from PIL import Image, ImageTk
import threading
import webbrowser
import requests
from packaging.version import parse as vparse

APP_VERSION = "1.0.1"
VERSION_JSON_URL = "https://aleest1.github.io/Reserva-de-sala/version.json"

class UpdateChecker:
    def __init__(self, root, current_version, json_url, timeout=5):
        self.root = root
        self.current_version = str(current_version)
        self.json_url = json_url
        self.timeout = timeout
        self.session = requests.Session()

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            resp = self.session.get(self.json_url, timeout=self.timeout, headers={"User-Agent": f"App/{self.current_version}"})
            if resp.status_code != 200:
                return
            data = resp.json()
            latest = str(data.get("latest") or data.get("version") or "")
            download_url = str(data.get("download_url") or data.get("installer_url") or "")
            changelog = str(data.get("changelog") or "")
            if not latest or not download_url:
                return
            if vparse(latest) <= vparse(self.current_version):
                return
            self.root.after(0, lambda: self._show_popup(latest, download_url, changelog))
        except Exception:
            pass

    def _show_popup(self, latest, download_url, changelog):
        top = tk.Toplevel(self.root)
        top.title("Atualização disponível")
        top.resizable(False, False)
        top.transient(self.root)
        top.grab_set()
        container = ttk.Frame(top, padding=16)
        container.grid(row=0, column=0, sticky="nsew")
        top.columnconfigure(0, weight=1)
        top.rowconfigure(0, weight=1)
        ttk.Label(container, text="Uma nova versão está disponível").grid(row=0, column=0, sticky="w")
        ttk.Label(container, text=f"Versão atual: {self.current_version}").grid(row=1, column=0, sticky="w", pady=(8,0))
        ttk.Label(container, text=f"Nova versão: {latest}").grid(row=2, column=0, sticky="w")
        if changelog.strip():
            ttk.Label(container, text="Changelog:", font=("Segoe UI", 9, "bold")).grid(row=3, column=0, sticky="w", pady=(12,4))
            ttk.Label(container, text=changelog, wraplength=520, justify="left").grid(row=4, column=0, sticky="w")
        btns = ttk.Frame(container)
        btns.grid(row=5, column=0, sticky="ew", pady=(16,0))
        btns.columnconfigure(0, weight=1)
        def on_download():
            webbrowser.open(download_url)
            top.destroy()
        ttk.Button(btns, text="Baixar agora", command=on_download).grid(row=0, column=0, sticky="w")
        ttk.Button(btns, text="Depois", command=top.destroy).grid(row=0, column=1, sticky="e")
        top.update_idletasks()
        w = top.winfo_width()
        h = top.winfo_height()
        x = (top.winfo_screenwidth() - w) // 2
        y = (top.winfo_screenheight() - h) // 2
        top.geometry(f"+{x}+{y}")

def schedule_update_check(root):
    UpdateChecker(root, APP_VERSION, VERSION_JSON_URL, timeout=5).start()

class SistemaReservas:
    def __init__(self, root):
        self.root = root
        self.root.title('Sistema de Reservas de Salas')
        self.root.geometry('500x900')
        self.root.resizable(False, False)
        self.root.configure(bg='#f8f9fa')
        
        # Set window icon - Improved method for cross-machine compatibility
        try:
            # Get resource path that works both in development and PyInstaller
            def get_resource_path(relative_path):
                try:
                    # PyInstaller creates a temp folder and stores path in _MEIPASS
                    base_path = sys._MEIPASS
                except Exception:
                    base_path = os.path.abspath(os.path.dirname(__file__))
                return os.path.join(base_path, relative_path)
            
            # Define icon paths - Updated to use the combined icon
            icon_primary = get_resource_path(os.path.join('resources', 'icone_completo.ico'))
            icon_secondary = get_resource_path(os.path.join('resources', 'icone96.ico'))  # Fallback to largest icon
            
            # Try to set the icon with better error handling
            icon_set = False
            
            # Try primary icon first (ICO format)
            if os.path.exists(icon_primary):
                try:
                    self.root.iconbitmap(icon_primary)
                    icon_set = True
                    print(f'Ícone combinado carregado com sucesso: {icon_primary}')
                except Exception as e:
                    print(f'Erro ao carregar ícone combinado: {e}')
            
            # If primary icon failed, try secondary icon (96x96)
            if not icon_set and os.path.exists(icon_secondary):
                try:
                    self.root.iconbitmap(icon_secondary)
                    icon_set = True
                    print(f'Ícone 96x96 carregado com sucesso: {icon_secondary}')
                except Exception as e:
                    print(f'Erro ao carregar ícone 96x96: {e}')
            
            # If both methods failed, try other available icons
            if not icon_set:
                for icon_size in ['72', '64', '48', '32']:
                    icon_path = get_resource_path(os.path.join('resources', f'icone{icon_size}.ico'))
                    if os.path.exists(icon_path):
                        try:
                            self.root.iconbitmap(icon_path)
                            icon_set = True
                            print(f'Ícone {icon_size}x{icon_size} carregado com sucesso: {icon_path}')
                            break
                        except Exception as e:
                            print(f'Erro ao carregar ícone {icon_size}x{icon_size}: {e}')
            
            if not icon_set:
                print('Nenhum ícone foi carregado com sucesso')
                
        except Exception as e:
            print(f'Erro geral ao carregar ícones: {e}')


        
        # Variável para controlar o temporizador de atualização automática
        self.update_timer = None
        self.update_interval = 10000  # Intervalo de atualização em milissegundos (10 segundos)
        self.cleanup_timer = None
        self.cleanup_interval = 86400000

        # Configurar estilo moderno
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f8f9fa')
        self.style.configure('MainFrame.TFrame', background='#f8f9fa')
        self.style.configure('TLabel', background='#f8f9fa', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 9, 'bold'), padding=6)
        self.style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#2c3e50')
        self.style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#2c3e50')
        
        # Configurar estilo dos campos de entrada
        self.style.configure('TEntry',
                            fieldbackground='#ffffff',
                            borderwidth=1,
                            relief='solid',
                            padding=4)
        self.style.configure('TCombobox',
                            fieldbackground='#ffffff',
                            background='#ffffff',
                            arrowcolor='#2c3e50',
                            padding=4)
        
        # Estilos modernos para os slots de horário
        self.style.configure('Slot.TFrame', background='#f8f9fa', padding=4)
        self.style.configure('Disponivel.TButton',
                          background='#4CAF50',
                          foreground='white',
                          relief='flat',
                          borderwidth=0)
        self.style.configure('Ocupado.TButton',
                          background='#e74c3c',
                          foreground='white',
                          relief='flat',
                          borderwidth=0)
        self.style.map('Disponivel.TButton',
                      background=[('active', '#45a049'), ('!disabled', '#4CAF50'), ('disabled', '#e9ecef')],
                      foreground=[('active', 'white'), ('!disabled', 'white'), ('disabled', '#6c757d')],
                      relief=[('pressed', 'flat')])
        self.style.map('Ocupado.TButton',
                      background=[('active', '#c0392b'), ('!disabled', '#e74c3c'), ('disabled', '#e9ecef')],
                      foreground=[('active', 'white'), ('!disabled', 'white'), ('disabled', '#6c757d')],
                      relief=[('pressed', 'flat')])

        # Frame principal com sombra e borda arredondada
        self.main_frame = ttk.Frame(self.root, style='MainFrame.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # Logo
        self.carregar_logo()

        # Container para os campos
        self.campos_frame = ttk.Frame(self.main_frame)
        self.campos_frame.pack(fill=tk.X, pady=5)

        # Seleção de sala
        ttk.Label(self.campos_frame, text='Selecione a Sala:', style='Header.TLabel').pack(pady=1)
        self.sala_var = tk.StringVar()
        salas = ['Rally', 'Motocross', 'Freestyle', 'Arena Cross', 'Enduro']
        self.sala_combo = ttk.Combobox(self.campos_frame, textvariable=self.sala_var, values=salas, width=25)
        self.sala_combo.pack(pady=1)

        # Nome do solicitante
        ttk.Label(self.campos_frame, text='Nome do Solicitante:', style='Header.TLabel').pack(pady=2)
        self.nome_var = tk.StringVar()
        self.nome_entry = ttk.Entry(self.campos_frame, textvariable=self.nome_var, width=25)
        self.nome_entry.pack(pady=2)

        # Data
        ttk.Label(self.campos_frame, text='Data:', style='Header.TLabel').pack(pady=2)
        self.data_frame = ttk.Frame(self.campos_frame)
        self.data_frame.pack(pady=2)
        
        self.data_var = tk.StringVar()
        self.data_entry = ttk.Entry(self.data_frame, textvariable=self.data_var, width=15, state='readonly')
        self.data_entry.pack(pady=2)
        
        self.cal_btn = ttk.Button(self.data_frame, text='Selecionar Data', command=self.abrir_calendario)
        self.cal_btn.pack(pady=2)

        # Horários
        ttk.Label(self.campos_frame, text='Horário:', style='Header.TLabel').pack(pady=2)
        self.horarios_frame = ttk.Frame(self.campos_frame)
        self.horarios_frame.pack(pady=2, anchor='center', padx=50)

        # Variáveis para horários
        self.hora_inicio_var = tk.StringVar()
        self.hora_fim_var = tk.StringVar()

        valores_horarios = []
        h = datetime.strptime('08:00', '%H:%M')
        hf = datetime.strptime('18:00', '%H:%M')
        while h <= hf:
            valores_horarios.append(h.strftime('%H:%M'))
            h += timedelta(minutes=30)

        ttk.Label(self.horarios_frame, text='Início:', style='TLabel').pack(side=tk.LEFT, padx=(0,5))
        self.hora_inicio_combo = ttk.Combobox(self.horarios_frame, textvariable=self.hora_inicio_var, values=valores_horarios, width=8, state='readonly')
        self.hora_inicio_combo.pack(side=tk.LEFT, padx=(0,15))

        ttk.Label(self.horarios_frame, text='Fim:', style='TLabel').pack(side=tk.LEFT, padx=(0,5))
        self.hora_fim_combo = ttk.Combobox(self.horarios_frame, textvariable=self.hora_fim_var, values=valores_horarios, width=8, state='readonly')
        self.hora_fim_combo.pack(side=tk.LEFT, padx=0)

        # Botões de ação
        self.botoes_frame = ttk.Frame(self.main_frame)
        self.botoes_frame.pack(pady=5)
        
        # Atualizar estilo dos botões de ação com tamanho reduzido
        action_button_style = {'width': 20, 'padding': 4}
        ttk.Button(self.botoes_frame, text='Adicionar Reserva', command=self.adicionar_reserva, **action_button_style).pack(pady=2)
        ttk.Button(self.botoes_frame, text='Editar Reserva', command=self.editar_reserva, **action_button_style).pack(pady=2)
        ttk.Button(self.botoes_frame, text='Excluir Reserva', command=self.excluir_reserva, **action_button_style).pack(pady=2)

        # Frame para exibir reservas atuais com borda e destaque visual
        self.reservas_frame = ttk.Frame(self.main_frame)
        self.reservas_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)
        
        # Adicionar um separador visual antes da seção de reservas
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=5, before=self.reservas_frame)
        
        # Título com estilo mais destacado
        title_frame = ttk.Frame(self.reservas_frame)
        title_frame.pack(fill=tk.X, pady=5)
        ttk.Label(title_frame, text='SALAS RESERVADAS', style='Title.TLabel', anchor='center').pack(fill=tk.X)
        
        # Criar Treeview para exibir as reservas com altura aumentada
        self.tree = ttk.Treeview(self.reservas_frame, columns=('Sala', 'Data', 'Horário', 'Solicitante'), show='headings', height=65)
        self.tree.heading('Sala', text='Sala')
        self.tree.heading('Data', text='Data')
        self.tree.heading('Horário', text='Horário')
        self.tree.heading('Solicitante', text='Solicitante')
        
        # Configurar larguras das colunas
        self.tree.column('Sala', width=120)
        self.tree.column('Data', width=80)
        self.tree.column('Horário', width=120)
        self.tree.column('Solicitante', width=120)
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(self.reservas_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Posicionar Treeview e scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar tags para linhas alternadas
        self.tree.tag_configure('odd', background='#f8f9fa')
        self.tree.tag_configure('even', background='#e9ecef')

        # Remover a redeclaração das variáveis de horário
        # self.hora_inicio_var = tk.StringVar()
        # self.hora_fim_var = tk.StringVar()
        
        # Configurar estilo do Treeview
        self.configurar_estilo_treeview()
        
        self.root.after(300, self.iniciar_db)
        
        # Iniciar o temporizador para atualização automática
        self.iniciar_atualizacao_automatica()
        self.iniciar_limpeza_automatica()
        self.root.after(200, lambda: schedule_update_check(self.root))

    def carregar_logo(self):
        try:
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(os.path.dirname(__file__))
            logo_path = os.path.join(base_path, 'resources', 'logo_rinaldi.png')
            logo_img = Image.open(logo_path)
            max_size = (280, 120)
            logo_img.thumbnail(max_size, Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            self.logo_label = ttk.Label(self.main_frame, image=self.logo_photo)
            self.logo_label.pack(pady=5)
        except Exception as e:
            print(f'Erro ao carregar logo: {e}')
            self.logo_label = ttk.Label(self.main_frame, text='Logo não encontrada')
            self.logo_label.pack(pady=10)

    def iniciar_db(self):
        try:
            self.conectar_bd()
            self.criar_tabelas()
            self.atualizar_lista_reservas()
        except Exception as e:
            print(e)

    def conectar_bd(self):
        try:
            self.conn = mysql.connector.connect(
                host='RINBGWDS',
                user='root',
                password='WSR&28fs@az_19',
                database='reservas_salas',
                connection_timeout=3,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            self.cursor = self.conn.cursor(buffered=True)
            
            # Configurar o formato da data para o padrão brasileiro
            self.cursor.execute("SET lc_time_names = 'pt_BR'")
            self.cursor.execute("SET time_zone = '-03:00'")
            self.conn.commit()
            
        except mysql.connector.Error as err:
            messagebox.showerror('Erro', f'Erro ao conectar ao banco de dados: {err}')

    def criar_tabelas(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS reservas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sala VARCHAR(50) NOT NULL,
                    solicitante VARCHAR(100) NOT NULL,
                    data DATE NOT NULL,
                    hora_inicio TIME NOT NULL,
                    hora_fim TIME NOT NULL
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            ''')
            self.conn.commit()
        except mysql.connector.Error as err:
            messagebox.showerror('Erro', f'Erro ao criar tabelas: {err}')

    def centralizar_janela(self, janela, largura, altura):
        """Centraliza uma janela em relação à janela principal"""
        # Obter as dimensões da tela
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()
        
        # Calcular a posição x e y para centralizar
        x = (largura_tela - largura) // 2
        y = (altura_tela - altura) // 2
        
        # Definir a geometria da janela
        janela.geometry(f'{largura}x{altura}+{x}+{y}')
        janela.resizable(False, False)

    def abrir_calendario(self):
        top = tk.Toplevel(self.root)
        top.title('Selecionar Data')
        cal = Calendar(top, selectmode='day', locale='pt_BR', date_pattern='dd/mm/yyyy')
        cal.pack(padx=10, pady=10)

        def selecionar_data():
            selected_date = cal.get_date()
            try:
                # A data já vem no formato correto do calendário
                self.data_var.set(selected_date)
                top.destroy()
            except ValueError as e:
                messagebox.showerror('Erro', f'Erro no formato da data: {e}')

        ttk.Button(top, text='Selecionar', command=selecionar_data).pack(pady=5)
        
        # Centralizar a janela
        self.centralizar_janela(top, 300, 300)

    def abrir_seletor_horario_manual(self):
        top = tk.Toplevel(self.root)
        top.title('Selecionar Horário')
        top.configure(bg='#f8f9fa')
        frame = ttk.Frame(top, style='MainFrame.TFrame')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        inicio_var = tk.StringVar(value=self.hora_inicio_var.get() or '08:00')
        fim_var = tk.StringVar(value=self.hora_fim_var.get() or '08:30')

        valores = []
        h = datetime.strptime('08:00', '%H:%M')
        hf = datetime.strptime('18:00', '%H:%M')
        while h <= hf:
            valores.append(h.strftime('%H:%M'))
            h += timedelta(minutes=30)

        ttk.Label(frame, text='Início:', style='TLabel').pack(pady=5)
        inicio_combo = ttk.Combobox(frame, textvariable=inicio_var, values=valores, width=10)
        inicio_combo.pack(pady=5)

        ttk.Label(frame, text='Fim:', style='TLabel').pack(pady=5)
        fim_combo = ttk.Combobox(frame, textvariable=fim_var, values=valores, width=10)
        fim_combo.pack(pady=5)

        def aplicar():
            if not self.sala_var.get() or not self.data_var.get():
                messagebox.showwarning('Aviso', 'Por favor, selecione a sala e a data.')
                return
            try:
                t_inicio = datetime.strptime(inicio_var.get(), '%H:%M')
                t_fim = datetime.strptime(fim_var.get(), '%H:%M')
                if t_fim <= t_inicio:
                    messagebox.showerror('Erro', 'Hora de fim deve ser maior que a de início.')
                    return
                if not self.verificar_horario_disponivel(inicio_var.get(), fim_var.get()):
                    messagebox.showerror('Erro', 'Este horário está indisponível.')
                    return
                self.hora_inicio_var.set(inicio_var.get())
                self.hora_fim_var.set(fim_var.get())
                top.destroy()
            except Exception as e:
                messagebox.showerror('Erro', f'Erro no formato da hora: {e}')

        ttk.Button(frame, text='Aplicar', command=aplicar).pack(pady=5)
        ttk.Button(frame, text='Cancelar', command=top.destroy).pack(pady=5)
        self.centralizar_janela(top, 300, 250)

    def adicionar_reserva(self):
        # Verificar se todos os campos estão preenchidos
        if not all([self.sala_var.get(), self.nome_var.get(), self.data_var.get(),
                    self.hora_inicio_var.get(), self.hora_fim_var.get()]):
            messagebox.showwarning('Aviso', 'Por favor, preencha todos os campos.')
            return

        try:
            # Verificar novamente a disponibilidade antes de adicionar
            if not self.verificar_horario_disponivel(self.hora_inicio_var.get(), self.hora_fim_var.get()):
                messagebox.showerror('Erro', 'Este horário já não está mais disponível. Por favor, escolha outro horário.')
                return

            # Converter a data para o formato do banco de dados
            data_obj = datetime.strptime(self.data_var.get(), '%d/%m/%Y').date()
            hora_inicio_obj = datetime.strptime(self.hora_inicio_var.get(), '%H:%M').time()
            hora_fim_obj = datetime.strptime(self.hora_fim_var.get(), '%H:%M').time()

            if hora_fim_obj <= hora_inicio_obj:
                messagebox.showerror('Erro', 'Hora de fim deve ser maior que a de início.')
                return

            # Inserir a reserva
            self.cursor.execute('''
                INSERT INTO reservas (sala, solicitante, data, hora_inicio, hora_fim)
                VALUES (%s, %s, %s, %s, %s)
            ''', (self.sala_var.get(), self.nome_var.get(), data_obj, hora_inicio_obj, hora_fim_obj))

            self.conn.commit()
            messagebox.showinfo('Sucesso', 'Reserva adicionada com sucesso!')
            
            # Limpar os campos após adicionar
            self.limpar_campos()
            # Atualizar a lista de reservas
            self.atualizar_lista_reservas()

        except mysql.connector.Error as err:
            messagebox.showerror('Erro', f'Erro ao adicionar reserva: {err}')
            self.conn.rollback()

    def limpar_campos(self):
        self.sala_var.set('')
        self.nome_var.set('')
        self.data_var.set('')
        self.hora_inicio_var.set('')
        self.hora_fim_var.set('')
        
    def atualizar_lista_reservas(self):
        # Limpar itens existentes
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            # Sempre fechar e reconectar ao banco de dados para garantir dados atualizados
            if hasattr(self, 'conn') and self.conn is not None:
                try:
                    if self.conn.is_connected():
                        self.cursor.close()
                        self.conn.close()
                except Exception as e:
                    print(f"Erro ao fechar conexão existente: {e}")
            
            # Estabelecer uma nova conexão
            try:
                self.conectar_bd()
                print("Conexão estabelecida para atualização da lista")
            except Exception as e:
                print(f"Erro ao conectar ao banco de dados: {e}")
                return  # Sair da função se não conseguir conectar
            
            # Buscar todas as reservas com uma conexão fresca
            self.cursor.execute('''
                SELECT sala, data, TIME_FORMAT(hora_inicio, '%H:%i') as hora_inicio, 
                       TIME_FORMAT(hora_fim, '%H:%i') as hora_fim, solicitante
                FROM reservas
                ORDER BY data, hora_inicio
            ''')
            reservas = self.cursor.fetchall()
            
            # Adicionar reservas na Treeview com cores alternadas
            for i, reserva in enumerate(reservas):
                sala = reserva[0]
                data = reserva[1].strftime('%d/%m/%Y')
                horario = f'{reserva[2]} - {reserva[3]}'
                solicitante = reserva[4]
                # Aplicar tag 'odd' ou 'even' para alternar cores das linhas
                tag = 'odd' if i % 2 == 0 else 'even'
                self.tree.insert('', tk.END, values=(sala, data, horario, solicitante), tags=(tag,))
            
            # Garantir que a configuração de estilo seja aplicada
            self.configurar_estilo_treeview()
                
        except mysql.connector.Error as err:
            print(f'Erro ao buscar reservas: {err}')
            # Tentar reconectar na próxima atualização automática
        except Exception as e:
            print(f'Erro inesperado na atualização da lista: {e}')
            # Usar print em vez de messagebox para erros durante atualizações automáticas
            # para não interromper a experiência do usuário com muitas mensagens de erro

    def gerar_horarios_disponiveis(self):
        horarios = []

        try:
            data_obj = datetime.strptime(self.data_var.get(), '%d/%m/%Y').date()

            hora_atual = datetime.strptime('08:00', '%H:%M')
            hora_fim_dia = datetime.strptime('18:00', '%H:%M')

            while hora_atual < hora_fim_dia:
                hora_fim = hora_atual + timedelta(minutes=30)
                inicio = hora_atual.strftime('%H:%M')
                fim = hora_fim.strftime('%H:%M')

                hora_inicio_obj = datetime.strptime(inicio, '%H:%M').time()
                hora_fim_obj = datetime.strptime(fim, '%H:%M').time()

                self.cursor.execute("""
                    SELECT COUNT(*) FROM reservas
                    WHERE sala = %s AND data = %s
                    AND (
                        (hora_inicio < %s AND hora_fim > %s)
                        OR (hora_inicio < %s AND hora_fim > %s)
                        OR (hora_inicio >= %s AND hora_fim <= %s)
                    )
                """, (self.sala_var.get(), data_obj, hora_fim_obj, hora_inicio_obj,
                       hora_inicio_obj, hora_inicio_obj, hora_inicio_obj, hora_fim_obj))

                count = self.cursor.fetchone()[0]
                disponivel = count == 0

                horarios.append({
                    'inicio': inicio,
                    'fim': fim,
                    'disponivel': disponivel
                })

                hora_atual = hora_fim

        except Exception as e:
            messagebox.showerror('Erro', f'Erro ao verificar disponibilidade: {e}')
            return []

        return horarios

    def verificar_horario_disponivel(self, hora_inicio, hora_fim):
        try:
            # Converter a data para o formato do banco de dados
            data_obj = datetime.strptime(self.data_var.get(), '%d/%m/%Y').date()
            hora_inicio_obj = datetime.strptime(hora_inicio, '%H:%M').time()
            hora_fim_obj = datetime.strptime(hora_fim, '%H:%M').time()

            # Consultar reservas que se sobrepõem ao horário solicitado
            # Corrigido para permitir reservas adjacentes (ex: 09:00-10:00 e 10:00-11:00)
            self.cursor.execute("""
                SELECT COUNT(*) FROM reservas
                WHERE sala = %s
                AND data = %s
                AND (
                    (hora_inicio < %s AND hora_fim > %s) -- Verifica se o início da nova reserva está dentro de uma existente
                    OR (hora_inicio < %s AND hora_fim > %s) -- Verifica se o fim da nova reserva está dentro de uma existente
                    OR (hora_inicio >= %s AND hora_fim <= %s) -- Verifica se a nova reserva contém uma existente
                )
            """, (self.sala_var.get(), data_obj, hora_fim_obj, hora_inicio_obj, hora_inicio_obj, hora_inicio_obj, hora_inicio_obj, hora_fim_obj))

            count = self.cursor.fetchone()[0]
            return count == 0

        except mysql.connector.Error as err:
            messagebox.showerror('Erro', f'Erro ao verificar horário: {err}')
            return False
        except ValueError as err:
            messagebox.showerror('Erro', f'Erro no formato da data ou hora: {err}')
            return False

    def configurar_estilo_treeview(self):
        # Configurar estilo do Treeview com cores alternadas para as linhas
        self.style.configure('Treeview',
                            background='#ffffff',
                            fieldbackground='#ffffff',
                            foreground='#2c3e50',
                            rowheight=30,
                            font=('Segoe UI', 10),
                            borderwidth=1,
                            relief='solid')
        self.style.configure('Treeview.Heading',
                            font=('Segoe UI', 10, 'bold'),
                            background='#f8f9fa',
                            foreground='#2c3e50',
                            padding=5,
                            relief='raised')
        self.style.map('Treeview',
                      background=[('selected', '#3498db')],
                      foreground=[('selected', '#ffffff')])
        
        # Configurar tags para linhas alternadas se a árvore já estiver criada
        if hasattr(self, 'tree'):
            self.tree.tag_configure('odd', background='#f8f9fa')
            self.tree.tag_configure('even', background='#e9ecef')

    def verificar_disponibilidade(self):
        if not all([self.sala_var.get(), self.data_var.get(), self.hora_inicio_var.get(), self.hora_fim_var.get()]):
            messagebox.showwarning('Aviso', 'Por favor, selecione sala, data, início e fim.')
            return
        try:
            disponivel = self.verificar_horario_disponivel(self.hora_inicio_var.get(), self.hora_fim_var.get())
            if disponivel:
                if hasattr(self, 'horario_status_label'):
                    self.horario_status_label.configure(text='Status: Livre')
                messagebox.showinfo('Disponibilidade', 'Horário livre para reserva.')
            else:
                data_obj = datetime.strptime(self.data_var.get(), '%d/%m/%Y').date()
                hora_inicio_obj = datetime.strptime(self.hora_inicio_var.get(), '%H:%M').time()
                hora_fim_obj = datetime.strptime(self.hora_fim_var.get(), '%H:%M').time()
                self.cursor.execute(
                    """
                    SELECT solicitante FROM reservas
                    WHERE sala = %s AND data = %s
                    AND (
                        (hora_inicio < %s AND hora_fim > %s)
                        OR (hora_inicio < %s AND hora_fim > %s)
                        OR (hora_inicio >= %s AND hora_fim <= %s)
                    )
                    ORDER BY hora_inicio
                    LIMIT 1
                    """,
                    (self.sala_var.get(), data_obj, hora_fim_obj, hora_inicio_obj, hora_inicio_obj, hora_inicio_obj, hora_inicio_obj, hora_fim_obj),
                )
                row = self.cursor.fetchone()
                reservado_por = row[0] if row else ''
                if hasattr(self, 'horario_status_label'):
                    if reservado_por:
                        self.horario_status_label.configure(text=f'Status: Ocupado (Solicitante: {reservado_por})')
                    else:
                        self.horario_status_label.configure(text='Status: Ocupado')
                if reservado_por:
                    messagebox.showerror('Disponibilidade', f'Horário ocupado por {reservado_por}.')
                else:
                    messagebox.showerror('Disponibilidade', 'Horário ocupado.')
        except mysql.connector.Error as err:
            messagebox.showerror('Erro', f'Erro ao verificar disponibilidade: {err}')
        except ValueError as err:
            messagebox.showerror('Erro', f'Erro no formato da data ou hora: {err}')

    def selecionar_horario(self, inicio, fim, janela):
        self.hora_inicio_var.set(inicio)
        self.hora_fim_var.set(fim)
        janela.destroy()

    def editar_reserva(self):
        # Verificar se uma reserva foi selecionada
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning('Aviso', 'Por favor, selecione uma reserva para editar.')
            return

        # Obter dados da reserva selecionada
        item = self.tree.item(selected_item[0])
        sala, data, horario, solicitante = item['values']
        hora_inicio, hora_fim = horario.split(' - ')
        
        # Abrir janela de edição
        self.abrir_janela_edicao(sala, data, hora_inicio, hora_fim, solicitante, selected_item[0])
        
    def abrir_janela_edicao(self, sala, data, hora_inicio, hora_fim, solicitante, item_id):
        # Criar janela de edição
        edit_window = tk.Toplevel(self.root)
        edit_window.title('Editar Reserva')
        edit_window.configure(bg='#f8f9fa')
        
        # Frame principal
        main_frame = ttk.Frame(edit_window, style='MainFrame.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Título
        ttk.Label(main_frame, text='Editar Reserva', style='Header.TLabel').pack(pady=10)
        
        # Container para os campos
        campos_frame = ttk.Frame(main_frame)
        campos_frame.pack(fill=tk.X, pady=5)
        
        # Variáveis para os campos
        sala_var = tk.StringVar(value=sala)
        nome_var = tk.StringVar(value=solicitante)
        data_var = tk.StringVar(value=data)
        hora_inicio_var = tk.StringVar(value=hora_inicio)
        hora_fim_var = tk.StringVar(value=hora_fim)
        
        # Seleção de sala
        ttk.Label(campos_frame, text='Selecione a Sala:', style='Header.TLabel').pack(pady=1)
        salas = ['Rally', 'Motocross', 'Freestyle', 'Arena Cross', 'Enduro']
        sala_combo = ttk.Combobox(campos_frame, textvariable=sala_var, values=salas, width=25)
        sala_combo.pack(pady=1)
        
        # Nome do solicitante
        ttk.Label(campos_frame, text='Nome do Solicitante:', style='Header.TLabel').pack(pady=2)
        nome_entry = ttk.Entry(campos_frame, textvariable=nome_var, width=25)
        nome_entry.pack(pady=2)
        
        # Data
        ttk.Label(campos_frame, text='Data:', style='Header.TLabel').pack(pady=2)
        data_frame = ttk.Frame(campos_frame)
        data_frame.pack(pady=2)
        
        data_entry = ttk.Entry(data_frame, textvariable=data_var, width=15, state='readonly')
        data_entry.pack(side=tk.LEFT, padx=5)
        
        # Função para abrir calendário na janela de edição
        def abrir_calendario_edicao():
            cal_top = tk.Toplevel(edit_window)
            cal_top.title('Selecionar Data')
            cal = Calendar(cal_top, selectmode='day', locale='pt_BR', date_pattern='dd/mm/yyyy')
            cal.pack(padx=10, pady=10)

            def selecionar_data():
                selected_date = cal.get_date()
                try:
                    # A data já vem no formato correto do calendário
                    data_var.set(selected_date)
                    cal_top.destroy()
                except ValueError as e:
                    messagebox.showerror('Erro', f'Erro no formato da data: {e}')

            ttk.Button(cal_top, text='Selecionar', command=selecionar_data).pack(pady=5)
            
            # Centralizar a janela do calendário
            self.centralizar_janela(cal_top, 300, 300)
        
        cal_btn = ttk.Button(data_frame, text='Selecionar Data', command=abrir_calendario_edicao)
        cal_btn.pack(side=tk.LEFT)
        
        # Horários
        ttk.Label(campos_frame, text='Horário:', style='Header.TLabel').pack(pady=2)
        horarios_frame = ttk.Frame(campos_frame)
        horarios_frame.pack(pady=2)
        
        valores_horarios = []
        h = datetime.strptime('08:00', '%H:%M')
        hf = datetime.strptime('18:00', '%H:%M')
        while h <= hf:
            valores_horarios.append(h.strftime('%H:%M'))
            h += timedelta(minutes=30)

        ttk.Label(horarios_frame, text='Início:', style='TLabel').pack(side=tk.LEFT, padx=5)
        hora_inicio_combo = ttk.Combobox(horarios_frame, textvariable=hora_inicio_var, values=valores_horarios, width=8, state='readonly')
        hora_inicio_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(horarios_frame, text='Fim:', style='TLabel').pack(side=tk.LEFT, padx=5)
        hora_fim_combo = ttk.Combobox(horarios_frame, textvariable=hora_fim_var, values=valores_horarios, width=8, state='readonly')
        hora_fim_combo.pack(side=tk.LEFT, padx=5)
        
        status_label_edicao = ttk.Label(campos_frame, text='Status:')
        status_label_edicao.pack(pady=5)

        def verificar_disponibilidade_edicao():
            if not all([sala_var.get(), data_var.get(), hora_inicio_var.get(), hora_fim_var.get()]):
                messagebox.showwarning('Aviso', 'Por favor, selecione sala, data, início e fim.')
                return
            try:
                data_obj = datetime.strptime(data_var.get(), '%d/%m/%Y').date()
                hora_inicio_obj = datetime.strptime(hora_inicio_var.get(), '%H:%M').time()
                hora_fim_obj = datetime.strptime(hora_fim_var.get(), '%H:%M').time()
                if hora_fim_obj <= hora_inicio_obj:
                    messagebox.showerror('Erro', 'Hora de fim deve ser maior que a de início.')
                    return
                self.cursor.execute(
                    """
                    SELECT COUNT(*) FROM reservas
                    WHERE sala = %s
                    AND data = %s
                    AND (
                        (hora_inicio < %s AND hora_fim > %s)
                        OR (hora_inicio < %s AND hora_fim > %s)
                        OR (hora_inicio >= %s AND hora_fim <= %s)
                    )
                    AND NOT (sala = %s AND data = %s AND hora_inicio = %s AND solicitante = %s)
                    """,
                    (sala_var.get(), data_obj, hora_fim_obj, hora_inicio_obj, hora_inicio_obj, hora_inicio_obj, hora_inicio_obj, hora_fim_obj,
                     sala, datetime.strptime(data, '%d/%m/%Y').date(), datetime.strptime(hora_inicio, '%H:%M').time(), solicitante),
                )
                count = self.cursor.fetchone()[0]
                if count == 0:
                    status_label_edicao.configure(text='Status: Livre')
                    messagebox.showinfo('Disponibilidade', 'Horário livre para reserva.')
                else:
                    self.cursor.execute(
                        """
                        SELECT solicitante FROM reservas
                        WHERE sala = %s AND data = %s
                        AND (
                            (hora_inicio < %s AND hora_fim > %s)
                            OR (hora_inicio < %s AND hora_fim > %s)
                            OR (hora_inicio >= %s AND hora_fim <= %s)
                        )
                        ORDER BY hora_inicio
                        LIMIT 1
                        """,
                        (sala_var.get(), data_obj, hora_fim_obj, hora_inicio_obj, hora_inicio_obj, hora_inicio_obj, hora_inicio_obj, hora_fim_obj),
                    )
                    row = self.cursor.fetchone()
                    reservado_por = row[0] if row else ''
                    if reservado_por:
                        status_label_edicao.configure(text=f'Status: Ocupado (Solicitante: {reservado_por})')
                        messagebox.showerror('Disponibilidade', f'Horário ocupado por {reservado_por}.')
                    else:
                        status_label_edicao.configure(text='Status: Ocupado')
                        messagebox.showerror('Disponibilidade', 'Horário ocupado.')
            except mysql.connector.Error as err:
                messagebox.showerror('Erro', f'Erro ao verificar disponibilidade: {err}')
            except ValueError as err:
                messagebox.showerror('Erro', f'Erro no formato da data ou hora: {err}')
        
        # Botões de ação
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(pady=10)
        
        # Estilo dos botões
        action_button_style = {'width': 20, 'padding': 4}
        
        
        # Função para salvar as alterações
        def salvar_alteracoes():
            if not all([sala_var.get(), nome_var.get(), data_var.get(),
                        hora_inicio_var.get(), hora_fim_var.get()]):
                messagebox.showwarning('Aviso', 'Por favor, preencha todos os campos.')
                return
            try:
                data_obj = datetime.strptime(data_var.get(), '%d/%m/%Y').date()
                hora_inicio_obj = datetime.strptime(hora_inicio_var.get(), '%H:%M').time()
                hora_fim_obj = datetime.strptime(hora_fim_var.get(), '%H:%M').time()

                if hora_fim_obj <= hora_inicio_obj:
                    messagebox.showerror('Erro', 'Hora de fim deve ser maior que a de início.')
                    return

                self.cursor.execute("""
                    SELECT COUNT(*) FROM reservas
                    WHERE sala = %s
                    AND data = %s
                    AND (
                        (hora_inicio < %s AND hora_fim > %s) 
                        OR (hora_inicio < %s AND hora_fim > %s) 
                        OR (hora_inicio >= %s AND hora_fim <= %s)
                    )
                    AND NOT (sala = %s AND data = %s AND hora_inicio = %s AND solicitante = %s)
                """, (sala_var.get(), data_obj, 
                       hora_fim_obj, hora_inicio_obj, 
                       hora_inicio_obj, hora_inicio_obj, 
                       hora_inicio_obj, hora_fim_obj,
                       sala, datetime.strptime(data, '%d/%m/%Y').date(),
                       datetime.strptime(hora_inicio, '%H:%M').time(), solicitante))
                
                count = self.cursor.fetchone()[0]
                if count > 0:
                    messagebox.showerror('Erro', 'Este horário já está reservado. Por favor, escolha outro horário.')
                    return
                
                self.cursor.execute('''
                    UPDATE reservas
                    SET sala = %s, solicitante = %s, data = %s, hora_inicio = %s, hora_fim = %s
                    WHERE sala = %s AND data = %s AND hora_inicio = %s AND solicitante = %s
                ''', (sala_var.get(), nome_var.get(), data_obj, hora_inicio_obj, hora_fim_obj,
                      sala, datetime.strptime(data, '%d/%m/%Y').date(),
                      datetime.strptime(hora_inicio, '%H:%M').time(), solicitante))
                
                self.conn.commit()
                messagebox.showinfo('Sucesso', 'Reserva atualizada com sucesso!')
                edit_window.destroy()
                self.atualizar_lista_reservas()
            except mysql.connector.Error as err:
                messagebox.showerror('Erro', f'Erro ao atualizar reserva: {err}')
                self.conn.rollback()
            except ValueError as err:
                messagebox.showerror('Erro', f'Erro no formato da data ou hora: {err}')
        
        # Botão para salvar alterações
        ttk.Button(botoes_frame, 
                  text='Salvar Alterações', 
                  command=salvar_alteracoes, 
                  **action_button_style).pack(pady=2)
        
        # Botão para cancelar
        ttk.Button(botoes_frame, 
                  text='Cancelar', 
                  command=edit_window.destroy, 
                  **action_button_style).pack(pady=2)
        
        # Centralizar a janela de edição
        self.centralizar_janela(edit_window, 450, 600)

    def abrir_seletor_horario_manual_edicao(self, hora_inicio_var, hora_fim_var, sala_var, data_var, parent):
        top = tk.Toplevel(parent)
        top.title('Selecionar Horário')
        top.configure(bg='#f8f9fa')
        frame = ttk.Frame(top, style='MainFrame.TFrame')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        inicio_var = tk.StringVar(value=hora_inicio_var.get() or '08:00')
        fim_var = tk.StringVar(value=hora_fim_var.get() or '08:30')

        valores = []
        h = datetime.strptime('08:00', '%H:%M')
        hf = datetime.strptime('18:00', '%H:%M')
        while h <= hf:
            valores.append(h.strftime('%H:%M'))
            h += timedelta(minutes=30)

        ttk.Label(frame, text='Início:', style='TLabel').pack(pady=5)
        inicio_combo = ttk.Combobox(frame, textvariable=inicio_var, values=valores, width=10)
        inicio_combo.pack(pady=5)

        ttk.Label(frame, text='Fim:', style='TLabel').pack(pady=5)
        fim_combo = ttk.Combobox(frame, textvariable=fim_var, values=valores, width=10)
        fim_combo.pack(pady=5)

        def disponibilidade_local(inicio, fim):
            try:
                data_obj = datetime.strptime(data_var.get(), '%d/%m/%Y').date()
                hora_inicio_obj = datetime.strptime(inicio, '%H:%M').time()
                hora_fim_obj = datetime.strptime(fim, '%H:%M').time()
                self.cursor.execute(
                    """
                    SELECT COUNT(*) FROM reservas
                    WHERE sala = %s
                    AND data = %s
                    AND (
                        (hora_inicio < %s AND hora_fim > %s)
                        OR (hora_inicio < %s AND hora_fim > %s)
                        OR (hora_inicio >= %s AND hora_fim <= %s)
                    )
                    """,
                    (sala_var.get(), data_obj, hora_fim_obj, hora_inicio_obj, hora_inicio_obj, hora_inicio_obj, hora_inicio_obj, hora_fim_obj),
                )
                count = self.cursor.fetchone()[0]
                return count == 0
            except Exception:
                return False

        def aplicar():
            if not sala_var.get() or not data_var.get():
                messagebox.showwarning('Aviso', 'Por favor, selecione a sala e a data.')
                return
            try:
                t_inicio = datetime.strptime(inicio_var.get(), '%H:%M')
                t_fim = datetime.strptime(fim_var.get(), '%H:%M')
                if t_fim <= t_inicio:
                    messagebox.showerror('Erro', 'Hora de fim deve ser maior que a de início.')
                    return
                if not disponibilidade_local(inicio_var.get(), fim_var.get()):
                    messagebox.showerror('Erro', 'Este horário está indisponível.')
                    return
                hora_inicio_var.set(inicio_var.get())
                hora_fim_var.set(fim_var.get())
                top.destroy()
            except Exception as e:
                messagebox.showerror('Erro', f'Erro no formato da hora: {e}')

        ttk.Button(frame, text='Aplicar', command=aplicar).pack(pady=5)
        ttk.Button(frame, text='Cancelar', command=top.destroy).pack(pady=5)
        self.centralizar_janela(top, 300, 250)

    def excluir_reserva(self):
        # Verificar se uma reserva foi selecionada
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning('Aviso', 'Por favor, selecione uma reserva para excluir.')
            return

        # Obter dados da reserva selecionada
        item = self.tree.item(selected_item[0])
        sala, data, horario, solicitante = item['values']
        hora_inicio = horario.split(' - ')[0]

        # Confirmar exclusão
        if messagebox.askyesno('Confirmar', 'Tem certeza que deseja excluir esta reserva?'):
            try:
                # Converter a data para o formato do banco de dados
                data_obj = datetime.strptime(data, '%d/%m/%Y').date()
                hora_inicio_obj = datetime.strptime(hora_inicio, '%H:%M').time()

                # Excluir a reserva do banco de dados
                self.cursor.execute('''
                    DELETE FROM reservas
                    WHERE sala = %s AND data = %s AND hora_inicio = %s AND solicitante = %s
                ''', (sala, data_obj, hora_inicio_obj, solicitante))

                self.conn.commit()
                messagebox.showinfo('Sucesso', 'Reserva excluída com sucesso!')
                
                # Limpar os campos e atualizar a lista
                self.limpar_campos()
                self.atualizar_lista_reservas()

            except mysql.connector.Error as err:
                messagebox.showerror('Erro', f'Erro ao excluir reserva: {err}')
                self.conn.rollback()
            except ValueError as err:
                messagebox.showerror('Erro', f'Erro no formato da data ou hora: {err}')

    def iniciar_atualizacao_automatica(self):
        """Inicia o temporizador para atualização automática das reservas"""
        # Cancelar qualquer temporizador existente para evitar múltiplas instâncias
        if self.update_timer is not None:
            self.root.after_cancel(self.update_timer)
        
        # Executar uma atualização imediata antes de programar a próxima
        self.atualizar_lista_reservas()
        
        # Programar a próxima atualização
        self.update_timer = self.root.after(self.update_interval, self.executar_atualizacao_automatica)
    
    def executar_atualizacao_automatica(self):
        """Executa a atualização automática e agenda a próxima"""
        try:
            # Não precisamos verificar a conexão aqui, pois atualizar_lista_reservas já faz isso
            # e sempre estabelece uma nova conexão para garantir dados atualizados
            
            # Atualizar a lista de reservas (isso já inclui reconexão ao banco)
            self.atualizar_lista_reservas()
            
            # Agendar a próxima atualização
            self.update_timer = self.root.after(self.update_interval, self.executar_atualizacao_automatica)
        except Exception as e:
            print(f"Erro na atualização automática: {e}")
            # Sempre agendar a próxima atualização, mesmo em caso de erro
            self.update_timer = self.root.after(self.update_interval, self.executar_atualizacao_automatica)

    def limpar_reservas_expiradas(self):
        try:
            if not hasattr(self, 'conn') or self.conn is None or not self.conn.is_connected():
                self.conectar_bd()
            self.cursor.execute("DELETE FROM reservas WHERE DATEDIFF(CURDATE(), data) >= %s", (5,))
            self.conn.commit()
        except mysql.connector.Error as err:
            print(f'Erro ao limpar reservas expiradas: {err}')
        except Exception as e:
            print(e)

    def iniciar_limpeza_automatica(self):
        if self.cleanup_timer is not None:
            self.root.after_cancel(self.cleanup_timer)
        self.limpar_reservas_expiradas()
        self.cleanup_timer = self.root.after(self.cleanup_interval, self.executar_limpeza_automatica)

    def executar_limpeza_automatica(self):
        try:
            self.limpar_reservas_expiradas()
        except Exception as e:
            print(e)
        finally:
            self.cleanup_timer = self.root.after(self.cleanup_interval, self.executar_limpeza_automatica)

if __name__ == '__main__':
    try:
        import pyi_splash
        pyi_splash.close()
    except Exception:
        pass
    root = tk.Tk()
    app = SistemaReservas(root)
    root.mainloop()
