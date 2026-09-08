"""正常示例：无故障，用来对比基线"""
import asyncio
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    # 1. 创建 Server，注册一个正常工具
    server = MCPServer("demo-server")

    @server.tool()
    def add(a: int, b: int) -> int:
        """两个数相加"""
        return a + b

    # 2. Client 直接连 Server 实例（内存传输，自动完成）
    async with Client(server) as client:
        # 3. 调用工具
        result = await client.call_tool("add", {"a": 1, "b": 2})
        print("=== 正常返回 ===")
        print(result)

if __name__ == "__main__":
    asyncio.run(main())