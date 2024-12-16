"""Tool allows agents to interact with the Twitter API.

To use this tool, you must first set as environment variables:
    OPENAI_API_KEY
    TWITTER_API_KEY
    TWITTER_API_SECRET
    TWITTER_ACCESS_TOKEN
    TWITTER_ACCESS_TOKEN_SECRET
    TWITTER_BEARER_TOKEN

"""

from collections.abc import Callable
from typing import Any

# from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool

# from pydantic import BaseModel

from twitter_langchain.twitter_api_wrapper import TwitterApiWrapper


class TwitterTool(BaseTool):  # type: ignore[override]
    """Tool for interacting with Twitter API."""

    def __init__(
        self,
        name: str,
        description: str,
        twitter_api_wrapper: TwitterApiWrapper,
        args_schema: dict,
        func: Callable[..., Any],
    ):
        """Initialize the TwitterTool."""
        super().__init__(name=name, description=description)
        self.twitter_api_wrapper = twitter_api_wrapper
        self.args_schema = args_schema
        self.func = func

    def _run(self, **kwargs: Any) -> Any:
        """Run the tool."""
        return self.twitter_api_wrapper.run_action(self.func, **kwargs)
