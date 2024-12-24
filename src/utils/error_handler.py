import logging
import traceback
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio

from .errors import BaseError

logger = logging.getLogger(__name__)

class ErrorHandler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.error_counts = {}
        self.last_errors = {}
        self.max_retries = config.get('max_retries', 3)
        self.cooldown_period = config.get('error_cooldown', 5)
        
    async def handle_error(self, 
                          error: Exception,
                          context: Optional[Dict] = None,
                          retry_function: Optional[callable] = None) -> None:
        """Handle any error with optional retry logic"""
        try:
            error_type = type(error).__name__
            
            # Log error with context
            self._log_error(error, context)
            
            # Update error tracking
            await self._track_error(error_type)
            
            # Handle retries if function provided
            if retry_function and await self._should_retry(error_type):
                await self._retry_operation(retry_function)
            
            # Cleanup if needed
            await self._error_cleanup(error)
            
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
            # Prevent infinite recursion
            if not isinstance(e, type(error)):
                await self.handle_error(e)

    def _log_error(self, error: Exception, context: Optional[Dict] = None) -> None:
        """Log error with full context"""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'traceback': traceback.format_exc(),
            'context': context
        }
        
        logger.error(f"Error occurred: {error_info}")

    async def _track_error(self, error_type: str) -> None:
        """Track error frequency"""
        current_time = datetime.now()
        
        if error_type in self.error_counts:
            self.error_counts[error_type] += 1
        else:
            self.error_counts[error_type] = 1
            
        self.last_errors[error_type] = current_time

    async def _should_retry(self, error_type: str) -> bool:
        """Determine if operation should be retried"""
        if error_type not in self.error_counts:
            return True
            
        if self.error_counts[error_type] >= self.max_retries:
            logger.warning(f"Max retries ({self.max_retries}) reached for {error_type}")
            return False
            
        return True

    async def _retry_operation(self, retry_function: callable) -> None:
        """Retry the failed operation"""
        try:
            await asyncio.sleep(self.cooldown_period)
            await retry_function()
        except Exception as e:
            logger.error(f"Retry failed: {e}")

    async def _error_cleanup(self, error: Exception) -> None:
        """Perform any necessary cleanup after error"""
        try:
            # Add cleanup logic specific to error type
            pass
        except Exception as e:
            logger.error(f"Error cleanup failed: {e}")
