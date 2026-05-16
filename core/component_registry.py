# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class PropType(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    COLOR = "color"
    IMAGE = "image"
    FONT = "font"
    RECT = "rect"
    ENUM = "enum"
    INSETS = "insets"


@dataclass
class PropertyDef:
    name: str
    prop_type: PropType
    default: object = None
    display_name: str = ""
    enum_values: List[str] = field(default_factory=list)
    category: str = "common"
    tooltip: str = ""


@dataclass
class ComponentDef:
    class_name: str
    parent_class: str
    display_name: str
    category: str
    properties: List[PropertyDef] = field(default_factory=list)
    is_container: bool = False
    is_pvz: bool = False
    icon_name: str = ""
    description: str = ""


_BASE_WIDGET_PROPS = [
    PropertyDef("mX", PropType.INT, 0, "X坐标", category="geometry", tooltip="控件左上角的X坐标位置"),
    PropertyDef("mY", PropType.INT, 0, "Y坐标", category="geometry", tooltip="控件左上角的Y坐标位置"),
    PropertyDef("mWidth", PropType.INT, 100, "宽度", category="geometry", tooltip="控件的宽度（像素）"),
    PropertyDef("mHeight", PropType.INT, 30, "高度", category="geometry", tooltip="控件的高度（像素）"),
    PropertyDef("mVisible", PropType.BOOL, True, "可见", category="appearance", tooltip="控件是否可见"),
    PropertyDef("mDisabled", PropType.BOOL, False, "禁用", category="appearance", tooltip="控件是否被禁用（不可交互）"),
    PropertyDef("mHasTransparencies", PropType.BOOL, False, "透明区域", category="appearance", tooltip="控件是否包含透明像素"),
    PropertyDef("mClip", PropType.BOOL, False, "裁剪", category="appearance", tooltip="是否裁剪超出控件范围的子控件"),
    PropertyDef("mHasAlpha", PropType.BOOL, False, "Alpha通道", category="appearance", tooltip="是否启用Alpha混合"),
    PropertyDef("mDoFinger", PropType.BOOL, False, "手指光标", category="appearance", tooltip="鼠标悬停时是否显示手指光标"),
    PropertyDef("mWantsFocus", PropType.BOOL, False, "请求焦点", category="behavior", tooltip="控件是否接受键盘焦点"),
]

_BUTTON_COLOR_ENUMS = [
    "COLOR_LABEL", "COLOR_LABEL_HILITE", "COLOR_DARK_OUTLINE",
    "COLOR_LIGHT_OUTLINE", "COLOR_MEDIUM_OUTLINE", "COLOR_BKG"
]

_BUTTON_MODE_ENUMS = [
    "BUTTONS_NONE", "BUTTONS_YES_NO", "BUTTONS_OK_CANCEL", "BUTTONS_FOOTER"
]

_JUSTIFY_ENUMS = ["LEFT", "CENTER", "RIGHT"]


def _build_component_defs() -> Dict[str, ComponentDef]:
    defs = {}

    defs["Widget"] = ComponentDef(
        class_name="Widget",
        parent_class="WidgetContainer",
        display_name="基础控件",
        category="base",
        properties=list(_BASE_WIDGET_PROPS),
        is_container=True,
        icon_name="widget",
        description="基础Widget控件"
    )

    defs["ButtonWidget"] = ComponentDef(
        class_name="ButtonWidget",
        parent_class="Widget",
        display_name="按钮",
        category="basic",
        properties=_BASE_WIDGET_PROPS + [
            PropertyDef("mId", PropType.INT, 0, "ID", category="identity", tooltip="按钮的唯一标识符"),
            PropertyDef("mLabel", PropType.STRING, "", "标签文本", category="content", tooltip="按钮上显示的文本"),
            PropertyDef("mLabelJustify", PropType.ENUM, "CENTER", "文本对齐", enum_values=_JUSTIFY_ENUMS, category="content", tooltip="标签文本的对齐方式"),
            PropertyDef("mFont", PropType.FONT, "FONT_DWARVENTODCRAFT12", "字体", category="content", tooltip="标签文本使用的字体"),
            PropertyDef("mButtonImage", PropType.IMAGE, "", "正常图片", category="images", tooltip="按钮正常状态的图片"),
            PropertyDef("mOverImage", PropType.IMAGE, "", "悬停图片", category="images", tooltip="鼠标悬停时的图片"),
            PropertyDef("mDownImage", PropType.IMAGE, "", "按下图片", category="images", tooltip="鼠标按下时的图片"),
            PropertyDef("mDisabledImage", PropType.IMAGE, "", "禁用图片", category="images", tooltip="按钮禁用时的图片"),
            PropertyDef("mNormalRect", PropType.RECT, "0,0,0,0", "正常区域", category="images", tooltip="正常状态图片的裁剪区域(x,y,w,h)"),
            PropertyDef("mOverRect", PropType.RECT, "0,0,0,0", "悬停区域", category="images", tooltip="悬停状态图片的裁剪区域(x,y,w,h)"),
            PropertyDef("mDownRect", PropType.RECT, "0,0,0,0", "按下区域", category="images", tooltip="按下状态图片的裁剪区域(x,y,w,h)"),
            PropertyDef("mDisabledRect", PropType.RECT, "0,0,0,0", "禁用区域", category="images", tooltip="禁用状态图片的裁剪区域(x,y,w,h)"),
            PropertyDef("mInverted", PropType.BOOL, False, "反转效果", category="behavior", tooltip="是否反转按钮效果"),
            PropertyDef("mBtnNoDraw", PropType.BOOL, False, "不绘制按钮", category="behavior", tooltip="是否跳过按钮本身的绘制"),
            PropertyDef("mFrameNoDraw", PropType.BOOL, False, "不绘制边框", category="behavior", tooltip="是否跳过按钮边框的绘制"),
            PropertyDef("mOverAlpha", PropType.FLOAT, 0.0, "悬停透明度", category="animation", tooltip="悬停效果的透明度"),
            PropertyDef("mOverAlphaSpeed", PropType.FLOAT, 0.05, "透明度速度", category="animation", tooltip="悬停透明度变化速度"),
        ],
        icon_name="button",
        description="可点击的按钮控件"
    )

    defs["DialogButton"] = ComponentDef(
        class_name="DialogButton",
        parent_class="ButtonWidget",
        display_name="对话框按钮",
        category="basic",
        properties=_BASE_WIDGET_PROPS + [
            PropertyDef("mId", PropType.INT, 0, "ID", category="identity", tooltip="按钮的唯一标识符"),
            PropertyDef("mLabel", PropType.STRING, "", "标签文本", category="content", tooltip="按钮上显示的文本"),
            PropertyDef("mComponentImage", PropType.IMAGE, "", "组件图片", category="images", tooltip="对话框按钮的组件图片"),
            PropertyDef("mStretchImage", PropType.BOOL, True, "拉伸图片", category="images", tooltip="是否拉伸图片以填充按钮区域"),
            PropertyDef("mTranslateX", PropType.INT, 0, "绘制偏移X", category="geometry", tooltip="绘制时的X偏移量"),
            PropertyDef("mTranslateY", PropType.INT, 0, "绘制偏移Y", category="geometry", tooltip="绘制时的Y偏移量"),
            PropertyDef("mTextOffsetX", PropType.INT, 0, "文本偏移X", category="geometry", tooltip="文本的X偏移量"),
            PropertyDef("mTextOffsetY", PropType.INT, 0, "文本偏移Y", category="geometry", tooltip="文本的Y偏移量"),
        ],
        icon_name="dialog_button",
        description="对话框中使用的按钮"
    )

    defs["HyperlinkWidget"] = ComponentDef(
        class_name="HyperlinkWidget",
        parent_class="ButtonWidget",
        display_name="超链接",
        category="basic",
        properties=_BASE_WIDGET_PROPS + [
            PropertyDef("mId", PropType.INT, 0, "ID", category="identity", tooltip="超链接的唯一标识符"),
            PropertyDef("mLabel", PropType.STRING, "", "标签文本", category="content", tooltip="超链接显示的文本"),
            PropertyDef("mColor", PropType.COLOR, "255,255,255", "正常颜色", category="appearance", tooltip="正常状态下的文本颜色"),
            PropertyDef("mOverColor", PropType.COLOR, "255,255,0", "悬停颜色", category="appearance", tooltip="鼠标悬停时的文本颜色"),
            PropertyDef("mUnderlineSize", PropType.INT, 1, "下划线粗细", category="appearance", tooltip="下划线的像素粗细"),
            PropertyDef("mUnderlineOffset", PropType.INT, 0, "下划线偏移", category="appearance", tooltip="下划线的Y偏移量"),
        ],
        icon_name="hyperlink",
        description="可点击的超链接文本"
    )

    defs["EditWidget"] = ComponentDef(
        class_name="EditWidget",
        parent_class="Widget",
        display_name="输入框",
        category="basic",
        properties=_BASE_WIDGET_PROPS + [
            PropertyDef("mId", PropType.INT, 0, "ID", category="identity", tooltip="输入框的唯一标识符"),
            PropertyDef("mString", PropType.STRING, "", "文本内容", category="content", tooltip="输入框中的文本"),
            PropertyDef("mFont", PropType.FONT, "FONT_DWARVENTODCRAFT12", "字体", category="content", tooltip="文本使用的字体"),
            PropertyDef("mMaxChars", PropType.INT, 0, "最大字符数", category="behavior", tooltip="允许输入的最大字符数(0=无限制)"),
            PropertyDef("mMaxPixels", PropType.INT, 0, "最大像素宽", category="behavior", tooltip="文本的最大像素宽度(0=无限制)"),
            PropertyDef("mPasswordChar", PropType.STRING, "", "密码字符", category="behavior", tooltip="密码模式下显示的替代字符"),
        ],
        icon_name="edit",
        description="文本输入框"
    )

    defs["TextWidget"] = ComponentDef(
        class_name="TextWidget",
        parent_class="Widget",
        display_name="文本视图(Sexy)",
        category="basic",
        properties=_BASE_WIDGET_PROPS + [
            PropertyDef("mFont", PropType.FONT, "FONT_DWARVENTODCRAFT12", "字体", category="content", tooltip="文本使用的字体"),
            PropertyDef("mMaxLines", PropType.INT, 0, "最大行数", category="content", tooltip="显示的最大行数(0=无限制)"),
            PropertyDef("mStickToBottom", PropType.BOOL, False, "自动滚底", category="behavior", tooltip="是否自动滚动到最底部"),
            PropertyDef("mLines", PropType.STRING, "", "文本内容", category="content", tooltip="多行文本，用\\n分隔"),
        ],
        icon_name="text",
        description="多行文本显示控件(Sexy框架)"
    )

    defs["ListWidget"] = ComponentDef(
        class_name="ListWidget",
        parent_class="Widget",
        display_name="列表框",
        category="basic",
        properties=_BASE_WIDGET_PROPS + [
            PropertyDef("mId", PropType.INT, 0, "ID", category="identity", tooltip="列表框的唯一标识符"),
            PropertyDef("mFont", PropType.FONT, "FONT_DWARVENTODCRAFT12", "字体", category="content", tooltip="列表项使用的字体"),
            PropertyDef("mJustify", PropType.ENUM, "LEFT", "对齐方式", enum_values=_JUSTIFY_ENUMS, category="content", tooltip="列表项文本的对齐方式"),
            PropertyDef("mItemHeight", PropType.INT, 20, "项高度", category="geometry", tooltip="每个列表项的像素高度"),
            PropertyDef("mHiliteIdx", PropType.INT, -1, "高亮索引", category="behavior", tooltip="当前高亮项的索引(-1=无)"),
            PropertyDef("mSelectIdx", PropType.INT, -1, "选中索引", category="behavior", tooltip="当前选中项的索引(-1=无)"),
            PropertyDef("mLines", PropType.STRING, "", "列表项", category="content", tooltip="列表项，用\\n分隔"),
        ],
        icon_name="list",
        description="可滚动的列表控件"
    )

    defs["ScrollbarWidget"] = ComponentDef(
        class_name="ScrollbarWidget",
        parent_class="Widget",
        display_name="滚动条",
        category="basic",
        properties=_BASE_WIDGET_PROPS + [
            PropertyDef("mId", PropType.INT, 0, "ID", category="identity", tooltip="滚动条的唯一标识符"),
            PropertyDef("mValue", PropType.FLOAT, 0.0, "当前值", category="value", tooltip="滚动条当前位置值"),
            PropertyDef("mMaxValue", PropType.FLOAT, 100.0, "最大值", category="value", tooltip="滚动条的最大值"),
            PropertyDef("mPageSize", PropType.FLOAT, 10.0, "页大小", category="value", tooltip="每页显示的范围大小"),
            PropertyDef("mHorizontal", PropType.BOOL, False, "水平方向", category="geometry", tooltip="是否为水平滚动条"),
            PropertyDef("mInvisIfNoScroll", PropType.BOOL, False, "无滚动时隐藏", category="appearance", tooltip="当内容不需要滚动时是否隐藏"),
        ],
        icon_name="scrollbar",
        description="内容滚动条"
    )

    defs["Checkbox"] = ComponentDef(
        class_name="Checkbox",
        parent_class="Widget",
        display_name="复选框",
        category="basic",
        properties=_BASE_WIDGET_PROPS + [
            PropertyDef("mId", PropType.INT, 0, "ID", category="identity", tooltip="复选框的唯一标识符"),
            PropertyDef("mChecked", PropType.BOOL, False, "已选中", category="value", tooltip="复选框是否被选中"),
            PropertyDef("mUncheckedImage", PropType.IMAGE, "", "未选中图片", category="images", tooltip="未选中状态的图片"),
            PropertyDef("mCheckedImage", PropType.IMAGE, "", "选中图片", category="images", tooltip="选中状态的图片"),
            PropertyDef("mUncheckedRect", PropType.RECT, "0,0,0,0", "未选中区域", category="images", tooltip="未选中图片的裁剪区域"),
            PropertyDef("mCheckedRect", PropType.RECT, "0,0,0,0", "选中区域", category="images", tooltip="选中图片的裁剪区域"),
            PropertyDef("mOutlineColor", PropType.COLOR, "255,255,255", "边框颜色", category="appearance", tooltip="无图片时的边框颜色"),
            PropertyDef("mBkgColor", PropType.COLOR, "0,0,0", "背景颜色", category="appearance", tooltip="无图片时的背景颜色"),
            PropertyDef("mCheckColor", PropType.COLOR, "255,255,0", "勾选颜色", category="appearance", tooltip="勾选标记的颜色"),
        ],
        icon_name="checkbox",
        description="复选框控件"
    )

    defs["Slider"] = ComponentDef(
        class_name="Slider",
        parent_class="Widget",
        display_name="滑块",
        category="basic",
        properties=_BASE_WIDGET_PROPS + [
            PropertyDef("mId", PropType.INT, 0, "ID", category="identity", tooltip="滑块的唯一标识符"),
            PropertyDef("mVal", PropType.FLOAT, 0.5, "当前值", category="value", tooltip="滑块当前值(0.0~1.0)"),
            PropertyDef("mTrackImage", PropType.IMAGE, "", "轨道图片", category="images", tooltip="滑块轨道的图片"),
            PropertyDef("mThumbImage", PropType.IMAGE, "", "滑块图片", category="images", tooltip="滑块手柄的图片"),
        ],
        icon_name="slider",
        description="滑块控件，用于调整数值"
    )

    defs["Dialog"] = ComponentDef(
        class_name="Dialog",
        parent_class="Widget",
        display_name="对话框",
        category="container",
        properties=_BASE_WIDGET_PROPS + [
            PropertyDef("mId", PropType.INT, 0, "ID", category="identity", tooltip="对话框的唯一标识符"),
            PropertyDef("mDialogHeader", PropType.STRING, "", "标题", category="content", tooltip="对话框标题文本"),
            PropertyDef("mDialogFooter", PropType.STRING, "", "页脚", category="content", tooltip="对话框页脚文本"),
            PropertyDef("mDialogLines", PropType.STRING, "", "内容文本", category="content", tooltip="对话框正文内容"),
            PropertyDef("mComponentImage", PropType.IMAGE, "", "组件图片", category="images", tooltip="对话框背景图片"),
            PropertyDef("mStretchImage", PropType.BOOL, True, "拉伸图片", category="images", tooltip="是否拉伸背景图片以填充对话框区域"),
            PropertyDef("mButtonMode", PropType.ENUM, "BUTTONS_NONE", "按钮模式", enum_values=_BUTTON_MODE_ENUMS, category="behavior", tooltip="对话框底部按钮的配置模式"),
            PropertyDef("mHeaderFont", PropType.FONT, "", "标题字体", category="content", tooltip="标题文本使用的字体"),
            PropertyDef("mLinesFont", PropType.FONT, "", "内容字体", category="content", tooltip="正文内容使用的字体"),
            PropertyDef("mIsModal", PropType.BOOL, True, "模态", category="behavior", tooltip="是否为模态对话框"),
        ],
        is_container=True,
        icon_name="dialog",
        description="带按钮的对话框窗口"
    )

    defs["LawnDialog"] = ComponentDef(
        class_name="LawnDialog",
        parent_class="Dialog",
        display_name="PVZ对话框",
        category="pvz",
        is_pvz=True,
        properties=_BASE_WIDGET_PROPS + [
            PropertyDef("mId", PropType.INT, 0, "ID", category="identity", tooltip="对话框的唯一标识符"),
            PropertyDef("mDialogHeader", PropType.STRING, "", "标题", category="content", tooltip="对话框标题文本"),
            PropertyDef("mDialogLines", PropType.STRING, "", "内容文本", category="content", tooltip="对话框正文内容"),
            PropertyDef("mComponentImage", PropType.IMAGE, "", "组件图片", category="images", tooltip="对话框背景图片"),
            PropertyDef("mStretchImage", PropType.BOOL, True, "拉伸图片", category="images", tooltip="是否拉伸背景图片以填充对话框区域"),
            PropertyDef("mButtonMode", PropType.ENUM, "BUTTONS_NONE", "按钮模式", enum_values=_BUTTON_MODE_ENUMS, category="behavior", tooltip="对话框底部按钮的配置模式"),
            PropertyDef("mDrawStandardBack", PropType.BOOL, True, "标准背景", category="appearance", tooltip="是否绘制PVZ标准背景"),
            PropertyDef("mTallBottom", PropType.BOOL, False, "高底部", category="geometry", tooltip="是否使用较高的底部区域"),
            PropertyDef("mVerticalCenterText", PropType.BOOL, False, "垂直居中文本", category="appearance", tooltip="文本是否垂直居中"),
            PropertyDef("mButtonDelay", PropType.INT, 0, "按钮延迟", category="behavior", tooltip="按钮可点击前的延迟帧数"),
        ],
        is_container=True,
        icon_name="lawn_dialog",
        description="PVZ风格的对话框"
    )

    defs["LawnStoneButton"] = ComponentDef(
        class_name="LawnStoneButton",
        parent_class="DialogButton",
        display_name="石质按钮",
        category="pvz",
        is_pvz=True,
        properties=_BASE_WIDGET_PROPS + [
            PropertyDef("mId", PropType.INT, 0, "ID", category="identity", tooltip="按钮的唯一标识符"),
            PropertyDef("mLabel", PropType.STRING, "", "标签文本", category="content", tooltip="按钮上显示的文本"),
        ],
        icon_name="stone_button",
        description="PVZ石质风格按钮"
    )

    defs["NewLawnButton"] = ComponentDef(
        class_name="NewLawnButton",
        parent_class="DialogButton",
        display_name="新风格按钮",
        category="pvz",
        is_pvz=True,
        properties=_BASE_WIDGET_PROPS + [
            PropertyDef("mId", PropType.INT, 0, "ID", category="identity", tooltip="按钮的唯一标识符"),
            PropertyDef("mLabel", PropType.STRING, "", "标签文本", category="content", tooltip="按钮上显示的文本"),
            PropertyDef("mFont", PropType.FONT, "FONT_DWARVENTODCRAFT12", "字体", category="content", tooltip="正常状态使用的字体"),
            PropertyDef("mHiliteFont", PropType.FONT, "", "高亮字体", category="content", tooltip="高亮状态使用的字体"),
            PropertyDef("mUniformImage", PropType.IMAGE, "IMAGE_BUTTON_MIDDLE", "统一图片", category="images", tooltip="设置后自动应用到正常/悬停/按下图片"),
            PropertyDef("mButtonImage", PropType.IMAGE, "", "正常图片", category="images", tooltip="按钮正常状态的图片(留空使用统一图片)"),
            PropertyDef("mOverImage", PropType.IMAGE, "", "悬停图片", category="images", tooltip="鼠标悬停时的图片(留空使用统一图片)"),
            PropertyDef("mDownImage", PropType.IMAGE, "", "按下图片", category="images", tooltip="鼠标按下时的图片(留空使用统一图片)"),
            PropertyDef("mTextDownOffsetX", PropType.INT, 0, "按下文本偏移X", category="geometry", tooltip="按下时文本的X偏移"),
            PropertyDef("mTextDownOffsetY", PropType.INT, 0, "按下文本偏移Y", category="geometry", tooltip="按下时文本的Y偏移"),
            PropertyDef("mButtonOffsetX", PropType.INT, 0, "按钮偏移X", category="geometry", tooltip="按钮的X偏移"),
            PropertyDef("mButtonOffsetY", PropType.INT, 0, "按钮偏移Y", category="geometry", tooltip="按钮的Y偏移"),
            PropertyDef("mUsePolygonShape", PropType.BOOL, False, "多边形碰撞", category="behavior", tooltip="是否使用多边形碰撞检测"),
        ],
        icon_name="new_lawn_button",
        description="PVZ新风格按钮"
    )

    defs["LawnEditWidget"] = ComponentDef(
        class_name="LawnEditWidget",
        parent_class="EditWidget",
        display_name="PVZ输入框",
        category="pvz",
        is_pvz=True,
        properties=_BASE_WIDGET_PROPS + [
            PropertyDef("mId", PropType.INT, 0, "ID", category="identity", tooltip="输入框的唯一标识符"),
            PropertyDef("mString", PropType.STRING, "", "文本内容", category="content", tooltip="输入框中的文本"),
            PropertyDef("mFont", PropType.FONT, "FONT_DWARVENTODCRAFT12", "字体", category="content", tooltip="文本使用的字体"),
            PropertyDef("mTitle", PropType.STRING, "", "标题", category="content", tooltip="输入框标题"),
            PropertyDef("mDescription", PropType.STRING, "", "描述", category="content", tooltip="输入框描述"),
        ],
        icon_name="lawn_edit",
        description="PVZ风格的文本输入框"
    )

    defs["ScrollbuttonWidget"] = ComponentDef(
        class_name="ScrollbuttonWidget",
        parent_class="ButtonWidget",
        display_name="滚动按钮",
        category="basic",
        properties=_BASE_WIDGET_PROPS + [
            PropertyDef("mHorizontal", PropType.BOOL, False, "水平方向", category="geometry", tooltip="是否为水平方向"),
            PropertyDef("mType", PropType.ENUM, "1", "方向", enum_values=["1=上", "2=下", "3=左", "4=右"], category="behavior", tooltip="滚动箭头的方向"),
        ],
        icon_name="scroll_button",
        description="滚动箭头按钮"
    )

    defs["GameButton"] = ComponentDef(
        class_name="GameButton",
        parent_class="",
        display_name="游戏按钮",
        category="pvz",
        is_pvz=True,
        properties=[
            PropertyDef("mX", PropType.INT, 0, "X坐标", category="geometry", tooltip="按钮左上角的X坐标"),
            PropertyDef("mY", PropType.INT, 0, "Y坐标", category="geometry", tooltip="按钮左上角的Y坐标"),
            PropertyDef("mWidth", PropType.INT, 100, "宽度", category="geometry", tooltip="按钮的宽度"),
            PropertyDef("mHeight", PropType.INT, 30, "高度", category="geometry", tooltip="按钮的高度"),
            PropertyDef("mId", PropType.INT, 0, "ID", category="identity", tooltip="按钮的唯一标识符"),
            PropertyDef("mLabel", PropType.STRING, "", "标签文本", category="content", tooltip="按钮上显示的文本"),
            PropertyDef("mFont", PropType.FONT, "FONT_DWARVENTODCRAFT12", "字体", category="content", tooltip="文本使用的字体"),
            PropertyDef("mButtonImage", PropType.IMAGE, "", "正常图片", category="images", tooltip="按钮正常状态的图片"),
            PropertyDef("mOverImage", PropType.IMAGE, "", "悬停图片", category="images", tooltip="鼠标悬停时的图片"),
            PropertyDef("mDownImage", PropType.IMAGE, "", "按下图片", category="images", tooltip="鼠标按下时的图片"),
            PropertyDef("mDisabledImage", PropType.IMAGE, "", "禁用图片", category="images", tooltip="按钮禁用时的图片"),
            PropertyDef("mOverOverlayImage", PropType.IMAGE, "", "悬停叠加图", category="images", tooltip="悬停时的叠加图片"),
            PropertyDef("mDrawStoneButton", PropType.BOOL, False, "石质按钮", category="appearance", tooltip="是否绘制为石质按钮风格"),
            PropertyDef("mDisabled", PropType.BOOL, False, "禁用", category="behavior", tooltip="按钮是否被禁用"),
        ],
        icon_name="game_button",
        description="PVZ游戏按钮(非Widget辅助类)"
    )

    return defs


class ComponentRegistry:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._defs = _build_component_defs()

    def get(self, class_name: str) -> Optional[ComponentDef]:
        return self._defs.get(class_name)

    def all_defs(self) -> Dict[str, ComponentDef]:
        return dict(self._defs)

    def categories(self) -> Dict[str, List[ComponentDef]]:
        cats = {}
        for d in self._defs.values():
            cats.setdefault(d.category, []).append(d)
        return cats

    def class_names(self) -> List[str]:
        return list(self._defs.keys())
