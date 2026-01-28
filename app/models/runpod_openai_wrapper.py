"""
RunPod OpenAI-Compatible Wrapper for Agno
Allows RunPod Serverless vLLM to work seamlessly with Agno Agents
"""

from agno.models.openai import OpenAIChat
from agno.models.message import Message
from agno.models.response import ModelResponse
from typing import Optional, List, Iterator, Dict, Any
import requests
import time
import logging

logger = logging.getLogger(__name__)


class RunPodOpenAIChat(OpenAIChat):
    """
    OpenAI-compatible wrapper for RunPod Serverless vLLM
    
    This wrapper allows you to use RunPod vLLM endpoints with Agno Agents
    as if they were OpenAI models.
    
    Args:
        runpod_endpoint_id: Your RunPod serverless endpoint ID
        runpod_api_key: Your RunPod API key
        id: Model identifier (e.g., "Qwen/Qwen2.5-32B-Instruct")
        use_custom_handler: Set True if using custom OpenAI-compatible handler
        request_timeout: Request timeout in seconds (default: 300)
        **kwargs: Additional OpenAI-compatible parameters
    
    Example:
```python
        from agno.agent import Agent
        from runpod_openai_wrapper import RunPodOpenAIChat
        
        model = RunPodOpenAIChat(
            runpod_endpoint_id="abc123xyz",
            runpod_api_key="your-api-key",
            id="Qwen/Qwen2.5-32B-Instruct"
        )
        
        agent = Agent(
            model=model,
            instructions="You are a helpful assistant."
        )
        
        agent.print_response("Hello!")
```
    """
    
    runpod_endpoint_id: Optional[str] = None
    runpod_api_key: Optional[str] = None
    runpod_base_url: str = "https://api.runpod.ai/v2"
    use_custom_handler: bool = False
    request_timeout: int = 300
    
    def __init__(
        self,
        runpod_endpoint_id: str,
        runpod_api_key: str,
        id: str = "vllm-model",
        use_custom_handler: bool = False,
        request_timeout: int = 300,
        **kwargs
    ):
        # Initialize parent OpenAIChat
        super().__init__(id=id, **kwargs)
        
        # Set RunPod-specific attributes
        self.runpod_endpoint_id = runpod_endpoint_id
        self.runpod_api_key = runpod_api_key
        self.use_custom_handler = use_custom_handler
        self.request_timeout = request_timeout
    
    def _call_runpod(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call RunPod serverless endpoint"""
        
        url = f"{self.runpod_base_url}/{self.runpod_endpoint_id}/runsync"
        
        headers = {
            "Authorization": f"Bearer {self.runpod_api_key}",
            "Content-Type": "application/json"
        }
        
        # Build payload
        payload = {
            "input": {
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", getattr(self, "max_tokens", 512)),
                "temperature": kwargs.get("temperature", getattr(self, "temperature", 0.7)),
                "top_p": kwargs.get("top_p", getattr(self, "top_p", 0.9)),
                "stop": kwargs.get("stop", None),
            }
        }
        
        logger.debug(f"RunPod request: {url}")
        logger.debug(f"Payload: {payload}")
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                headers=headers, 
                timeout=self.request_timeout
            )
            response.raise_for_status()
            result = response.json()
            logger.debug(f"RunPod response: {result}")
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"RunPod request timeout after {self.request_timeout}s")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"RunPod API error: {e}")
            raise
    
    def _transform_to_openai_format(self, runpod_response: Dict) -> Dict:
        """Transform RunPod response to OpenAI-compatible format"""
        
        output = runpod_response.get("output", {})
        
        # Check if using custom handler (already OpenAI format)
        if self.use_custom_handler and isinstance(output, dict):
            if "choices" in output and output.get("choices"):
                first_choice = output["choices"][0]
                if "message" in first_choice:
                    return output  # Already OpenAI format
        
        # Handle list wrapper (default vLLM format)
        if isinstance(output, list) and len(output) > 0:
            output = output[0]
        
        # Transform default vLLM format
        if isinstance(output, dict):
            choices = output.get("choices", [])
            
            if choices and "tokens" in choices[0]:
                # Extract content
                content = choices[0]["tokens"][0] if choices[0]["tokens"] else ""
                
                # Extract usage
                usage = output.get("usage", {})
                prompt_tokens = usage.get("input", 0)
                completion_tokens = usage.get("output", 0)
                
                return {
                    "id": runpod_response.get("id", "chatcmpl-runpod"),
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": self.id,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": content
                            },
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens
                    }
                }
        
        # Fallback: unexpected format
        logger.warning(f"Unexpected RunPod response format: {output}")
        return {
            "id": "chatcmpl-error",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": self.id,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"Error: Unexpected response format - {str(output)}"
                    },
                    "finish_reason": "error"
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
    
    def response(self, messages: List[Message]) -> ModelResponse:
        """
        Generate response using RunPod endpoint
        
        This method is called by Agno Agents to get model responses.
        """
        
        # Convert Agno Messages to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        logger.debug(f"Sending {len(openai_messages)} messages to RunPod")
        
        # Call RunPod
        runpod_response = self._call_runpod(openai_messages)
        
        # Transform to OpenAI format
        openai_response = self._transform_to_openai_format(runpod_response)
        
        # Extract content
        content = openai_response["choices"][0]["message"]["content"]
        
        # Build Agno ModelResponse
        return ModelResponse(
            content=content,
            model=self.id,
            metrics={
                "time": runpod_response.get("executionTime", 0) / 1000,  # ms to s
                "prompt_tokens": openai_response["usage"]["prompt_tokens"],
                "completion_tokens": openai_response["usage"]["completion_tokens"],
                "total_tokens": openai_response["usage"]["total_tokens"],
            }
        )
    
    def response_stream(self, messages: List[Message]) -> Iterator[ModelResponse]:
        """
        Streaming not currently supported
        
        Falls back to regular response method.
        """
        logger.warning("Streaming not supported for RunPod wrapper, using regular response")
        yield self.response(messages)