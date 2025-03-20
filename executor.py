import aiohttp
import asyncio

async def execute_api(base_url, api_name, details, headers):
    """Execute API request asynchronously."""
    url = f"{base_url}{api_name.split(' ', 1)[1]}"
    method = api_name.split(' ', 1)[0]
    payload = details.get("payload", {})
    
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, json=payload, headers=headers) as response:
            return {
                "api": api_name,
                "status": response.status,
                "response": await response.text()
            }

async def execute_all_apis(base_url, api_sequence, api_map, headers):
    """Execute all APIs in sequence."""
    results = []
    for api_name in api_sequence:
        details = api_map.get(api_name, {})
        result = await execute_api(base_url, api_name, details, headers)
        results.append(result)
    return results
