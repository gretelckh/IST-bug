# MCP 故障数据集构建 — 学生操作手册（任务一）

> 目标：基于官方 MCP Python v2 SDK，构建 20 个可复现故障脚本 + 故障汇总 Excel 表。
> 全部使用内存传输（in-memory），Windows/Linux 均可稳定运行，不涉及 stdio 管道。

---

## 第一步：环境搭建（必须先做完）

### 1.1 克隆官方仓库

```bash
git clone https://github.com/modelcontextprotocol/python-sdk.git
cd python-sdk
```

### 1.2 创建虚拟环境并安装依赖

```bash
python -m venv .venv
# Windows:要换cmd跑
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -e ".[cli]"
# windows：如果上面这个安装失败:执行下面（如果你是其他系统然后运行出问题的话，可以问ai解决方案）
git checkout v2.0.0
pip install -e ".[cli]"
```

验证安装成功：

```bash
python -c "from mcp.server.mcpserver import MCPServer; from mcp.client.client import Client; print('OK')"
```

输出 `OK` 即为成功。

### 1.3 创建工作目录

在仓库根目录下新建文件夹，所有代码放这里，**不要修改 SDK 源码**：

```
python-sdk/
└── fault_case/              ← 所有故障脚本放这里
    ├── 01_host/             ← Host 调度层故障（4个）
    ├── 02_client/           ← Client 报文层故障（4个）
    ├── 03_server/           ← Server 工具层故障（8个）
    ├── 04_transport/        ← Transport 传输层故障（4个）
    └── fault_dataset.xlsx   ← 故障汇总表
```

创建命令（**Windows CMD 用反斜杠**）：

```bash
mkdir fault_case
mkdir fault_case\01_host
mkdir fault_case\02_client
mkdir fault_case\03_server
mkdir fault_case\04_transport
```

### 1.4 用 VS Code 打开项目文件夹（创建代码文件的方法）

**必须先打开文件夹，才能在里面创建 .py 文件。**

方法一（推荐）：在命令行里输入：

```bash
code .
```

这会用 VS Code 打开当前的 `python-sdk` 文件夹。

方法二：手动打开 VS Code → 文件 → 打开文件夹 → 选择 `python-sdk` 文件夹。

**在 VS Code 里创建 .py 文件的步骤：**

1. 左侧资源管理器里找到 `fault_case` 文件夹，点击展开
2. 鼠标悬停在要放文件的文件夹上（比如 `01_host`），点击出现的「新建文件」图标
3. 输入文件名（比如 `h1_tool_not_exist.py`），按回车
4. 把手册里的代码复制粘贴进去
5. 按 `Ctrl + S` 保存

**运行 .py 文件的方法：**

回到命令行（CMD/PowerShell），确保在 `python-sdk` 目录下，输入：

```bash
python fault_case\01_host\h1_tool_not_exist.py
```

（没激活虚拟环境就用 `.venv\Scripts\python.exe` 代替 `python`）

---

## 第二步：理解基础模板（先跑通这个，再做故障）

每个故障脚本的结构都是：**创建一个正常的 Server → 用 Client 连接 → 故意触发一个故障 → 打印完整报错**。

先把下面这个「正常示例」保存为 `fault_case/00_normal_example.py`，跑通确认环境没问题：

```python
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
```

运行（Windows 用反斜杠）：

```bash
python fault_case\00_normal_example.py
```

能看到正常返回结果，说明环境 OK，继续下面的故障脚本。

---

## 第三步：20 个故障脚本（逐个复制，逐个运行）

### 第一层：Host 调度层故障（4个）

> 故障根源：LLM/Host 生成的工具调用内容本身错误（工具名、参数内容）。
> Server 代码完全正常，只是 Host 发过来的请求不对。

#### H1：调用不存在的工具

文件：`fault_case/01_host/h1_tool_not_exist.py`

```python
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
```

#### H2：缺少必填参数

文件：`fault_case/01_host/h2_missing_param.py`

```python
"""Host层故障2：LLM漏传必填参数 b"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def add(a: int, b: int) -> int:
        """两个数相加，a和b都是必填"""
        return a + b

    async with Client(server) as client:
        try:
            # Host 错误：只传了 a，漏了必填的 b
            result = await client.call_tool("add", {"a": 5})
            print(result)
        except Exception as e:
            print("=== 故障类型：Host调度层 - 缺少必填参数 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

#### H3：参数名拼写错误

文件：`fault_case/01_host/h3_wrong_param_name.py`

```python
"""Host层故障3：LLM把参数名 user_id 写成 userId"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def get_user(user_id: int) -> str:
        """根据用户ID查询用户"""
        return f"User_{user_id}"

    async with Client(server) as client:
        try:
            # Host 错误：参数名应该是 user_id，写成了 userId
            result = await client.call_tool("get_user", {"userId": 123})
            print(result)
        except Exception as e:
            print("=== 故障类型：Host调度层 - 参数名拼写错误 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

#### H4：参数类型错误（LLM 传了字符串而不是数字）

文件：`fault_case/01_host/h4_wrong_param_type.py`

```python
"""Host层故障4：LLM把int参数传成了字符串"""
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
            # Host 错误：a 应该是 int，传成了字符串 "5"
            result = await client.call_tool("add", {"a": "5", "b": 3})
            print(result)
        except Exception as e:
            print("=== 故障类型：Host调度层 - 参数类型错误 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

---

### 第二层：Client 报文层故障（4个）

> 故障根源：Client 封装/解析 JSON-RPC 报文时出错。
> Host 给的业务数据没问题，是打包成协议报文时出了问题。
> 实现方式：绕过 Client 高层 API，直接用底层 ClientSession 发送畸形报文。

#### C1：传入多余未定义参数

文件：`fault_case/02_client/c1_extra_param.py`

```python
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
```

#### C2：嵌套 JSON 结构错误（参数多包了一层）

文件：`fault_case/02_client/c2_wrong_nesting.py`

```python
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
```

#### C3：枚举值非法

文件：`fault_case/02_client/c3_invalid_enum.py`

```python
"""Client报文层故障3：Client传了一个不在枚举范围内的值"""
import asyncio
import traceback
from enum import Enum
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

class Color(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def set_color(color: Color) -> str:
        """设置颜色，只接受 red/green/blue"""
        return f"Color set to {color.value}"

    async with Client(server) as client:
        try:
            # Client 错误：传了 "yellow"，不在枚举范围内
            result = await client.call_tool("set_color", {"color": "yellow"})
            print(result)
        except Exception as e:
            print("=== 故障类型：Client报文层 - 枚举值非法 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

#### C4：协议方法名写错（JSON-RPC method 字段错误）

文件：`fault_case/02_client/c4_wrong_method.py`

```python
"""Client报文层故障4：JSON-RPC方法名错误（v2高层Client封装不可篡改method，仅模拟说明）"""
import asyncio
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")
    @server.tool()
    def add(a: int, b: int) -> int:
        return a + b

    print("=== 故障类型：Client报文层 - 协议方法名错误 ===")
    print("【重要说明】MCP v2官方高层Client内置固定method='tools/call'，上层API无法手动传入错误method如'tool/call'；")
    print("该故障仅底层原始JSON-RPC发送场景可复现，本SDK封装后屏蔽此故障触发路径。")
    async with Client(server) as client:
        res = await client.call_tool("add", {"a":1,"b":2})
        print("正常返回：", res)

if __name__ == "__main__":
    asyncio.run(main())
```

---

### 第三层：Server 工具层故障（8个）

> 故障根源：Server 内部工具代码、配置、权限、返回逻辑出错。
> Host 和 Client 发的请求完全合规，是 Server 自己炸了。

#### S1：工具内部除零异常

文件：`fault_case/03_server/s1_divide_by_zero.py`

```python
"""Server工具层故障1：工具内部除零运算崩溃"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def divide(a: int, b: int) -> float:
        """除法运算"""
        # Server 错误：b=0 时触发除零异常
        return a / b

    async with Client(server) as client:
        try:
            result = await client.call_tool("divide", {"a": 10, "b": 0})
            print(result)
        except Exception as e:
            print("=== 故障类型：Server工具层 - 除零异常 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

#### S2：数组下标越界

文件：`fault_case/03_server/s2_index_out_of_range.py`

```python
"""Server工具层故障2：工具内部数组越界"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def get_item(index: int) -> str:
        """获取列表中的元素"""
        items = ["apple", "banana", "cherry"]
        # Server 错误：index 超出列表长度
        return items[index]

    async with Client(server) as client:
        try:
            result = await client.call_tool("get_item", {"index": 99})
            print(result)
        except Exception as e:
            print("=== 故障类型：Server工具层 - 数组越界 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

#### S3：自定义业务断言异常

文件：`fault_case/03_server/s3_assertion_error.py`

```python
"""Server工具层故障3：工具内部业务断言失败"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def withdraw(amount: int) -> str:
        """取款"""
        balance = 100
        # Server 错误：余额不足时断言失败
        assert amount <= balance, f"余额不足，当前余额: {balance}"
        return f"取款成功，剩余余额: {balance - amount}"

    async with Client(server) as client:
        try:
            result = await client.call_tool("withdraw", {"amount": 500})
            print(result)
        except Exception as e:
            print("=== 故障类型：Server工具层 - 断言异常 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

#### S4：自定义业务异常抛出

文件：`fault_case/03_server/s4_custom_exception.py`

```python
"""Server工具层故障4：工具抛出自定义业务异常"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

class OrderNotFoundError(Exception):
    """自定义异常：订单不存在"""
    pass

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def get_order(order_id: str) -> str:
        """查询订单"""
        valid_orders = {"ORD001", "ORD002"}
        if order_id not in valid_orders:
            # Server 错误：抛出自定义业务异常
            raise OrderNotFoundError(f"订单 {order_id} 不存在")
        return f"订单 {order_id} 详情: ..."

    async with Client(server) as client:
        try:
            result = await client.call_tool("get_order", {"order_id": "ORD999"})
            print(result)
        except Exception as e:
            print("=== 故障类型：Server工具层 - 自定义业务异常 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

#### S5：工具返回超大文本导致报文膨胀（Taraghi 高频故障）

文件：`fault_case/03_server/s5_oversized_response.py`

```python
"""Server工具层故障5：工具返回超大文本，JSON载荷膨胀"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def generate_huge_text() -> str:
        """生成超大文本"""
        # Server 错误：返回 1000 万字符的超大文本
        return "x" * 10_000_000

    async with Client(server) as client:
        try:
            result = await client.call_tool("generate_huge_text", {})
            print(f"返回长度: {len(str(result))}")
        except Exception as e:
            print("=== 故障类型：Server工具层 - 返回超大文本 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {str(e)[:500]}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

#### S6：Pydantic 模型序列化失败（Taraghi 高频故障）

文件：`fault_case/03_server/s6_pydantic_serialize_error.py`

```python
"""Server工具层故障6：工具返回不可JSON序列化的对象，序列化失败"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

class User:
    """普通类，无法被JSON序列化"""
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def get_user_info(user_id: int) -> dict:
        """获取用户信息"""
        # Server 错误：返回了一个不可JSON序列化的自定义对象
        user = User(name="Alice", age=30)
        return {"user": user}  # User 对象无法被 JSON 序列化

    async with Client(server) as client:
        try:
            result = await client.call_tool("get_user_info", {"user_id": 1})
            print(result)
        except Exception as e:
            print("=== 故障类型：Server工具层 - JSON序列化失败 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

#### S7：工具重复注册，客户端检索混乱（Taraghi 高频故障）

文件：`fault_case/03_server/s7_duplicate_tool_registration.py`

```python
"""Server工具层故障7：同一个工具名重复注册"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def get_info() -> str:
        """获取信息 - 版本1"""
        return "Version 1"

    try:
        # Server 错误：用同一个名字再注册一次
        @server.tool()
        def get_info() -> str:
            """获取信息 - 版本2"""
            return "Version 2"
    except Exception as e:
        print("=== 故障类型：Server工具层 - 工具重复注册 ===")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {e}")
        print("=== 完整堆栈 ===")
        traceback.print_exc()
        return

    # 如果没报错，尝试调用看看返回哪个版本
    async with Client(server) as client:
        tools = await client.list_tools()
        print(f"工具列表: {[t.name for t in tools.tools]}")
        result = await client.call_tool("get_info", {})
        print(f"调用结果: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

#### S8：工具鉴权/权限校验失败（Taraghi 高频故障）

文件：`fault_case/03_server/s8_auth_error.py`

```python
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def delete_file(file_path: str, api_key: str) -> str:
        """删除文件，需要API密钥"""
        # Server 错误：模拟鉴权失败
        valid_key = "sk-valid-12345"
        if api_key != valid_key:
            raise PermissionError(f"鉴权失败，API密钥无效: {api_key}")
        return f"文件 {file_path} 已删除"

    async with Client(server) as client:
        try:
            # 传入错误的 API 密钥
            result = await client.call_tool(
                "delete_file",
                {"file_path": "/tmp/test.txt", "api_key": "sk-wrong-key"}
            )
            print(result)
        except Exception as e:
            print("=== 故障类型：Server工具层 - 鉴权权限失败 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

---

### 第四层：Transport 传输层故障（4个）

> 故障根源：Client 和 Server 之间的通信通道出问题。
> 全部用内存传输模拟，不涉及 Windows stdio 管道。

#### T1：会话中途关闭

文件：`fault_case/04_transport/t1_session_closed.py`

```python
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
```

#### T2：请求中途取消

文件：`fault_case/04_transport/t2_request_cancelled.py`

```python
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
```

#### T3：发送非法原始消息（非标准 JSON-RPC）

文件：`fault_case/04_transport/t3_invalid_message.py`

```python
"""Transport传输层故障3：非法原始消息（v2高层无原始报文发送接口，仅说明）"""
import asyncio
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")
    @server.tool()
    def add(a:int,b:int) -> int:
        return a+b
    print("=== 故障类型：Transport传输层 - 非法消息载荷 ===")
    print("【说明】v2高层Client封装全部JSON-RPC序列化逻辑，上层无法手动写入非法原始字符串报文；")
    print("该故障仅底层传输流直接写数据场景可触发，本高层脚本无法复现。")
    async with Client(server) as client:
        print(await client.call_tool("add",{"a":1,"b":2}))

if __name__ == "__main__":
    asyncio.run(main())
```

#### T4：初始化时序错误（Client 未等握手完成就发请求）

文件：`fault_case/04_transport/t4_timing_error.py`

```python
"""Transport传输层故障4：初始化时序错误，未握手直接调用工具"""
import asyncio
import traceback
from mcp import Client
from mcp.server.mcpserver import MCPServer

async def main():
    server = MCPServer("demo-server")
    @server.tool()
    def add(a:int,b:int) -> int:
        return a+b
    client = Client(server)
    try:
        # 未执行async with/await __aenter__初始化握手，直接调用
        res = await client.call_tool("add",{"a":1,"b":2})
        print(res)
    except Exception as e:
        print("=== 故障类型：Transport传输层 - 初始化时序错误 ===")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 第四步：逐个运行脚本，采集报错信息

### 4.1 运行命令（Windows 用反斜杠）

每个脚本单独运行：

```bash
python fault_case\01_host\h1_tool_not_exist.py
python fault_case\01_host\h2_missing_param.py
python fault_case\01_host\h3_wrong_param_name.py
python fault_case\01_host\h4_wrong_param_type.py

python fault_case\02_client\c1_extra_param.py
python fault_case\02_client\c2_wrong_nesting.py
python fault_case\02_client\c3_invalid_enum.py
python fault_case\02_client\c4_wrong_method.py

python fault_case\03_server\s1_divide_by_zero.py
python fault_case\03_server\s2_index_out_of_range.py
python fault_case\03_server\s3_assertion_error.py
python fault_case\03_server\s4_custom_exception.py
python fault_case\03_server\s5_oversized_response.py
python fault_case\03_server\s6_pydantic_serialize_error.py
python fault_case\03_server\s7_duplicate_tool_registration.py
python fault_case\03_server\s8_auth_error.py

python fault_case\04_transport\t1_session_closed.py
python fault_case\04_transport\t2_request_cancelled.py
python fault_case\04_transport\t3_invalid_message.py
python fault_case\04_transport\t4_timing_error.py
```

### 4.2 每个脚本运行后，记录以下信息到 Excel

| 字段 | 说明 |
|------|------|
| 序号 | 1-20 |
| 故障分层 | Host调度层 / Client报文层 / Server工具层 / Transport传输层 |
| 脚本文件名 | 如 h1_tool_not_exist.py |
| 故障描述 | 一句话说明这个故障是什么 |
| 触发代码片段 | 贴出导致故障的那 1-3 行核心代码 |
| 异常类型 | 如 ValueError、PermissionError、CancelledError |
| 完整报错文本 | 把终端输出的完整堆栈**原样复制**，不要删减、不要美化 |
| Taraghi对应大类 | 映射到论文5分类：Server Setting / Server-Tool / Server-Host / Documentation / General Programming |
| 故障范围标记 | 单层故障 / 跨Host-Server跨组件故障 |

### 4.3 Taraghi 五大类映射参考

| 我们的分层 | 对应 Taraghi 大类 |
|-----------|-------------------|
| Host调度层（全部） | Server/Host Configuration → LLM 子类 |
| Client报文层（全部） | Server/Host Configuration → Host Connection Configuration |
| Server工具层 S1-S4 | General Programming / Server-Tool Configuration |
| Server工具层 S5-S8 | Server/Tool Configuration |
| Transport传输层（全部） | Server Setting / Server-Host Configuration |

---

## 第五步：Excel 表格模板

创建 `fault_case/fault_dataset.xlsx`，表头如下（第一行）：

```
序号 | 故障分层 | 脚本文件名 | 故障描述 | 触发代码片段 | 异常类型 | 完整报错文本 | Taraghi对应大类 | 故障范围标记
```

20 行数据，按上面 20 个脚本依次填写。

---


## 第六步：最终交付物检查清单

完成后确认以下内容全部存在：

- [ ] `fault_case/00_normal_example.py`（正常基线）
- [ ] `fault_case/01_host/` 下 4 个脚本（h1-h4）
- [ ] `fault_case/02_client/` 下 4 个脚本（c1-c4）
- [ ] `fault_case/03_server/` 下 8 个脚本（s1-s8）
- [ ] `fault_case/04_transport/` 下 4 个脚本（t1-t4）
- [ ] `fault_case/fault_dataset.xlsx`（20行数据，9列）
- [ ] 每个脚本都能独立运行，且确实能触发对应故障
- [ ] Excel 中「完整报错文本」列是终端原样输出，没有人工修改

---

## 常见问题

**Q: PowerShell 提示"无法加载文件，禁止运行脚本"？**
A: 这是 PowerShell 的执行策略限制。两种解决方法：
1. 不用激活虚拟环境，直接用 `.venv\Scripts\python.exe` 运行所有命令（推荐，最简单）
2. 以管理员身份打开 PowerShell，运行 `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`，输入 Y 确认

**Q: 某个脚本运行后没有报错？**
A: 说明这个故障在当前 SDK 版本下被自动处理了。记录实际输出（即使是正常返回），在 Excel 备注里写「该版本SDK已自动处理此故障」，这本身也是有价值的发现。

**Q: InMemoryTransport 导入报错？**
A: 确认安装的是 v2.0.0 版本 SDK。运行 `python -c "import mcp; print(mcp.__version__)"` 查看版本。如果不是 2.0.0，重新运行 `git checkout v2.0.0` 和 `pip install -e ".[cli]"`。

**Q: 报错文本太长，Excel 装不下？**
A: 没关系，Excel 单元格可以放很长文本。如果实在太长，把完整堆栈存到单独的 `.txt` 文件（放在对应脚本同目录），Excel 里填文件名引用。

**Q: 运行脚本提示找不到模块？**
A: 确认你在 `python-sdk` 根目录下运行命令，并且已经执行过 `pip install -e ".[cli]"`。
