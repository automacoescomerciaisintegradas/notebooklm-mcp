"""
NotebookLM MCP Server Manager — GUI Principal
Interface grafica completa com Tkinter.
"""

import sys
import os
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext, filedialog
except ImportError:
    print("[ERRO] Tkinter nao encontrado. Instale com: pip install tk")
    sys.exit(1)

from cli.server_manager import ServerManager
from cli.config_util import (
    load_servers_config,
    save_servers_config,
    load_app_config,
    save_app_config,
    SUPPORTED_CLIENTS,
)

# === Cores do Design System ACI ===
COLORS = {
    "bg_primary": "#02030a",
    "bg_secondary": "#05070c",
    "bg_card": "#0d1117",
    "bg_input": "#161b22",
    "border": "#30363d",
    "text_primary": "#e5e7eb",
    "text_secondary": "#8b949e",
    "accent": "#5B7CFF",
    "accent_hover": "#7B96FF",
    "danger": "#ef4444",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "brand_red": "#ef4444",
}


class MCPServerManagerApp:
    """Aplicacao GUI do MCP Server Manager."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NotebookLM MCP Server Manager")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        self.root.configure(bg=COLORS["bg_primary"])

        # Icone (se disponivel)
        icon_path = PROJECT_ROOT / "gui" / "assets" / "icon.ico"
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))

        self.manager = ServerManager(PROJECT_ROOT)
        self.refresh_interval = 3000  # ms

        self._build_ui()
        self._refresh_servers()

    def _build_ui(self):
        """Constroi toda a interface."""
        # === Header ===
        header = tk.Frame(self.root, bg=COLORS["bg_secondary"], height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title_frame = tk.Frame(header, bg=COLORS["bg_secondary"])
        title_frame.pack(side="left", padx=20, pady=10)

        tk.Label(
            title_frame,
            text="NotebookLM MCP Server Manager",
            font=("Segoe UI", 18, "bold"),
            fg=COLORS["accent"],
            bg=COLORS["bg_secondary"],
        ).pack(anchor="w")

        tk.Label(
            title_frame,
            text="The AI that actually does things.",
            font=("Segoe UI", 10),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_secondary"],
        ).pack(anchor="w")

        # Status badge
        self.status_label = tk.Label(
            header,
            text="0 servidores",
            font=("Segoe UI", 10),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
            padx=12,
            pady=4,
        )
        self.status_label.pack(side="right", padx=20)

        # === Main Content ===
        main = tk.Frame(self.root, bg=COLORS["bg_primary"])
        main.pack(fill="both", expand=True, padx=15, pady=10)

        # Left panel — Server List
        left = tk.Frame(main, bg=COLORS["bg_card"], width=400)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Toolbar
        toolbar = tk.Frame(left, bg=COLORS["bg_card"])
        toolbar.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(
            toolbar,
            text="Servidores MCP",
            font=("Segoe UI", 13, "bold"),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
        ).pack(side="left")

        btn_add = tk.Button(
            toolbar,
            text="+ Adicionar",
            font=("Segoe UI", 9),
            fg=COLORS["text_primary"],
            bg=COLORS["accent"],
            activebackground=COLORS["accent_hover"],
            activeforeground=COLORS["text_primary"],
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._show_add_dialog,
        )
        btn_add.pack(side="right")

        btn_refresh = tk.Button(
            toolbar,
            text="Atualizar",
            font=("Segoe UI", 9),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_input"],
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._refresh_servers,
        )
        btn_refresh.pack(side="right", padx=(0, 8))

        # Server list
        list_frame = tk.Frame(left, bg=COLORS["bg_card"])
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("name", "status", "transport", "pid")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15,
        )
        self.tree.heading("name", text="Nome")
        self.tree.heading("status", text="Status")
        self.tree.heading("transport", text="Transporte")
        self.tree.heading("pid", text="PID")

        self.tree.column("name", width=180, minwidth=120)
        self.tree.column("status", width=90, minwidth=70)
        self.tree.column("transport", width=80, minwidth=60)
        self.tree.column("pid", width=70, minwidth=50)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Right panel — Details + Logs
        right = tk.Frame(main, bg=COLORS["bg_card"], width=400)
        right.pack(side="right", fill="both", expand=True, padx=(8, 0))

        # Server details
        details_frame = tk.Frame(right, bg=COLORS["bg_card"])
        details_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(
            details_frame,
            text="Detalhes do Servidor",
            font=("Segoe UI", 13, "bold"),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
        ).pack(anchor="w")

        self.details_text = tk.Label(
            details_frame,
            text="Selecione um servidor na lista",
            font=("Segoe UI", 10),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card"],
            justify="left",
            anchor="w",
        )
        self.details_text.pack(fill="x", pady=(5, 0))

        # Action buttons
        actions = tk.Frame(right, bg=COLORS["bg_card"])
        actions.pack(fill="x", padx=10, pady=(0, 10))

        self.btn_start = tk.Button(
            actions,
            text="Iniciar",
            font=("Segoe UI", 9),
            fg="white",
            bg=COLORS["success"],
            bd=0,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self._start_selected,
        )
        self.btn_start.pack(side="left", padx=(0, 5))

        self.btn_stop = tk.Button(
            actions,
            text="Parar",
            font=("Segoe UI", 9),
            fg="white",
            bg=COLORS["danger"],
            bd=0,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self._stop_selected,
        )
        self.btn_stop.pack(side="left", padx=(0, 5))

        self.btn_restart = tk.Button(
            actions,
            text="Reiniciar",
            font=("Segoe UI", 9),
            fg="white",
            bg=COLORS["warning"],
            bd=0,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self._restart_selected,
        )
        self.btn_restart.pack(side="left", padx=(0, 5))

        self.btn_remove = tk.Button(
            actions,
            text="Remover",
            font=("Segoe UI", 9),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_input"],
            bd=0,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self._remove_selected,
        )
        self.btn_remove.pack(side="left", padx=(0, 5))

        self.btn_configure = tk.Button(
            actions,
            text="Configurar Cliente",
            font=("Segoe UI", 9),
            fg=COLORS["text_primary"],
            bg=COLORS["accent"],
            bd=0,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self._configure_client,
        )
        self.btn_configure.pack(side="right")

        # Logs
        log_frame = tk.Frame(right, bg=COLORS["bg_card"])
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tk.Label(
            log_frame,
            text="Logs em Tempo Real",
            font=("Segoe UI", 11, "bold"),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
        ).pack(anchor="w", pady=(0, 5))

        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            font=("Cascadia Code", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            selectbackground=COLORS["accent"],
            bd=0,
            wrap="word",
            state="disabled",
            height=12,
        )
        self.log_area.pack(fill="both", expand=True)

        # === Footer ===
        footer = tk.Frame(self.root, bg=COLORS["bg_secondary"], height=35)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        tk.Label(
            footer,
            text="(c) Automacoes Comerciais Integradas 2026 | contato@automacoescomerciais.com.br",
            font=("Segoe UI", 8),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_secondary"],
        ).pack(side="left", padx=15, pady=8)

        tk.Label(
            footer,
            text="v1.0.0",
            font=("Segoe UI", 8),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_secondary"],
        ).pack(side="right", padx=15, pady=8)

    def _refresh_servers(self):
        """Atualiza lista de servidores."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        servers = self.manager.list_servers()
        for srv in servers:
            status = "Rodando" if srv.get("running") else "Parado"
            pid = str(srv.get("pid", "-"))
            self.tree.insert("", "end", values=(
                srv["name"],
                status,
                srv.get("transport", "stdio"),
                pid,
            ))

        running = sum(1 for s in servers if s.get("running"))
        self.status_label.config(
            text=f"{len(servers)} servidores | {running} rodando",
            bg=COLORS["success"] if running > 0 else COLORS["bg_card"],
        )

        # Auto-refresh
        self.root.after(self.refresh_interval, self._refresh_servers)

    def _on_select(self, event):
        """Evento de selecao na treeview."""
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        name = values[0]
        info = self.manager.get_server_info(name)
        if info:
            details = (
                f"Nome: {info.get('name', name)}\n"
                f"Comando: {info.get('command', '-')}\n"
                f"Transporte: {info.get('transport', 'stdio')}\n"
                f"Status: {'Rodando' if info.get('running') else 'Parado'}\n"
                f"PID: {info.get('pid', '-')}\n"
                f"Porta: {info.get('port', '-')}"
            )
            self.details_text.config(text=details)

            # Atualizar logs
            logs = self.manager.get_logs(name, 50)
            self.log_area.config(state="normal")
            self.log_area.delete("1.0", "end")
            if logs:
                self.log_area.insert("1.0", logs)
            else:
                self.log_area.insert("1.0", f"Nenhum log para '{name}'.")
            self.log_area.see("end")
            self.log_area.config(state="disabled")

    def _get_selected_name(self) -> str:
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um servidor na lista.")
            return ""
        return self.tree.item(selection[0], "values")[0]

    def _start_selected(self):
        name = self._get_selected_name()
        if not name:
            return
        if self.manager.start_server(name):
            messagebox.showinfo("Sucesso", f"Servidor '{name}' iniciado!")
        else:
            messagebox.showerror("Erro", f"Falha ao iniciar '{name}'.")
        self._refresh_servers()

    def _stop_selected(self):
        name = self._get_selected_name()
        if not name:
            return
        if self.manager.stop_server(name):
            messagebox.showinfo("Sucesso", f"Servidor '{name}' parado!")
        else:
            messagebox.showerror("Erro", f"Falha ao parar '{name}'.")
        self._refresh_servers()

    def _restart_selected(self):
        name = self._get_selected_name()
        if not name:
            return
        self.manager.stop_server(name)
        if self.manager.start_server(name):
            messagebox.showinfo("Sucesso", f"Servidor '{name}' reiniciado!")
        else:
            messagebox.showerror("Erro", f"Falha ao reiniciar '{name}'.")
        self._refresh_servers()

    def _remove_selected(self):
        name = self._get_selected_name()
        if not name:
            return
        if messagebox.askyesno("Confirmar", f"Remover servidor '{name}'?"):
            self.manager.remove_server(name)
            self.details_text.config(text="Selecione um servidor na lista")
            self._refresh_servers()

    def _configure_client(self):
        """Dialogo de configuracao de cliente."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Configurar Cliente MCP")
        dialog.geometry("400x250")
        dialog.configure(bg=COLORS["bg_card"])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Selecione o Cliente",
            font=("Segoe UI", 14, "bold"),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
        ).pack(pady=(20, 10))

        selected_client = tk.StringVar(value=SUPPORTED_CLIENTS[0])

        for client in SUPPORTED_CLIENTS:
            tk.Radiobutton(
                dialog,
                text=client,
                variable=selected_client,
                value=client,
                font=("Segoe UI", 11),
                fg=COLORS["text_primary"],
                bg=COLORS["bg_card"],
                selectcolor=COLORS["bg_input"],
                activebackground=COLORS["bg_card"],
                activeforeground=COLORS["accent"],
            ).pack(anchor="w", padx=30)

        def apply():
            client = selected_client.get()
            if self.manager.configure_client(client):
                messagebox.showinfo("Sucesso", f"Servidores exportados para '{client}'!")
            else:
                messagebox.showerror("Erro", f"Falha ao configurar '{client}'.")
            dialog.destroy()

        tk.Button(
            dialog,
            text="Aplicar",
            font=("Segoe UI", 10),
            fg="white",
            bg=COLORS["accent"],
            bd=0,
            padx=20,
            pady=6,
            cursor="hand2",
            command=apply,
        ).pack(pady=20)

    def _show_add_dialog(self):
        """Dialogo para adicionar novo servidor."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Adicionar Servidor MCP")
        dialog.geometry("500x400")
        dialog.configure(bg=COLORS["bg_card"])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Novo Servidor MCP",
            font=("Segoe UI", 14, "bold"),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
        ).pack(pady=(20, 15))

        form = tk.Frame(dialog, bg=COLORS["bg_card"])
        form.pack(fill="x", padx=30)

        fields = {}
        for label_text, key, default in [
            ("Nome:", "name", ""),
            ("Comando:", "command", "notebooklm-mcp"),
            ("Transporte:", "transport", "stdio"),
            ("Porta (opcional):", "port", ""),
            ("Argumentos (sep. por espaco):", "args", ""),
        ]:
            tk.Label(
                form,
                text=label_text,
                font=("Segoe UI", 10),
                fg=COLORS["text_primary"],
                bg=COLORS["bg_card"],
            ).pack(anchor="w", pady=(8, 2))

            entry = tk.Entry(
                form,
                font=("Segoe UI", 10),
                bg=COLORS["bg_input"],
                fg=COLORS["text_primary"],
                insertbackground=COLORS["text_primary"],
                bd=1,
                relief="flat",
            )
            entry.insert(0, default)
            entry.pack(fill="x", ipady=4)
            fields[key] = entry

        def save():
            name = fields["name"].get().strip()
            if not name:
                messagebox.showwarning("Aviso", "Nome e obrigatorio.")
                return
            server_config = {
                "name": name,
                "command": fields["command"].get().strip(),
                "transport": fields["transport"].get().strip() or "stdio",
                "args": fields["args"].get().strip().split() if fields["args"].get().strip() else [],
                "env": {},
            }
            port = fields["port"].get().strip()
            if port:
                try:
                    server_config["port"] = int(port)
                except ValueError:
                    messagebox.showwarning("Aviso", "Porta deve ser um numero.")
                    return
            if self.manager.add_server(server_config):
                messagebox.showinfo("Sucesso", f"Servidor '{name}' adicionado!")
                dialog.destroy()
                self._refresh_servers()
            else:
                messagebox.showerror("Erro", "Falha ao adicionar servidor.")

        tk.Button(
            dialog,
            text="Salvar",
            font=("Segoe UI", 10),
            fg="white",
            bg=COLORS["accent"],
            bd=0,
            padx=20,
            pady=6,
            cursor="hand2",
            command=save,
        ).pack(pady=20)

    def run(self):
        """Inicia o loop principal da GUI."""
        self.root.mainloop()
        self.manager.stop_all()


def main():
    app = MCPServerManagerApp()
    app.run()


if __name__ == "__main__":
    main()
