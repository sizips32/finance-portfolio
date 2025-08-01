"""
Error handling utilities for the Finance Portfolio application.
"""
import streamlit as st
import logging
from typing import Dict, Any, Optional
from .exceptions import *


class ErrorHandler:
    """Centralized error handling for the application."""
    
    @staticmethod
    def show_error(error_type: str, details: str = None, suggestions: str = None):
        """Display user-friendly error messages."""
        
        error_messages = {
            'db_error': {
                'title': '💾 데이터베이스 오류',
                'message': '데이터베이스 연결에 문제가 있습니다. 잠시 후 다시 시도해주세요.',
                'suggestion': '문제가 지속되면 앱을 다시 시작해보세요.'
            },
            'api_error': {
                'title': '🌐 외부 데이터 오류',
                'message': '외부 데이터 조회에 실패했습니다.',
                'suggestion': '네트워크 연결을 확인하고 다시 시도해주세요.'
            },
            'validation_error': {
                'title': '✏️ 입력 오류',
                'message': '입력된 정보에 문제가 있습니다.',
                'suggestion': '입력값을 확인하고 다시 시도해주세요.'
            },
            'file_error': {
                'title': '📁 파일 오류',
                'message': '파일 처리 중 오류가 발생했습니다.',
                'suggestion': '파일이 존재하고 접근 권한이 있는지 확인해주세요.'
            },
            'unknown_error': {
                'title': '❓ 알 수 없는 오류',
                'message': '예상치 못한 오류가 발생했습니다.',
                'suggestion': '페이지를 새로고침하거나 관리자에게 문의해주세요.'
            }
        }
        
        error_info = error_messages.get(error_type, error_messages['unknown_error'])
        
        st.error(f"**{error_info['title']}**")
        st.error(error_info['message'])
        
        if details:
            with st.expander("🔍 상세 오류 정보"):
                st.code(details)
        
        suggestion_text = suggestions or error_info['suggestion']
        if suggestion_text:
            st.info(f"💡 **해결 방법**: {suggestion_text}")
    
    @staticmethod
    def show_warning(message: str, suggestion: str = None):
        """Display warning messages."""
        st.warning(f"⚠️ {message}")
        if suggestion:
            st.info(f"💡 {suggestion}")
    
    @staticmethod
    def show_success(message: str):
        """Display success messages."""
        st.success(f"✅ {message}")
    
    @staticmethod
    def log_error(error: Exception, context: Dict[str, Any] = None):
        """Log errors for debugging."""
        logger = logging.getLogger(__name__)
        
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'context': context or {}
        }
        
        logger.error(f"Error occurred: {error_info}")
        
        # 디버그 모드에서만 상세 정보 표시
        if st.get_option("runner.fastReruns"):
            with st.expander("🐛 디버그 정보 (개발 모드)"):
                st.json(error_info)


def handle_database_operation(operation_func, error_context: str = None):
    """Decorator for database operations with error handling."""
    def wrapper(*args, **kwargs):
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.log_error(e, {'context': error_context})
            ErrorHandler.show_error('db_error', str(e))
            return None
    return wrapper


def handle_api_call(api_func, api_name: str = None):
    """Decorator for API calls with error handling."""
    def wrapper(*args, **kwargs):
        try:
            return api_func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.log_error(e, {'api': api_name})
            ErrorHandler.show_error('api_error', str(e))
            return None
    return wrapper


def safe_execute(func, error_type: str = 'unknown_error', context: str = None, default_return=None):
    """Safely execute a function with error handling."""
    try:
        return func()
    except Exception as e:
        ErrorHandler.log_error(e, {'context': context})
        ErrorHandler.show_error(error_type, str(e))
        return default_return