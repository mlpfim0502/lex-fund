"""
Routers package
"""
from .cases import router as cases_router
from .search import router as search_router
from .chat import router as chat_router
from .analytics import router as analytics_router
from .data import router as data_router
from .checklist import router as checklist_router
from .docs import router as docs_router
from .backtest import router as backtest_router

__all__ = [
    "cases_router",
    "search_router",
    "chat_router",
    "analytics_router",
    "data_router",
    "checklist_router",
    "docs_router",
    "backtest_router",
]
