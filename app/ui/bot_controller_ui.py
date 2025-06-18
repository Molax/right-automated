import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger('PristonBot')

class BotControllerUI:
    def __init__(self, parent, root, hp_bar, mp_bar, sp_bar, largato_skill_bar, settings_ui, log_callback):
        self.parent = parent
        self.root = root
        self.hp_bar = hp_bar
        self.mp_bar = mp_bar
        self.sp_bar = sp_bar
        self.largato_skill_bar = largato_skill_bar
        self.settings_ui = settings_ui
        self.log_callback = log_callback
        
        from app.bot.bot_core import BotCore
        from app.bot.largato_controller import LargatoController
        
        self.bot_core = BotCore(hp_bar, mp_bar, sp_bar, settings_ui, log_callback)
        self.largato_controller = LargatoController(largato_skill_bar, hp_bar, mp_bar, sp_bar, settings_ui, log_callback)
        
        self.running = False
        self.largato_running = False
        
        self.hp_potions_used = 0
        self.mp_potions_used = 0
        self.sp_potions_used = 0
        self.spells_cast = 0
        self.start_time = None
        
        self._create_ui()
        self._setup_keyboard_shortcuts()
    
    def _create_ui(self):
        status_frame = ttk.Frame(self.parent)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_var = tk.StringVar(value="Ready to configure")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=("Arial", 10, "bold"))
        status_label.pack(side=tk.LEFT, padx=5)
        
        self._create_values_display()
        self._create_buttons()
        self._create_shortcut_info()
    
    def _create_values_display(self):
        values_frame = ttk.Frame(self.parent)
        values_frame.pack(fill=tk.X, padx=5, pady=5)
        
        values_left = ttk.Frame(values_frame)
        values_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        values_right = ttk.Frame(values_frame)
        values_right.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        self._create_left_values(values_left)
        self._create_right_values(values_right)
    
    def _create_left_values(self, parent):
        hp_frame = ttk.Frame(parent)
        hp_frame.pack(fill=tk.X, pady=2)
        ttk.Label(hp_frame, text="Health:", foreground="#e74c3c", width=10).pack(side=tk.LEFT)
        self.hp_value_var = tk.StringVar(value="100.0%")
        ttk.Label(hp_frame, textvariable=self.hp_value_var).pack(side=tk.LEFT)
        
        mp_frame = ttk.Frame(parent)
        mp_frame.pack(fill=tk.X, pady=2)
        ttk.Label(mp_frame, text="Mana:", foreground="#3498db", width=10).pack(side=tk.LEFT)
        self.mp_value_var = tk.StringVar(value="100.0%")
        ttk.Label(mp_frame, textvariable=self.mp_value_var).pack(side=tk.LEFT)
        
        sp_frame = ttk.Frame(parent)
        sp_frame.pack(fill=tk.X, pady=2)
        ttk.Label(sp_frame, text="Stamina:", foreground="#2ecc71", width=10).pack(side=tk.LEFT)
        self.sp_value_var = tk.StringVar(value="100.0%")
        ttk.Label(sp_frame, textvariable=self.sp_value_var).pack(side=tk.LEFT)
        
        runtime_frame = ttk.Frame(parent)
        runtime_frame.pack(fill=tk.X, pady=2)
        ttk.Label(runtime_frame, text="Runtime:", width=10).pack(side=tk.LEFT)
        self.runtime_var = tk.StringVar(value="00:00:00")
        ttk.Label(runtime_frame, textvariable=self.runtime_var).pack(side=tk.LEFT)
        
        window_frame = ttk.Frame(parent)
        window_frame.pack(fill=tk.X, pady=2)
        ttk.Label(window_frame, text="Game Window:", width=10).pack(side=tk.LEFT)
        self.window_var = tk.StringVar(value="Not Detected")
        ttk.Label(window_frame, textvariable=self.window_var).pack(side=tk.LEFT)
        
        skill_status_frame = ttk.Frame(parent)
        skill_status_frame.pack(fill=tk.X, pady=2)
        ttk.Label(skill_status_frame, text="Skill Bar:", width=10).pack(side=tk.LEFT)
        self.skill_value_var = tk.StringVar(value="0.0%")
        ttk.Label(skill_status_frame, textvariable=self.skill_value_var).pack(side=tk.LEFT)
    
    def _create_right_values(self, parent):
        hp_pot_frame = ttk.Frame(parent)
        hp_pot_frame.pack(fill=tk.X, pady=2)
        ttk.Label(hp_pot_frame, text="HP Potions:", width=12).pack(side=tk.LEFT)
        self.hp_potions_var = tk.StringVar(value="0")
        ttk.Label(hp_pot_frame, textvariable=self.hp_potions_var).pack(side=tk.LEFT)
        
        mp_pot_frame = ttk.Frame(parent)
        mp_pot_frame.pack(fill=tk.X, pady=2)
        ttk.Label(mp_pot_frame, text="MP Potions:", width=12).pack(side=tk.LEFT)
        self.mp_potions_var = tk.StringVar(value="0")
        ttk.Label(mp_pot_frame, textvariable=self.mp_potions_var).pack(side=tk.LEFT)
        
        sp_pot_frame = ttk.Frame(parent)
        sp_pot_frame.pack(fill=tk.X, pady=2)
        ttk.Label(sp_pot_frame, text="SP Potions:", width=12).pack(side=tk.LEFT)
        self.sp_potions_var = tk.StringVar(value="0")
        ttk.Label(sp_pot_frame, textvariable=self.sp_potions_var).pack(side=tk.LEFT)
        
        spell_frame = ttk.Frame(parent)
        spell_frame.pack(fill=tk.X, pady=2)
        ttk.Label(spell_frame, text="Spells Cast:", width=12).pack(side=tk.LEFT)
        self.spells_var = tk.StringVar(value="0")
        ttk.Label(spell_frame, textvariable=self.spells_var).pack(side=tk.LEFT)
        
        target_frame = ttk.Frame(parent)
        target_frame.pack(fill=tk.X, pady=2)
        ttk.Label(target_frame, text="Target Offset:", width=12).pack(side=tk.LEFT)
        self.target_var = tk.StringVar(value="(0, 0)")
        ttk.Label(target_frame, textvariable=self.target_var).pack(side=tk.LEFT)
        
        largato_status_frame = ttk.Frame(parent)
        largato_status_frame.pack(fill=tk.X, pady=2)
        ttk.Label(largato_status_frame, text="Largato Round:", width=12).pack(side=tk.LEFT)
        self.largato_round_var = tk.StringVar(value="0/4")
        ttk.Label(largato_status_frame, textvariable=self.largato_round_var).pack(side=tk.LEFT)
    
    def _create_buttons(self):
        from app.bot.largato_controller import LARGATO_AVAILABLE
        
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = tk.Button(
            button_frame,
            text="START BOT\n(Ctrl+Shift+A)",
            command=self.start_bot,
            bg="#4CAF50",
            fg="black",
            font=("Arial", 10, "bold"),
            height=2,
            state=tk.DISABLED
        )
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        largato_state = tk.NORMAL if LARGATO_AVAILABLE else tk.DISABLED
        largato_bg = "#FF9800" if LARGATO_AVAILABLE else "#a0a0a0"
        largato_text = "LARGATO HUNT\n(Ctrl+Shift+L)" if LARGATO_AVAILABLE else "LARGATO HUNT\n(Not Available)"
        
        self.largato_button = tk.Button(
            button_frame,
            text=largato_text,
            command=self.start_largato_hunt,
            bg=largato_bg,
            fg="black",
            font=("Arial", 10, "bold"),
            height=2,
            state=largato_state
        )
        self.largato_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.stop_button = tk.Button(
            button_frame,
            text="STOP BOT\n(Ctrl+Shift+B)",
            command=self.stop_bot,
            bg="#F44336",
            fg="black",
            font=("Arial", 10, "bold"),
            height=2,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    
    def _create_shortcut_info(self):
        from app.bot.largato_controller import LARGATO_AVAILABLE
        
        shortcut_frame = ttk.Frame(self.parent)
        shortcut_frame.pack(fill=tk.X, pady=5)
        
        shortcut_text = "Shortcuts: Ctrl+Shift+A (Start), Ctrl+Shift+L (Largato Hunt), Ctrl+Shift+B (Stop)"
        if not LARGATO_AVAILABLE:
            shortcut_text += " - Largato Hunt requires proper module installation"
        
        shortcut_label = ttk.Label(
            shortcut_frame,
            text=shortcut_text,
            font=("Arial", 8),
            foreground="#555555"
        )
        shortcut_label.pack(anchor=tk.CENTER)
    
    def _setup_keyboard_shortcuts(self):
        self.root.bind("<Control-Shift-a>", lambda event: self._handle_start_shortcut())
        self.root.bind("<Control-Shift-A>", lambda event: self._handle_start_shortcut())
        self.root.bind("<Control-Shift-b>", lambda event: self._handle_stop_shortcut())
        self.root.bind("<Control-Shift-B>", lambda event: self._handle_stop_shortcut())
        self.root.bind("<Control-Shift-l>", lambda event: self._handle_largato_shortcut())
        self.root.bind("<Control-Shift-L>", lambda event: self._handle_largato_shortcut())
        
        logger.info("Keyboard shortcuts registered")
    
    def _handle_start_shortcut(self):
        if not self.running and not self.largato_running and self.start_button.cget('state') != 'disabled':
            logger.info("Start bot shortcut (Ctrl+Shift+A) triggered")
            self.start_bot()
    
    def _handle_stop_shortcut(self):
        if self.running or self.largato_running:
            logger.info("Stop bot shortcut (Ctrl+Shift+B) triggered")
            self.stop_bot()
    
    def _handle_largato_shortcut(self):
        from app.bot.largato_controller import LARGATO_AVAILABLE
        
        if not LARGATO_AVAILABLE:
            self.log_callback("Largato Hunt not available - module not properly installed")
            return
        
        if not self.running and not self.largato_running:
            logger.info("Largato hunt shortcut (Ctrl+Shift+L) triggered")
            self.start_largato_hunt()
        elif self.largato_running:
            logger.info("Stop Largato hunt shortcut (Ctrl+Shift+L) triggered")
            self.stop_largato_hunt()
    
    def start_bot(self):
        if self.largato_running:
            from tkinter import messagebox
            messagebox.showwarning(
                "Largato Hunt Running",
                "Please stop Largato Hunt before starting the regular bot.",
                parent=self.root
            )
            return
        
        if self.running:
            logger.info("Start button clicked, but bot is already running")
            return
        
        self.running = True
        self.bot_core.start()
        self._update_ui_for_running_state()
    
    def start_largato_hunt(self):
        from app.bot.largato_controller import LARGATO_AVAILABLE
        from tkinter import messagebox
        
        if not LARGATO_AVAILABLE:
            messagebox.showerror(
                "Largato Hunt Not Available",
                "Largato Hunt module is not properly installed.",
                parent=self.root
            )
            return
        
        if self.running:
            messagebox.showwarning(
                "Bot Already Running",
                "Please stop the regular bot before starting Largato Hunt.",
                parent=self.root
            )
            return
        
        if self.largato_running:
            return
        
        if not self.largato_controller.is_skill_bar_configured():
            messagebox.showerror(
                "Largato Skill Bar Not Configured",
                "Please configure the Largato skill bar first.",
                parent=self.root
            )
            return
        
        self.largato_running = True
        success = self.largato_controller.start_hunt()
        
        if success:
            self._update_ui_for_largato_state()
            self._start_largato_progress_monitoring()
        else:
            self.largato_running = False
    
    def stop_bot(self):
        stopped_something = False
        
        if self.running:
            self.bot_core.stop()
            self.running = False
            stopped_something = True
        
        if self.largato_running:
            self.largato_controller.stop_hunt()
            self.largato_running = False
            stopped_something = True
        
        if stopped_something:
            self._update_ui_for_stopped_state()
    
    def stop_largato_hunt(self):
        if not self.largato_running:
            return
        
        self.largato_controller.stop_hunt()
        self.largato_running = False
        self._update_ui_for_stopped_state()
    
    def _update_ui_for_running_state(self):
        self.start_button.config(state=tk.DISABLED, bg="#a0a0a0")
        self.largato_button.config(state=tk.DISABLED, bg="#a0a0a0")
        self.stop_button.config(state=tk.NORMAL, bg="#F44336")
        self.status_var.set("Bot is running")
    
    def _update_ui_for_largato_state(self):
        from app.bot.largato_controller import LARGATO_AVAILABLE
        
        self.start_button.config(state=tk.DISABLED, bg="#a0a0a0")
        self.largato_button.config(text="STOP LARGATO\n(Ctrl+Shift+L)", bg="#F44336")
        self.stop_button.config(state=tk.NORMAL, bg="#F44336")
        self.status_var.set("Largato Hunt is running with potion support")
    
    def _update_ui_for_stopped_state(self):
        from app.bot.largato_controller import LARGATO_AVAILABLE
        
        self.stop_button.config(state=tk.DISABLED, bg="#a0a0a0")
        
        if LARGATO_AVAILABLE:
            self.largato_button.config(text="LARGATO HUNT\n(Ctrl+Shift+L)", bg="#FF9800", state=tk.NORMAL)
        else:
            self.largato_button.config(text="LARGATO HUNT\n(Not Available)", bg="#a0a0a0", state=tk.DISABLED)
        
        if self._can_enable_start_button():
            self.start_button.config(state=tk.NORMAL, bg="#4CAF50")
        
        self.status_var.set("All bots stopped")
    
    def _start_largato_progress_monitoring(self):
        self._update_largato_progress()
    
    def _update_largato_progress(self):
        if self.largato_running and self.largato_controller:
            round_count = self.largato_controller.get_current_round()
            self.largato_round_var.set(f"{round_count}/4")
            
            skill_percentage = self.largato_controller.get_skill_percentage()
            self.skill_value_var.set(f"{skill_percentage:.1f}%")
            
            self.hp_potions_var.set(str(self.largato_controller.get_hp_potions_used()))
            self.mp_potions_var.set(str(self.largato_controller.get_mp_potions_used()))
            self.sp_potions_var.set(str(self.largato_controller.get_sp_potions_used()))
            
            if not self.largato_controller.is_running():
                self.largato_running = False
                self._update_ui_for_stopped_state()
                
                if round_count >= 4:
                    self.status_var.set("Largato Hunt completed!")
                else:
                    self.status_var.set("Largato Hunt stopped")
                return
            
            self.root.after(1000, self._update_largato_progress)
    
    def _can_enable_start_button(self):
        configured = 0
        if self.hp_bar and hasattr(self.hp_bar, 'is_setup') and self.hp_bar.is_setup():
            configured += 1
        if self.mp_bar and hasattr(self.mp_bar, 'is_setup') and self.mp_bar.is_setup():
            configured += 1
        if self.sp_bar and hasattr(self.sp_bar, 'is_setup') and self.sp_bar.is_setup():
            configured += 1
        return configured == 3
    
    def enable_start_button(self):
        if not self.largato_running:
            self.start_button.config(state=tk.NORMAL, bg="#4CAF50")
            self.status_var.set("Ready to start")
    
    def disable_start_button(self):
        self.start_button.config(state=tk.DISABLED, bg="#a0a0a0")
    
    def set_status(self, message):
        self.status_var.set(message)