"""Client报文层故障1：Client组装报文时多加了一个未定义参数"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def add(a: int, b: int) -> int:
        """两个数相加，只接受a和b"""
        return a + b

    async with Client(server) as client:
        try:
            # Client 错误：多传了一个未定义的参数 c
            result = await client.call_tool("add", {"a": 1, "b": 2, "c": 999})
            print(result)
        except Exception as e:
            print("=== 故障类型：Client报文层 - 多余未定义参数 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())