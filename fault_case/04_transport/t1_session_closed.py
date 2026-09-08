"""Transport传输层故障1：会话中途关闭"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer()
    @server.tool()
    async def add(a: int, b: int) -> int:
        await asyncio.sleep(1)
        return a + b

    client = Client(server)
    try:
        await client.__aenter__()
        res1 = await client.call_tool("add", {"a": 1, "b": 2})
        print("首次调用成功：", res1)
        # 主动关闭会话
        await client.__aexit__(None, None, None)
        # 关闭后再次调用
        res2 = await client.call_tool("add", {"a": 3, "b": 4})
        print(res2)
    except Exception as e:
        print("=== 故障类型：Transport传输层 - 会话中途关闭 ===")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())