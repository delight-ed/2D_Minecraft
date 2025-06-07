"""
Error handling and logging utilities
"""
import traceback
import logging
import os
from datetime import datetime

class GameErrorHandler:
    """Centralized error handling for the game"""
    
    def __init__(self, log_file="game_errors.log"):
        self.log_file = log_file
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"logs/{self.log_file}"),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def log_error(self, error, context="Unknown"):
        """Log an error with context"""
        error_msg = f"Error in {context}: {str(error)}"
        self.logger.error(error_msg)
        self.logger.error(traceback.format_exc())
    
    def log_warning(self, message, context="Unknown"):
        """Log a warning"""
        warning_msg = f"Warning in {context}: {message}"
        self.logger.warning(warning_msg)
    
    def log_info(self, message, context="Game"):
        """Log an info message"""
        info_msg = f"Info in {context}: {message}"
        self.logger.info(info_msg)
    
    def handle_critical_error(self, error, context="Unknown"):
        """Handle critical errors that might crash the game"""
        self.log_error(error, context)
        
        # Try to save game state before crashing
        try:
            self.emergency_save()
        except Exception as save_error:
            self.log_error(save_error, "Emergency Save")
        
        # Show error dialog to user
        self.show_error_dialog(error, context)
    
    def emergency_save(self):
        """Emergency save function (to be implemented by game)"""
        # This should be overridden by the game to save current state
        pass
    
    def show_error_dialog(self, error, context):
        """Show error dialog to user"""
        print(f"\n{'='*50}")
        print(f"CRITICAL ERROR in {context}")
        print(f"{'='*50}")
        print(f"Error: {str(error)}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Check logs/game_errors.log for more details")
        print(f"{'='*50}\n")

def safe_execute(func, error_handler=None, context="Unknown", default_return=None):
    """Safely execute a function with error handling"""
    try:
        return func()
    except Exception as e:
        if error_handler:
            error_handler.log_error(e, context)
        else:
            print(f"Error in {context}: {e}")
        return default_return

def validate_file_path(file_path):
    """Validate that a file path is safe and exists"""
    if not file_path:
        raise ValueError("File path cannot be empty")
    
    # Normalize the path
    normalized_path = os.path.normpath(file_path)
    
    # Check for directory traversal attempts
    if ".." in normalized_path:
        raise ValueError("Directory traversal not allowed")
    
    return normalized_path

def safe_file_operation(operation, file_path, error_handler=None, context="File Operation"):
    """Safely perform file operations"""
    try:
        validated_path = validate_file_path(file_path)
        return operation(validated_path)
    except Exception as e:
        if error_handler:
            error_handler.log_error(e, f"{context} - {file_path}")
        else:
            print(f"File operation error in {context}: {e}")
        return None

class PerformanceMonitor:
    """Monitor game performance and detect issues"""
    
    def __init__(self, error_handler=None):
        self.error_handler = error_handler
        self.frame_times = []
        self.max_samples = 100
        self.warning_threshold = 50  # ms
        self.critical_threshold = 100  # ms
    
    def record_frame_time(self, frame_time):
        """Record a frame time"""
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.max_samples:
            self.frame_times.pop(0)
        
        # Check for performance issues
        if frame_time > self.critical_threshold:
            if self.error_handler:
                self.error_handler.log_warning(
                    f"Critical frame time: {frame_time}ms", 
                    "Performance Monitor"
                )
        elif frame_time > self.warning_threshold:
            if self.error_handler:
                self.error_handler.log_warning(
                    f"High frame time: {frame_time}ms", 
                    "Performance Monitor"
                )
    
    def get_average_frame_time(self):
        """Get average frame time"""
        if not self.frame_times:
            return 0
        return sum(self.frame_times) / len(self.frame_times)
    
    def get_fps(self):
        """Get current FPS"""
        avg_frame_time = self.get_average_frame_time()
        return 1000.0 / avg_frame_time if avg_frame_time > 0 else 0
    
    def is_performance_critical(self):
        """Check if performance is critically low"""
        return self.get_fps() < 30  # Below 30 FPS is considered critical