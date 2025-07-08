from mcp.server.fastmcp import FastMCP
from service.model import *
from mcp.server.fastmcp.server import Context
from utils.http import HttpClient
from config.config import settings
from typing import Annotated
from pydantic import Field


http_client = HttpClient(settings.HTTP_TIMEOUT)


control_node_tool_desc = f"""
# 工具用途：节点控制
- 家庭、区域、房间、设备组、设备都被视为"节点"，其类型通过 nodeType 区分。
- 节点控制请求中的 nodeId 是节点的唯一标识。用户通常提供的是节点名称，因此在调用控制接口前，必须先使用相应工具获取节点nodeId，nodeId可以是家庭ID，区域ID，房间ID，设备组ID，设备ID，确认后再执行控制操作。
- 节点控制指令通过 command 区分不同的操作。
- 控制指令中参数的 value 类型需与节点属性值的类型一致。
- 在调用此接口之前，请先确认节点支持的属性及其对应的可操作类型。如果目标节点不支持该属性，则无法进行控制。
- 控制指令中的propName（**参数名称propName请勿传错**）参数，必须填写节点属性列表中对应属性的 propId 字段值，如 p（开关）、c（颜色）、ct（色温）、l（亮度）、tp（窗帘开合度）等。应根据节点属性列表中支持的 propId 选择最合适的属性来进行控制操作。

## 控制节点说明
家庭、区域、房间、设备组、设备都被视为"节点"，其类型通过 nodeType 区分。

例如：
- "关闭所有灯"的请求，可视为关闭家庭下所有的灯，可以使用家庭节点类型来实现。
- "打开客厅灯"的请求，可以使用房间节点类型来实现。

### 节点类型（nodeType）信息列表
| 节点类型（node） | 节点编码（nodeType） | 节点描述 | 说明 |
| -------- | ------- | ------- | ------- |
| house | 5 | 家庭 | 例如："关闭所有灯"的请求，可视为关闭家庭下所有的灯，可以使用家庭节点类型来实现。先通过获取家庭信息工具获取到家庭ID，再使用家庭ID控制家庭下的所有灯。| 
| area | 3 | 区域 | 控制某个区域，可先通过获取区域的工具获取到区域ID,来控制区域。| 
| room | 1 | 房间 | 控制某个房间，可先通过获取区域的工具获取到房间ID,来控制房间。| 
| group | 4 | 设备组、灯组 | 控制某个设备组，可先通过获取区域的工具获取到设备组ID,来控制设备组。| 
| device | 2 | 设备 | 控制某个设备，可先通过获取区域的工具获取到设备ID,来控制设备。| 

## 控制属性说明
- 可以通过其他工具获取到节点支持的属性定义列表，表示该节点所支持的属性。所控制节点的属性必须在该节点的属性定义列表中存在，否则会发生错误。
- 调用该工具控制节点属性时，传入的属性值需符合属性定义中的类型、取值范围、枚举值等的要求。

### 相关属性信息列表
下面是一些属性的定义，可能会与其他工具中返回的属性定义冗余，供参考。

| 属性编码（propId/propName） | 属性描述（desc）    | 属性格式（format）   | 属性单位（unit）    | 属性值范围（valueRange） | 属性值枚举（valueList） | 属性支持的操作（operators） | 属性说明 |
| -------- | ------- |  ------- | ------- | ------- | ------- | ------- | ------- | 
| p | 开关属性（仅用于标识灯和开关类设备的开关状态） | boolean |  - |  - |   true:开, false:关 | set | true:开, false:关 |
| l | 亮度 | uint8 | % |  min:1;max:100;step:1; | - | set | 例如：80表示亮度值为80% |
| c | 颜色 | uint32 | RGB |  min:0;max:16777215;step:1; | - | set | 十进制整形的RGB颜色表示。例如16711680表示红色（十六进制表示为#FF0000）， 255表示蓝色（十六进制表示为#0000FF）|
| ct | 色温 | uint8| K |  min:2700;max:6500;step:1; | - | set | 色温|
| tp | 窗帘目标开合度 | uint8 | % |  min:0;max:100;step:1; | - | set | 窗帘目标开合度，用于控制窗帘开合度，0代表完全关闭，100代表完全打开。例如30表示窗帘开合度为30%|

"""

execute_scene_tool_desc = """
# 工具用途：执行情景（场景、模式）。
- 在执行情景（场景、模式）前，必须确保已获取到对应的情景ID。由于用户通常提供的是情景名称，因此请务必先通过相应的工具获取情景ID，再使用该ID执行情景操作。
"""

def get_auth_info(context: Context) -> tuple[str, str, str]:
    request_context = getattr(context, "request_context", None)
    request = getattr(request_context, "request", None)
    if request is None or not hasattr(request, "headers"):
        raise ValueError("request or request.headers is None, 无法获取认证信息")
    authorization = request.headers.get(settings.AUTHORIZATION_HEADER_KEY)
    client_id = request.headers.get(settings.CLIENT_ID_HEADER_KEY)
    house_id = request.headers.get(settings.HOUSE_ID_HEADER_KEY)
    return f"Bearer {authorization}", client_id, house_id


def register_house_tool(mcp:FastMCP):
    @mcp.tool(
        name="get_currnet_house_info",
        description="获取用户当前家庭（或项目）的信息",
    )
    def get_currnet_house_info(context: Context) -> HouseInfo:
        authorization, client_id, house_id = get_auth_info(context)
        url = f"{settings.API_BASE_URL}/v1/open/node/house/{house_id}/r/info"
        response = http_client.get(url, headers={"authorization": authorization, "clientId": client_id})
        if response.get("code") != "200":
            return HouseInfo(**{"isError":True, "errorMessage":response.get("msg")})
        return HouseInfo(**response.get("data"))


def register_area_tool(mcp:FastMCP):
    @mcp.tool(
        name="get_areas",
        description="获取当前用户家庭（项目）下所有的区域",
    )
    def get_areas(context: Context) -> AreasResponse:
        authorization, client_id, house_id = get_auth_info(context)
        url = f"{settings.API_BASE_URL}/v1/open/node/house/{house_id}/areas/r/list/1/{settings.FETCH_NODES_MAX_SIZE}"

        response = http_client.get(url, headers={"authorization": authorization, "clientId": client_id})
        if response.get("code") != "200":
            return AreasResponse(**{"isError":True, "errorMessage":response.get("msg")})
        return AreasResponse(**response.get("data"))


def register_room_tool(mcp:FastMCP):
    @mcp.tool(
        name="get_rooms",
        description="获取当前用户家庭（项目）下所有的房间",
    )
    def get_rooms(context: Context) -> RoomsResponse:
        authorization, client_id, house_id = get_auth_info(context)
        url = f"{settings.API_BASE_URL}/v1/open/node/house/{house_id}/rooms/r/list/1/{settings.FETCH_NODES_MAX_SIZE}"
        response = http_client.get(url, headers={"authorization": authorization, "clientId": client_id})
        if response.get("code") != "200":
            return RoomsResponse(**{"isError":True, "errorMessage":response.get("msg")})
        return RoomsResponse(**response.get("data"))


def register_device_tool(mcp:FastMCP):
    @mcp.tool(
        name="get_devices",
        description="获取当前用户家庭（项目）下所有的设备或者获取某个房间下的设备",
    )
    def get_devices(context: Context, roomId: Annotated[Optional[str], Field(None, description="房间ID。若不传此参数，则查询当前用户家庭（项目）下所有的设备")]) -> DevicesResponse:
        authorization, client_id, house_id = get_auth_info(context)
        if roomId:
            url = f"{settings.API_BASE_URL}/v1/open/node/house/{house_id}/devices/r/list/1/{settings.FETCH_NODES_MAX_SIZE}?roomId={roomId}"
        else:
            url = f"{settings.API_BASE_URL}/v1/open/node/house/{house_id}/devices/r/list/1/{settings.FETCH_NODES_MAX_SIZE}"
        response = http_client.get(url, headers={"authorization": authorization, "clientId": client_id})
        if response.get("code") != "200":
            return DevicesResponse(**{"isError":True, "errorMessage":response.get("msg")})
        return DevicesResponse(**response.get("data"))


def register_group_tool(mcp:FastMCP):
    @mcp.tool(
        name="get_groups",
        description="获取当前用户家庭（项目）下所有的设备组或者获取某个房间下的设备组（设备组：相同设备类型的设备可以组成设备组，例如灯组、开关组灯）",
    )
    def get_groups(context: Context, roomId: Annotated[Optional[str], Field(None, description="房间ID。若不传此参数，则查询当前用户家庭（项目）下所有的设备组")]) -> DevicesResponse:
        authorization, client_id, house_id = get_auth_info(context)
        if roomId:
            url = f"{settings.API_BASE_URL}/v1/open/node/house/{house_id}/groups/r/list/1/{settings.FETCH_NODES_MAX_SIZE}?roomId={roomId}"
        else:
            url = f"{settings.API_BASE_URL}/v1/open/node/house/{house_id}/groups/r/list/1/{settings.FETCH_NODES_MAX_SIZE}"
        response = http_client.get(url, headers={"authorization": authorization, "clientId": client_id})
        if response.get("code") != "200":
            return DevicesResponse(**{"isError":True, "errorMessage":response.get("msg")})
        return DevicesResponse(**response.get("data"))


def register_scene_tool(mcp:FastMCP):
    @mcp.tool(
        name="get_scenes",
        description="获取当前用户家庭（项目）下所有的情景（场景、模式）",
    )
    def get_scenes(context: Context) -> ScenesResponse:
        authorization, client_id, house_id = get_auth_info(context)
        url = f"{settings.API_BASE_URL}/v1/open/node/house/{house_id}/scenes/r/list/1/{settings.FETCH_NODES_MAX_SIZE}"
        response = http_client.get(url, headers={"authorization": authorization, "clientId": client_id})
        if response.get("code") != "200":
            return ScenesResponse(**{"isError":True, "errorMessage":response.get("msg")})
        return ScenesResponse(**response.get("data"))
    
def register_control_node_tool(mcp:FastMCP):
    @mcp.tool(
        name="control_node",
        description=control_node_tool_desc
    )
    def control_node(context: Context, controlRequest: Annotated[ControlNodeRequest, Field(description="节点控制请求体，包含节点ID、节点类型和控制指令等信息")]):
        authorization, client_id, house_id = get_auth_info(context)
        node_type = controlRequest.nodeType
        node_id = controlRequest.nodeId
        command = controlRequest.command
        url = f"{settings.API_BASE_URL}/v1/open/control/house/{house_id}/control/{node_type}/{node_id}/w/properties"
        headers = {
            "authorization": authorization,
            "clientId": client_id
        }
        response = http_client.post(url, headers=headers, json=command.model_dump())
        return response


def register_execute_scene_tool(mcp:FastMCP):
    @mcp.tool(
        name="execute_scene",
        description=execute_scene_tool_desc
    )
    def execute_scene(context: Context, scene_id: Annotated[str, Field(description="情景ID")]):
        authorization, client_id, house_id = get_auth_info(context)
        url = f"{settings.API_BASE_URL}/v1/open/control/house/{house_id}/control/w/scenes/{scene_id}"
        headers = {
            "authorization": authorization,
            "clientId": client_id
        }
        response = http_client.post(url, headers=headers)
        return response


def register_tools(mcp:FastMCP):
    register_house_tool(mcp)
    register_area_tool(mcp)
    register_room_tool(mcp)
    register_device_tool(mcp)
    register_group_tool(mcp)
    register_control_node_tool(mcp)
    register_scene_tool(mcp)
    register_execute_scene_tool(mcp)

