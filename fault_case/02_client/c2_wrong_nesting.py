"""Client报文层故障2：参数嵌套层级错误，畸形arguments结构"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")
    @server.tool()
    def add(a: int, b: int) -> int:
        """两数相加，要求顶层a、b"""
        return a + b

    async with Client(server) as client:
        try:
            # 错误：多套一层data，参数被嵌套
            # 正常{"a":1,"b":2}，错误{"data":{"a":1,"b":2}}
            response = await client.call_tool("add", {"data": {"a": 1, "b": 2}})
            print(response)
        except Exception as e:
            print("=== 故障类型：Client报文层 - 嵌套结构错误 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())