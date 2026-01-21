from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
import requests
import re
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

app = FastAPI(title="Leave Accrual MCP Server", version="0.1.0")


# ============================================
# JSON-RPC 2.0 Models
# ============================================

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[int, str]] = None


class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Union[int, str]] = None


class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


# ============================================
# MCP Protocol Models
# ============================================

class ServerInfo(BaseModel):
    name: str
    version: str


class Implementation(BaseModel):
    name: str
    version: str


class ToolInfo(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]


# ============================================
# Main Endpoint
# ============================================

@app.post("/mcp")
async def mcp_handler(request: Request):
    """Handle MCP JSON-RPC requests"""
    
    # Get raw body
    body_bytes = await request.body()
    body_str = body_bytes.decode('utf-8')
    
    # Log incoming request
    print("\n" + "="*70)
    print(f"🕐 TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print("📦 RAW BODY:")
    print(body_str)
    print("-"*70)
    
    # Parse JSON
    try:
        body_json = json.loads(body_str)
        print("✅ PARSED JSON:")
        print(json.dumps(body_json, indent=2, ensure_ascii=False))
        print("-"*70)
    except json.JSONDecodeError as e:
        print(f"❌ JSON PARSE ERROR: {e}")
        print("="*70 + "\n")
        return JSONRPCResponse(
            jsonrpc="2.0",
            error={
                "code": -32700,
                "message": "Parse error",
                "data": str(e)
            },
            id=None
        ).dict()
    
    # Parse JSON-RPC request
    try:
        rpc_request = JSONRPCRequest(**body_json)
        print(f"✅ JSON-RPC METHOD: {rpc_request.method}")
        print(f"   Params: {rpc_request.params}")
        print(f"   ID: {rpc_request.id}")
    except Exception as e:
        print(f"❌ JSON-RPC VALIDATION ERROR: {e}")
        print("="*70 + "\n")
        return JSONRPCResponse(
            jsonrpc="2.0",
            error={
                "code": -32600,
                "message": "Invalid Request",
                "data": str(e)
            },
            id=body_json.get("id")
        ).dict()
    
    print("="*70 + "\n")
    
    # Route to appropriate handler
    try:
        if rpc_request.method == "initialize":
            result = handle_initialize(rpc_request.params)
        elif rpc_request.method == "tools/list":
            result = handle_tools_list(rpc_request.params)
        elif rpc_request.method == "tools/call":
            result = handle_tools_call(rpc_request.params)
        elif rpc_request.method == "ping":
            result = {}
        else:
            return JSONRPCResponse(
                jsonrpc="2.0",
                error={
                    "code": -32601,
                    "message": f"Method not found: {rpc_request.method}"
                },
                id=rpc_request.id
            ).dict()
        
        print(f"✅ Response prepared for method: {rpc_request.method}\n")
        
        return JSONRPCResponse(
            jsonrpc="2.0",
            result=result,
            id=rpc_request.id
        ).dict()
        
    except Exception as e:
        print(f"❌ ERROR handling {rpc_request.method}: {e}\n")
        return JSONRPCResponse(
            jsonrpc="2.0",
            error={
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            },
            id=rpc_request.id
        ).dict()


# ============================================
# MCP Method Handlers
# ============================================

def handle_initialize(params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle initialize request"""
    print("🔧 Handling initialize...")
    
    return {
        "protocolVersion": "2025-11-25",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "LeaveAccrual",
            "version": "0.1.0"
        }
    }


def handle_tools_list(params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle tools/list request"""
    print("📋 Handling tools/list...")
    
    return {
        "tools": [
            {
                "name": "GetLeaveAccrual",
                "description": (
                    "Get the remaining employee leave balance as of a specific date. "
                    "The date information must be from the user, not you."
                    "Use this tool when you need to calculate or check how many leave days "
                    "are still available on a given date. "
                    "Returns remaining employee leave balance based on date."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "Date to check leave balance for (YYYY-MM-DD)",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        }
                    },
                    "required": ["date"]
                }
            }
        ]
    }


def handle_tools_call(params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle tools/call request"""
    print("🛠️  Handling tools/call...")
    
    if not params:
        raise ValueError("Missing params for tools/call")
    
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    print(f"   Tool: {tool_name}")
    print(f"   Arguments: {arguments}")
    
    if tool_name != "GetLeaveAccrual":
        raise ValueError(f"Unknown tool: {tool_name}")
    
    # Extract date
    date_str = arguments.get("date")
    
    if not date_str:
        raise ValueError("Missing required argument: 'date'")
    
    # Validate date format
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
    
    # Call the HR API
    print(f"🚀 Calling HR API with date: {date_str}")
    leave_data = get_leave_accrual(date_str)
    print(f"✅ HR API call successful")
    
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(leave_data, indent=2)
            }
        ]
    }


# ============================================
# HR API Call
# ============================================

def get_leave_accrual(date: str) -> Dict[str, Any]:
    """
    Fetch leave accrual data from the HR API
    
    Args:
        date: Date in YYYY-MM-DD format
        
    Returns:
        Dictionary containing leave accrual data
    """
    url = "https://hrp07-dev-be-v3.harpa-go.com:8080/apps/accrualPlans/getNetEntitleMobile/"
    
    params = {
        "people_uuid": "7f9ae3e9-b13e-425c-9476-55d3344bd21b",
        "effective_date": date
    }
    
    headers = {
        "Accept": "*/*",
        "Access-Function": "0d78d111-d1fe-444d-861a-5c6ed0edcc15",
        "Access-Org": "09439306-b3b8-44db-8740-c069f48e7312",
        "Access-Role": "9434a7bd-d719-4d70-9476-3e7be6a4d219",
        "Authorization": "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1NzIsInVzZXJuYW1lIjoiQ09SQkVONTUiLCJleHAiOjE3Njg4ODM1MTEsInVzZXJfbmFtZSI6IkNPUkJFTjU1Iiwib3JpZ19pYXQiOjE3Njg3OTcxMTEsImxvZ2luX3V1aWQiOiI4ODUzMTQ2NS0xOWFmLTQ3ZGMtYmI0Ni1kMWJkZjRkNWE5ZGIiLCJ1c2VyX3V1aWQiOiJkODcxYTkyNi04ZDNmLTRiMDAtOGUxMS0zN2E4ZTBkMzQwZTMifQ.qtQUnkEBW1HBoXTfWrsiNwNebel6qtL-NFsF41vt6zE",
        "Referer": "https://hrp07-dev-v3.harpa-go.com:8080/"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        return {
            "status": "success",
            "as_of_date": date,
            "leave_data": response.json()
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Failed to get leave data: {str(e)}"
        }


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Leave Accrual MCP Server",
        "protocol": "JSON-RPC 2.0",
        "version": "0.1.0"
    }


# Run with: uvicorn main:app --reload --port 8000