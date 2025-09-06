"""
Async handler for Streamlit applications
Handles asyncio event loop conflicts in Streamlit
"""

import asyncio
import threading
import concurrent.futures
from typing import Any, Coroutine
import logging

logger = logging.getLogger(__name__)

class StreamlitAsyncHandler:
    """Handle async operations in Streamlit context"""
    
    @staticmethod
    def run_async(coro: Coroutine) -> Any:
        """
        Run an async coroutine in Streamlit context
        
        This handles the event loop conflicts that occur when Streamlit
        is already running its own event loop.
        """
        try:
            # Check if we're already in an event loop
            loop = asyncio.get_running_loop()
            logger.debug("Already in event loop, using thread executor")
            
            # We're in an event loop, need to run in a separate thread
            def run_in_thread():
                # Create a new event loop for this thread
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()
                    asyncio.set_event_loop(None)
            
            # Use ThreadPoolExecutor to run the coroutine
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_in_thread)
                return future.result(timeout=60)  # 60 second timeout
                
        except RuntimeError as e:
            if "no running event loop" in str(e).lower():
                # No event loop running, safe to use asyncio.run
                logger.debug("No event loop running, using asyncio.run")
                return asyncio.run(coro)
            else:
                # Some other RuntimeError
                logger.error(f"RuntimeError in async handler: {e}")
                raise
        except Exception as e:
            logger.error(f"Error in async handler: {e}")
            raise

# Convenience function
def run_async(coro: Coroutine) -> Any:
    """Run async coroutine in Streamlit context"""
    return StreamlitAsyncHandler.run_async(coro)