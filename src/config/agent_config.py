from typing import Dict, Any, Optional
import json
import logging

class AgentConfig:
    """Agent configuration with proper validation"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self._config: Dict[str, Any] = {}
        
        # Default configuration
        self.defaults = {
            'twitter_username': None,
            'loop_interval': 5,
            'max_retries': 3,
            'log_level': 'INFO',
        }
        
        if config_path:
            self.load_config(config_path)
        else:
            self._config = self.defaults.copy()
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from file with validation"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                
            # Merge with defaults
            self._config = {**self.defaults, **config_data}
            
            # Validate required fields
            self._validate_config()
            
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            self._config = self.defaults.copy()
    
    def _validate_config(self) -> None:
        """Validate configuration values"""
        if not self._config.get('twitter_username'):
            self.logger.warning("Twitter username not configured")
            
        if not isinstance(self._config.get('loop_interval'), (int, float)):
            self.logger.warning("Invalid loop_interval, using default")
            self._config['loop_interval'] = self.defaults['loop_interval']
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with default"""
        return self._config.get(key, default)
    
    @property
    def twitter_username(self) -> Optional[str]:
        """Get Twitter username with validation"""
        return self._config.get('twitter_username')
    
    @property
    def loop_interval(self) -> int:
        """Get loop interval with validation"""
        return int(self._config.get('loop_interval', self.defaults['loop_interval']))