"""
Logging utilities for the Intelligent Loan Processing System

This module provides centralized logging functionality for monitoring
and debugging the multi-agent loan processing system.
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any
import json


class LoanProcessingLogger:
    """
    Centralized logger for the loan processing system
    """
    
    def __init__(self, name: str = "loan_processing", log_level: str = "INFO"):
        """
        Initialize the logger
        
        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup console and file handlers"""
        # Create logs directory if it doesn't exist
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # Generate timestamped log filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"{logs_dir}/loan_processing_{timestamp}.log"
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        # Store log filename for reference
        self.log_filename = log_filename
        
        self.logger.info(f"Logger initialized. Log file: {log_filename}")
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log message with additional context"""
        if kwargs:
            context_str = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            full_message = f"{message} | {context_str}"
        else:
            full_message = message
        
        self.logger.log(level, full_message)
    
    def log_application_start(self, applicant_data: Dict[str, Any]):
        """Log the start of loan application processing"""
        self.info(
            "Starting loan application processing",
            applicant_name=applicant_data.get('name', 'Unknown'),
            loan_amount=applicant_data.get('loan_amount', 0),
            credit_score=applicant_data.get('credit_score', 'N/A')
        )
    
    def log_application_complete(self, result: Dict[str, Any]):
        """Log the completion of loan application processing"""
        self.info(
            "Loan application processing completed",
            applicant_name=result.get('applicant_name', 'Unknown'),
            status=result.get('status', 'Unknown'),
            risk_level=result.get('risk_level', 'Unknown')
        )
    
    def log_agent_execution(self, agent_name: str, task_description: str, duration: Optional[float] = None):
        """Log agent execution"""
        message = f"Agent executed: {agent_name}"
        if duration:
            message += f" (Duration: {duration:.2f}s)"
        
        self.debug(
            message,
            agent=agent_name,
            task=task_description[:100] + "..." if len(task_description) > 100 else task_description
        )
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]):
        """Log error with context information"""
        self.error(
            f"Error occurred: {str(error)}",
            error_type=type(error).__name__,
            **context
        )
    
    def log_business_rule_execution(self, rule_name: str, inputs: Dict[str, Any], outputs: Dict[str, Any]):
        """Log business rule execution"""
        self.debug(
            f"Business rule executed: {rule_name}",
            inputs=str(inputs)[:200] + "..." if len(str(inputs)) > 200 else str(inputs),
            outputs=str(outputs)[:200] + "..." if len(str(outputs)) > 200 else str(outputs)
        )
    
    def log_system_metrics(self, metrics: Dict[str, Any]):
        """Log system performance metrics"""
        self.info(
            "System metrics",
            **metrics
        )
    
    def get_log_filename(self) -> str:
        """Get the current log filename"""
        return getattr(self, 'log_filename', 'Unknown')


# Global logger instance
_global_logger = None


def get_logger(name: str = "loan_processing", log_level: str = "INFO") -> LoanProcessingLogger:
    """
    Get or create a logger instance
    
    Args:
        name: Logger name
        log_level: Logging level
        
    Returns:
        Logger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = LoanProcessingLogger(name, log_level)
    return _global_logger


def log_decorator(logger: Optional[LoanProcessingLogger] = None):
    """
    Decorator for automatic function logging
    
    Args:
        logger: Logger instance to use
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger()
            
            func_name = func.__name__
            module_name = func.__module__
            
            # Log function start
            logger.debug(f"Starting function execution", function=func_name, module=module_name)
            
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                
                # Log successful completion
                logger.debug(
                    f"Function completed successfully",
                    function=func_name,
                    duration=duration
                )
                
                return result
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                
                # Log error
                logger.log_error_with_context(
                    e,
                    {
                        'function': func_name,
                        'module': module_name,
                        'duration': duration
                    }
                )
                
                raise
        
        return wrapper
    return decorator


class PerformanceLogger:
    """
    Specialized logger for performance monitoring
    """
    
    def __init__(self, base_logger: LoanProcessingLogger):
        self.logger = base_logger
        self.start_time = None
        self.checkpoints = []
    
    def start(self, operation: str):
        """Start performance tracking"""
        self.start_time = datetime.now()
        self.checkpoints = []
        self.logger.debug(f"Performance tracking started", operation=operation)
    
    def checkpoint(self, name: str):
        """Add a performance checkpoint"""
        if self.start_time:
            current_time = datetime.now()
            elapsed = (current_time - self.start_time).total_seconds()
            self.checkpoints.append({
                'name': name,
                'elapsed': elapsed,
                'timestamp': current_time
            })
            self.logger.debug(f"Checkpoint reached", checkpoint=name, elapsed=elapsed)
    
    def end(self, operation: str):
        """End performance tracking and log results"""
        if self.start_time:
            total_time = (datetime.now() - self.start_time).total_seconds()
            
            metrics = {
                'operation': operation,
                'total_time': total_time,
                'checkpoints': len(self.checkpoints)
            }
            
            self.logger.log_system_metrics(metrics)
            
            # Log checkpoint details
            for checkpoint in self.checkpoints:
                self.logger.debug(
                    f"Checkpoint detail",
                    checkpoint=checkpoint['name'],
                    elapsed=checkpoint['elapsed']
                )
            
            self.start_time = None
            self.checkpoints = []
            
            return total_time
        
        return None


def setup_logging_from_config(config: Dict[str, Any]):
    """
    Setup logging from configuration dictionary
    
    Args:
        config: Configuration dictionary with logging settings
    """
    log_level = config.get('log_level', 'INFO')
    logger_name = config.get('logger_name', 'loan_processing')
    
    return get_logger(logger_name, log_level)


# Convenience functions for direct access
def debug(message: str, **kwargs):
    """Log debug message"""
    get_logger().debug(message, **kwargs)


def info(message: str, **kwargs):
    """Log info message"""
    get_logger().info(message, **kwargs)


def warning(message: str, **kwargs):
    """Log warning message"""
    get_logger().warning(message, **kwargs)


def error(message: str, **kwargs):
    """Log error message"""
    get_logger().error(message, **kwargs)


def critical(message: str, **kwargs):
    """Log critical message"""
    get_logger().critical(message, **kwargs)
