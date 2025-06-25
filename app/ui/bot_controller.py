import tkinter as tk
from tkinter import ttk, messagebox
import logging
import time
from tkinter import Toplevel

logger = logging.getLogger('PristonBot')

LARGATO_AVAILABLE = True
try:
    from app.largato_hunt import LargatoHunter
except ImportError:
    class LargatoHunter:
        def __init__(self, log_callback):
            self.log_callback = log_callback
            self.running = False
            self.wood_stacks_destroyed = 0
            self.current_round = 1
            self.hp_potions_used = 0
            self.mp_potions_used = 0
            self.sp_potions_used = 0
        
        def start_hunt(self):
            self.log_callback("ERROR: Largato Hunt module not available!")
            return False
        
        def stop_hunt(self):
            return True
            
        def set_skill_bar_selector(self, selector):
            pass
        
        def set_potion_system(self, hp_bar, mp_bar, sp_bar, settings_provider):
            pass
        
        def get_skill_percentage(self):
            return 0
    
    LARGATO_AVAILABLE = False

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify='left',
                        background="#ffffe0", relief='solid', borderwidth=1,
                        font=("Arial", 9))
        label.pack(ipadx=1)
    
    def hide_tooltip(self, event=None):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()

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
        
        try:
            from app.bot.bot_core import BotCore
            self.bot_core = BotCore(hp_bar, mp_bar, sp_bar, settings_ui, log_callback)
        except ImportError:
            self.bot_core = None
            logger.warning("BotCore not available")
        
        self.largato_hunter = LargatoHunter(self.log_callback)
        
        self.running = False
        self.largato_running = False
        
        self.hp_potions_used = 0
        self.mp_potions_used = 0
        self.sp_potions_used = 0
        self.spells_cast = 0
        self.start_time = None
        
        self.target_x_offset = 0
        self.target_y_offset = 0
        self.spells_cast_since_target_change = 0
        
        self.game_window = None
        self.game_window_rect = None
        self.game_hwnd = None
        
        self._create_ui()
        self._setup_keyboard_shortcuts()
    
    def _create_ui(self):
        status_frame = ttk.Frame(self.parent)
        status_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.status_var = tk.StringVar(value="Ready to configure")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=("Arial", 10, "bold"))
        status_label.pack(side=tk.LEFT)
        
        self._create_values_display()
        self._create_buttons()
        self._create_stats_display()
    
    def _create_values_display(self):
        values_frame = ttk.Frame(self.parent)
        values_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Left side - Bar percentages (more compact)
        left_frame = ttk.Frame(values_frame)
        left_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        hp_frame = ttk.Frame(left_frame)
        hp_frame.pack(fill=tk.X, pady=1)
        ttk.Label(hp_frame, text="Health:", foreground="#e74c3c", width=7).pack(side=tk.LEFT)
        self.hp_value_var = tk.StringVar(value="100.0%")
        ttk.Label(hp_frame, textvariable=self.hp_value_var, width=8).pack(side=tk.LEFT)
        
        mp_frame = ttk.Frame(left_frame)
        mp_frame.pack(fill=tk.X, pady=1)
        ttk.Label(mp_frame, text="Mana:", foreground="#3498db", width=7).pack(side=tk.LEFT)
        self.mp_value_var = tk.StringVar(value="100.0%")
        ttk.Label(mp_frame, textvariable=self.mp_value_var, width=8).pack(side=tk.LEFT)
        
        sp_frame = ttk.Frame(left_frame)
        sp_frame.pack(fill=tk.X, pady=1)
        ttk.Label(sp_frame, text="Stamina:", foreground="#2ecc71", width=7).pack(side=tk.LEFT)
        self.sp_value_var = tk.StringVar(value="100.0%")
        ttk.Label(sp_frame, textvariable=self.sp_value_var, width=8).pack(side=tk.LEFT)
        
        # Right side - Potion counters (more compact)
        right_frame = ttk.Frame(values_frame)
        right_frame.pack(side=tk.RIGHT)
        
        hp_pot_frame = ttk.Frame(right_frame)
        hp_pot_frame.pack(fill=tk.X, pady=1)
        ttk.Label(hp_pot_frame, text="HP Pots:", width=8).pack(side=tk.LEFT)
        self.hp_potions_var = tk.StringVar(value="0")
        ttk.Label(hp_pot_frame, textvariable=self.hp_potions_var, width=6).pack(side=tk.LEFT)
        
        mp_pot_frame = ttk.Frame(right_frame)
        mp_pot_frame.pack(fill=tk.X, pady=1)
        ttk.Label(mp_pot_frame, text="MP Pots:", width=8).pack(side=tk.LEFT)
        self.mp_potions_var = tk.StringVar(value="0")
        ttk.Label(mp_pot_frame, textvariable=self.mp_potions_var, width=6).pack(side=tk.LEFT)
        
        sp_pot_frame = ttk.Frame(right_frame)
        sp_pot_frame.pack(fill=tk.X, pady=1)
        ttk.Label(sp_pot_frame, text="SP Pots:", width=8).pack(side=tk.LEFT)
        self.sp_potions_var = tk.StringVar(value="0")
        ttk.Label(sp_pot_frame, textvariable=self.sp_potions_var, width=6).pack(side=tk.LEFT)
    
    def _create_buttons(self):
        buttons_frame = ttk.Frame(self.parent)
        buttons_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Main buttons row
        main_buttons_frame = ttk.Frame(buttons_frame)
        main_buttons_frame.pack(fill=tk.X, pady=(0, 2))
        
        left_buttons = ttk.Frame(main_buttons_frame)
        left_buttons.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.start_button = ttk.Button(left_buttons, text="Start Bot", command=self.start_bot, state="disabled")
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        ToolTip(self.start_button, "Start the potion bot (Ctrl+Shift+A)")
        
        self.stop_button = ttk.Button(left_buttons, text="Stop Bot", command=self.stop_bot, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        ToolTip(self.stop_button, "Stop the running bot (Ctrl+Shift+B)")
        
        if LARGATO_AVAILABLE:
            self.largato_button = ttk.Button(left_buttons, text="Largato Hunt", command=self.start_largato_hunt, state="disabled")
            self.largato_button.pack(side=tk.LEFT, padx=(0, 5))
            ToolTip(self.largato_button, "Start Largato Hunt mode (Ctrl+Shift+L)")
        
        # Shortcuts info
        shortcut_label = ttk.Label(
            buttons_frame, 
            text="Shortcuts: Ctrl+Shift+A (Start) | Ctrl+Shift+B (Stop)" + (" | Ctrl+Shift+L (Largato)" if LARGATO_AVAILABLE else ""),
            font=("Arial", 7),
            foreground="#555555"
        )
        shortcut_label.pack(pady=(2, 0))
    
    def _create_stats_display(self):
        stats_frame = ttk.Frame(self.parent)
        stats_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Left side - Spells and Uptime (compact)
        left_stats = ttk.Frame(stats_frame)
        left_stats.pack(side=tk.LEFT, padx=(0, 10))
        
        spells_frame = ttk.Frame(left_stats)
        spells_frame.pack(fill=tk.X, pady=1)
        ttk.Label(spells_frame, text="Spells:", width=7).pack(side=tk.LEFT)
        self.spells_var = tk.StringVar(value="0")
        ttk.Label(spells_frame, textvariable=self.spells_var, width=8).pack(side=tk.LEFT)
        
        uptime_frame = ttk.Frame(left_stats)
        uptime_frame.pack(fill=tk.X, pady=1)
        ttk.Label(uptime_frame, text="Uptime:", width=7).pack(side=tk.LEFT)
        self.uptime_var = tk.StringVar(value="00:00:00")
        ttk.Label(uptime_frame, textvariable=self.uptime_var, width=8).pack(side=tk.LEFT)
        
        # Right side - Largato stats (compact)
        if LARGATO_AVAILABLE:
            right_stats = ttk.Frame(stats_frame)
            right_stats.pack(side=tk.RIGHT)
            
            largato_frame = ttk.Frame(right_stats)
            largato_frame.pack(fill=tk.X, pady=1)
            ttk.Label(largato_frame, text="Wood:", width=6).pack(side=tk.LEFT)
            self.wood_stacks_var = tk.StringVar(value="0")
            ttk.Label(largato_frame, textvariable=self.wood_stacks_var, width=6).pack(side=tk.LEFT)
            
            round_frame = ttk.Frame(right_stats)
            round_frame.pack(fill=tk.X, pady=1)
            ttk.Label(round_frame, text="Round:", width=6).pack(side=tk.LEFT)
            self.round_var = tk.StringVar(value="1")
            ttk.Label(round_frame, textvariable=self.round_var, width=6).pack(side=tk.LEFT)
        
        # Action buttons above uptime
        actions_frame = ttk.Frame(self.parent)
        actions_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.reset_button = ttk.Button(actions_frame, text="Reset Stats", command=self.reset_stats)
        self.reset_button.pack(side=tk.LEFT, padx=(0, 5))
        ToolTip(self.reset_button, "Reset potion usage statistics")
        
        self.save_button = ttk.Button(actions_frame, text="Save Settings", command=self._save_settings)
        self.save_button.pack(side=tk.LEFT)
        ToolTip(self.save_button, "Save current settings to configuration file")
    
    def _setup_keyboard_shortcuts(self):
        self.root.bind("<Control-Shift-a>", lambda event: self._handle_start_shortcut())
        self.root.bind("<Control-Shift-A>", lambda event: self._handle_start_shortcut())
        self.root.bind("<Control-Shift-b>", lambda event: self._handle_stop_shortcut())
        self.root.bind("<Control-Shift-B>", lambda event: self._handle_stop_shortcut())
        
        if LARGATO_AVAILABLE:
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
        if self.running or self.largato_running:
            logger.info("Bot start button clicked, but bot is already running")
            return
        
        if not self._is_configuration_valid():
            messagebox.showerror(
                "Configuration Error",
                "Please configure all required bars before starting the bot.",
                parent=self.root
            )
            return
        
        try:
            self.start_time = time.time()
            self.running = True
            
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            if LARGATO_AVAILABLE:
                self.largato_button.configure(state="disabled")
            
            self.bot_core.start()
            self.set_status("Bot running...")
            self.log_callback("Potion bot started")
            
            self._update_display()
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            self.running = False
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            if LARGATO_AVAILABLE:
                self.largato_button.configure(state="normal" if self._is_largato_available() else "disabled")
            messagebox.showerror("Error", f"Failed to start bot: {e}", parent=self.root)
    
    def stop_bot(self):
        if not self.running and not self.largato_running:
            logger.info("Stop button clicked, but no bot is running")
            return
        
        try:
            if self.running:
                self.bot_core.stop()
                self.running = False
                self.log_callback("Potion bot stopped")
            
            if self.largato_running:
                self.largato_hunter.stop_hunt()
                self.largato_running = False
                self.log_callback("Largato hunt stopped")
            
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            if LARGATO_AVAILABLE:
                self.largato_button.configure(state="normal" if self._is_largato_available() else "disabled")
            
            self.set_status("Ready to start")
            
        except Exception as e:
            logger.error(f"Failed to stop bot: {e}")
            messagebox.showerror("Error", f"Failed to stop bot: {e}", parent=self.root)
    
    def start_largato_hunt(self):
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
            logger.info("Largato hunt button clicked, but hunt is already running")
            return
        
        if not self._is_skill_bar_configured():
            messagebox.showerror(
                "Largato Skill Bar Not Configured",
                "Please configure the Largato skill bar first.",
                parent=self.root
            )
            return
        
        try:
            self.start_time = time.time()
            self.largato_running = True
            
            self.start_button.configure(state="disabled")
            self.largato_button.configure(text="Stop Hunt", state="normal")
            self.stop_button.configure(state="normal")
            
            self.largato_hunter.set_skill_bar_selector(self.largato_skill_bar)
            self.largato_hunter.set_potion_system(self.hp_bar, self.mp_bar, self.sp_bar, self.settings_ui)
            
            if self.largato_hunter.start_hunt():
                self.set_status("Largato Hunt running...")
                self.log_callback("Largato Hunt started")
                self._update_display()
            else:
                self.largato_running = False
                self.start_button.configure(state="normal")
                self.largato_button.configure(text="Largato Hunt", state="normal")
                self.stop_button.configure(state="disabled")
                
        except Exception as e:
            logger.error(f"Failed to start Largato hunt: {e}")
            self.largato_running = False
            self.start_button.configure(state="normal")
            self.largato_button.configure(text="Largato Hunt", state="normal")
            self.stop_button.configure(state="disabled")
            messagebox.showerror("Error", f"Failed to start Largato hunt: {e}", parent=self.root)
    
    def stop_largato_hunt(self):
        self.largato_button.configure(text="Largato Hunt")
        self.stop_bot()
    
    def reset_stats(self):
        self.hp_potions_used = 0
        self.mp_potions_used = 0
        self.sp_potions_used = 0
        self.spells_cast = 0
        self.start_time = None
        
        self.hp_potions_var.set("0")
        self.mp_potions_var.set("0")
        self.sp_potions_var.set("0")
        self.spells_var.set("0")
        self.uptime_var.set("00:00:00")
        
        if LARGATO_AVAILABLE:
            self.largato_hunter.wood_stacks_destroyed = 0
            self.largato_hunter.current_round = 1
            self.wood_stacks_var.set("0")
            self.round_var.set("1")
        
        self.log_callback("Statistics reset")
    
    def _save_settings(self):
        try:
            if hasattr(self.settings_ui, 'save_callback'):
                result = self.settings_ui.save_callback()
                if result:
                    self.log_callback("Settings saved successfully")
                else:
                    self.log_callback("Failed to save settings")
            else:
                self.log_callback("Save functionality not available")
        except Exception as e:
            self.log_callback(f"Error saving settings: {e}")
            logger.error(f"Error saving settings: {e}")
    
    def _update_display(self):
        if not self.running and not self.largato_running:
            return
        
        try:
            if self.running and self.bot_core:
                hp_percent = self.hp_bar.get_percentage()
                mp_percent = self.mp_bar.get_percentage()
                sp_percent = self.sp_bar.get_percentage()
                
                self.hp_value_var.set(f"{hp_percent:.1f}%")
                self.mp_value_var.set(f"{mp_percent:.1f}%")
                self.sp_value_var.set(f"{sp_percent:.1f}%")
                
                self.hp_potions_var.set(str(self.bot_core.hp_potions_used))
                self.mp_potions_var.set(str(self.bot_core.mp_potions_used))
                self.sp_potions_var.set(str(self.bot_core.sp_potions_used))
                self.spells_var.set(str(self.bot_core.spells_cast))
            
            if self.largato_running and LARGATO_AVAILABLE:
                self.wood_stacks_var.set(str(self.largato_hunter.wood_stacks_destroyed))
                self.round_var.set(str(self.largato_hunter.current_round))
                
                self.hp_potions_var.set(str(self.largato_hunter.hp_potions_used))
                self.mp_potions_var.set(str(self.largato_hunter.mp_potions_used))
                self.sp_potions_var.set(str(self.largato_hunter.sp_potions_used))
            
            if self.start_time:
                uptime = time.time() - self.start_time
                hours = int(uptime // 3600)
                minutes = int((uptime % 3600) // 60)
                seconds = int(uptime % 60)
                self.uptime_var.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
        except Exception as e:
            logger.error(f"Error updating display: {e}")
        
        self.root.after(1000, self._update_display)
    
    def _is_configuration_valid(self):
        return (hasattr(self.hp_bar, 'is_setup') and self.hp_bar.is_setup() and
                hasattr(self.mp_bar, 'is_setup') and self.mp_bar.is_setup() and
                hasattr(self.sp_bar, 'is_setup') and self.sp_bar.is_setup())
    
    def _is_skill_bar_configured(self):
        return (hasattr(self.largato_skill_bar, 'is_setup') and 
                self.largato_skill_bar.is_setup())
    
    def _is_largato_available(self):
        return LARGATO_AVAILABLE and self._is_skill_bar_configured()
    
    def set_status(self, status):
        self.status_var.set(status)
    
    def enable_start_button(self):
        if not self.running and not self.largato_running:
            self.start_button.configure(state="normal")
            if LARGATO_AVAILABLE and self._is_skill_bar_configured():
                self.largato_button.configure(state="normal")
    
    def disable_start_button(self):
        self.start_button.configure(state="disabled")
        if LARGATO_AVAILABLE:
            self.largato_button.configure(state="disabled")
    
    def cleanup(self):
        try:
            if self.running:
                self.bot_core.stop()
            if self.largato_running:
                self.largato_hunter.stop_hunt()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")