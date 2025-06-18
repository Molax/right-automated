import logging

logger = logging.getLogger('PristonBot')

LARGATO_AVAILABLE = True
try:
    from app.largato_hunt import LargatoHunter
except:
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

class LargatoController:
    def __init__(self, largato_skill_bar, hp_bar, mp_bar, sp_bar, settings_ui, log_callback):
        self.largato_skill_bar = largato_skill_bar
        self.hp_bar = hp_bar
        self.mp_bar = mp_bar
        self.sp_bar = sp_bar
        self.settings_ui = settings_ui
        self.log_callback = log_callback
        
        self.largato_hunter = LargatoHunter(self.log_callback)
        
    def is_skill_bar_configured(self):
        if not self.largato_skill_bar:
            logger.debug("Largato skill bar is None")
            return False
        
        if hasattr(self.largato_skill_bar, 'is_setup'):
            result = self.largato_skill_bar.is_setup()
            logger.debug(f"Largato skill bar is_setup() returned: {result}")
            if result:
                return True
        
        if hasattr(self.largato_skill_bar, 'x1'):
            has_coords = (self.largato_skill_bar.x1 is not None and 
                        self.largato_skill_bar.y1 is not None and
                        self.largato_skill_bar.x2 is not None and
                        self.largato_skill_bar.y2 is not None)
            logger.debug(f"Largato skill bar coordinate check: {has_coords}")
            return has_coords
        
        logger.debug("Largato skill bar has no recognizable setup method or coordinates")
        return False
    
    def start_hunt(self):
        if not self.is_skill_bar_configured():
            self.log_callback("ERROR: Largato skill bar not configured!")
            return False
        
        self.largato_hunter.set_skill_bar_selector(self.largato_skill_bar)
        
        if LARGATO_AVAILABLE:
            self.largato_hunter.set_potion_system(
                self.hp_bar,
                self.mp_bar,
                self.sp_bar,
                self.settings_ui
            )
        
        success = self.largato_hunter.start_hunt()
        
        if success:
            self.log_callback("Largato Hunt started with potion support!")
        
        return success
    
    def stop_hunt(self):
        return self.largato_hunter.stop_hunt()
    
    def is_running(self):
        return self.largato_hunter.running
    
    def get_current_round(self):
        return self.largato_hunter.current_round
    
    def get_skill_percentage(self):
        return self.largato_hunter.get_skill_percentage()
    
    def get_hp_potions_used(self):
        return getattr(self.largato_hunter, 'hp_potions_used', 0)
    
    def get_mp_potions_used(self):
        return getattr(self.largato_hunter, 'mp_potions_used', 0)
    
    def get_sp_potions_used(self):
        return getattr(self.largato_hunter, 'sp_potions_used', 0)