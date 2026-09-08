"""Transport传输层故障2：请求中途取消"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def slow_tool():
    await asyncio.sleep(5)
    return "done"

async def main():
    server = MCPServer("demo-server")
    server.tool()(slow_tool)
    async with Client(server) as client:
        task = asyncio.create_task(client.call_tool("slow_tool",{}))
        await asyncio.sleep(0.5)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError as e:
            print("=== 故障类型：Transport传输层 - 请求中途取消 ===")
            print("异常类型: CancelledError")
            print("异常信息：工具请求执行中被主动取消")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())