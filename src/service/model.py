from pydantic import BaseModel, Field
from typing import Any, List, Optional
from enum import Enum


class BaseMessage(BaseModel):
    isError: Optional[bool] = Field(None, description="是否请求失败")
    errorMessage: Optional[str] = Field(None, description="错误信息")


class ValueListItem(BaseModel):
    code: str = Field(..., description="枚举值代码")
    desc: str = Field("", description="枚举值描述")

class Property(BaseModel):
    unit: Optional[str] = Field(None, description="属性单位")
    operators: Optional[List[str]] = Field(None, description="属性支持的操作类型。set：设置；toggle：切换（常用于开关类设备）；adjust：调节，用于基于当前值进行调节")
    propId: Optional[str] = Field(None, description="属性ID。开关；c：颜色；ct：色温；l：亮度；tp：窗帘开合度")
    format: Optional[str] = Field(None, description="属性值格式")
    scale: Optional[int] = Field(None, description="缩放比例")
    zoom: Optional[int] = Field(None, description="缩放系数")
    value: Optional[Any] = Field(None, description="属性值")
    desc: Optional[str] = Field(None, description="属性描述")
    valueRange: Optional[dict] = Field(None, description="属性值范围")
    valueList: Optional[List[ValueListItem]] = Field(None, description="属性枚举值列表")


class HouseInfo(BaseMessage):
    icon: Optional[str] = Field(None, description="家庭/项目图标")
    name: Optional[str] = Field(None, description="家庭/项目名称")
    id: Optional[str] = Field(None, description="家庭/项目ID")
    properties: Optional[List[Property]] = Field(default_factory=list, description="属性列表")
    desc: Optional[str] = Field(None, description="家庭/项目别称")

class YeelightResponse(BaseModel):
    msg: str = Field(..., description="状态描述")
    code: str = Field(..., description="状态码")
    data: HouseInfo = Field(..., description="家庭/项目信息")
    success: bool = Field(..., description="是否成功")

class Room(BaseModel):
    icon: str = Field("", description="房间图标")
    name: str = Field(..., description="房间名称")
    id: str = Field(..., description="房间ID")
    properties: List[Property] = Field(default_factory=list, description="房间属性列表")

class RoomsResponse(BaseMessage):
    total: int = Field(..., description="房间总数")
    pageSize: int = Field(..., description="每页数量")
    rows: List[Room] = Field(default_factory=list, description="房间列表")
    pageNum: int = Field(..., description="页码")

class Area(BaseModel):
    roomIds: List[str] = Field(default_factory=list, description="区域包含的房间ID列表")
    level: int = Field(..., description="区域层级")
    icon: str = Field("", description="区域图标")
    name: str = Field(..., description="区域名称")
    id: str = Field(..., description="区域ID")
    properties: List[Property] = Field(default_factory=list, description="区域属性列表")

class AreasResponse(BaseMessage):
    total: int = Field(..., description="区域总数")
    pageSize: int = Field(..., description="每页数量")
    rows: List[Area] = Field(default_factory=list, description="区域列表")
    pageNum: int = Field(..., description="页码")

class Scene(BaseModel):
    icon: Optional[str] = Field(None, description="情景图标")
    name: Optional[str] = Field(None, description="情景名称")
    id: Optional[str] = Field(None, description="情景ID")

class ScenesResponse(BaseMessage):
    total: int = Field(..., description="情景总数")
    pageSize: int = Field(..., description="情景数量")
    rows: List[Scene] = Field(default_factory=list, description="情景列表")
    pageNum: int = Field(..., description="页码")

class DeviceEvent(BaseModel):
    name: str = Field(..., description="事件名称")
    id: str = Field(..., description="事件ID")
    desc: str = Field("", description="事件描述")


class SubDevice(BaseModel):
    name: str = Field(..., description="子设备名称")
    index: int = Field(..., description="子设备序号。通过index标识子设备序号，从1开始，例如多键开关的第一个按键，index为1。")
    category: str = Field(..., description="子设备品类")
    properties: List[Property] = Field(default_factory=list, description="子设备属性列表")
    desc: str = Field("", description="子设备描述")

class Device(BaseModel):
    subDeviceList: Optional[List[SubDevice]] = Field(default_factory=list, description="子设备列表。例如多键开关的每个按键就是一个子设备，子设备之间通过index序号进行区分，每个子设备可以独立控制。没有该字段为空或者空数组，表明该设备是一个单组件设备。")
    icon: Optional[str] = Field(None, description="设备图标")
    name: Optional[str] = Field(None, description="设备名称")
    id: Optional[str] = Field(None, description="设备ID")
    category: Optional[str] = Field(None, description="设备品类")
    nodeType: Optional[int] = Field(None, description="节点类型")
    events: Optional[List[DeviceEvent]] = Field(None, description="事件列表")
    properties: Optional[List[Property]] = Field(default_factory=list, description="设备属性列表")
    roomId: Optional[str] = Field(None, description="房间ID")

class DevicesResponse(BaseMessage):
    total: int = Field(..., description="设备总数")
    pageSize: int = Field(..., description="每页数量")
    rows: List[Device] = Field(default_factory=list, description="设备列表")
    pageNum: int = Field(..., description="页码")

class CommandType(str, Enum):
    set = "set"
    toggle = "toggle"
    adjust = "adjust"

class CommandParam(BaseModel):
    propName: str = Field(..., description="属性ID、属性编码。传入对应节点属性列表中的propId字段值，如p(开关)；c(颜色)；ct(颜色)；l(亮度)；tp(窗帘开合度)。具体使用的属性，需要在该节点属性列表中支持的属性的propId找到最合适的")
    value: Optional[Any] = Field(None, description="属性值。 属性值类型与节点属性列表中支持的属性的propId一致。例如：propId为c时，c是无符号十进制整形，value为颜色值，例如：红色是16711680")

class Command(BaseModel):
    command: CommandType = Field(..., description="指令类型：set：设值,可针对任意属性类型；toggle：反转、切换（针对boolean类型属性，例如设备的开关），adjust：调整（针对数值类型，基于当前值进行增减）\n 须使用该节点该属性支持的operators操作类型")
    params: List[CommandParam] = Field(default_factory=list, description="指令参数列表")
    duration: Optional[int] = Field(None, description="渐变时间长度长。单位：毫秒。指设备指定动作的渐变时间长度。例如可实现5秒灯光渐变开关灯等效果。")
    delay: Optional[int] = Field(None, description="延时时间长度。单位：毫秒。指设备指定动作的延时时间长度。例如可实现5秒后灯光渐变开关灯等效果。")
    index: Optional[int] = Field(None, description="子设备序号，单组件设备（没有子设备）不需要传该字段。通过index标识子设备序号，从1开始，例如多键开关的第一个按键，index为1。")

class ControlNodeRequest(BaseModel):
    nodeId: int = Field(..., description="节点ID。节点包括设备、设备组、房间、区域、家庭、情景灯。可根据nodeType区分")
    nodeType: int = Field(..., description="节点类型。1：房间；2：设备；3：区域；4：设备组；5：家庭（项目）；")
    command: Command = Field(..., description="具体控制指令。例如：set：设值,可针对任意属性类型；toggle：反转、切换（针对boolean类型属性，例如设备的开关），adjust：调整（针对数值类型，基于当前值进行增减）")





