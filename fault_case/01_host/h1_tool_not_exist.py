"""Host层故障1：LLM幻觉，调用不存在的工具名"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def add(a: int, b: int) -> int:
        """两个数相加"""
        return a + b

    async with Client(server) as client:
        try:
            # Host 错误：调用了一个根本不存在的工具 "subtract"
            result = await client.call_tool("subtract", {"a": 5, "b": 3})
            print(result)
        except Exception as e:
            print("=== 故障类型：Host调度层 - 工具不存在 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())