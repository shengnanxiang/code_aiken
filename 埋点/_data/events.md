# AiKen 埋点事件清单

字段：事件名 | 模块/页面 | 元素 | 类型 | 上报时机 | 携带信息

## 相机页
| 事件名 | 元素 | 类型 | 时机 | 携带信息
|---|---|---|---|---|
| camera_page_view | 相机页 | page_view | 页面曝光 | device_sn |
| camera_connect_status_view | 连接状态条 | view | 曝光 | connect_status, battery |
| current_style_click | 当前风格卡 | click | 点击 | style_id, style_name |
| take_out_btn_click | 提前取出按钮 | click | 点击 | remaining, shot_cnt |

## 提前取出弹窗
| 事件名 | 元素 | 类型 | 时机 | 携带信息
|---|---|---|---|---|
| take_out_dialog_view | 弹窗 | view | 曝光 | remaining |
| take_out_confirm_click | 取出 | click | 点击 | remaining |
| take_out_cancel_click | 取消 | click | 点击 | - |

## 冲印方式弹窗（取出后）
| 事件名 | 元素 | 类型 | 时机 | 携带信息
|---|---|---|---|---|
| print_mode_dialog_view | 弹窗 | view | 曝光 | - |
| print_mode_select_click | 即时/经典冲印 | click | 选中 | print_mode |
| print_start_click | 开始冲印 | click | 点击 | print_mode |
| transfer_start | 传输开始 | - | 开始 | shot_cnt |
| transfer_end | 传输结束 | - | 结束 | result, duration |

## 风格列表
| 事件名 | 元素 | 类型 | 时机 | 携带信息
|---|---|---|---|---|
| style_list_view | 风格列表 | page_view | 曝光 | style_cnt |
| style_filter_click | 筛选标签 | click | 点击 | filter_type |
| style_card_view | 风格卡片 | view | 曝光 | style_id, select_status |
| style_detail_click | 查看详情 | click | 点击 | style_id |
| unlock_style_click | 解锁新风格 | click | 点击 | - |

## 风格详情
| 事件名 | 元素 | 类型 | 时机 | 携带信息
|---|---|---|---|---|
| style_detail_view | 风格详情 | page_view | 曝光 | style_id |
| image_setting_click | 颗粒/边框/漏光 | click | 选中 | setting_type, setting_val |
| use_style_click | 选用此风格 | click | 点击 | style_id |

## 相机设置
| 事件名 | 元素 | 类型 | 时机 | 携带信息
|---|---|---|---|---|
| camera_setting_view | 相机设置 | page_view | 曝光 | - |
| date_stamp_toggle | 日期戳开关 | click | 切换 | status |
| delete_device_click | 删除设备 | click | 点击 | - |
| print_mode_setting_click | 冲印方式 | click | 点击 | cur_value |

## 冲印方式设置弹窗
| 事件名 | 元素 | 类型 | 时机 | 携带信息
|---|---|---|---|---|
| print_mode_setting_view | 弹窗 | view | 曝光 | cur_value |
| print_mode_setting_select | 每次询问/即时/经典 | click | 选中 | print_mode |
| print_mode_setting_save | 完成 | click | 点击 | print_mode |

## 暗房-胶卷列表
| 事件名 | 元素 | 类型 | 时机 | 携带信息
|---|---|---|---|---|
| darkroom_list_view | 暗房列表 | page_view | 曝光 | roll_cnt |
| darkroom_filter_click | 筛选标签 | click | 点击 | filter_type |
| roll_card_view | 胶卷卡片 | view | 曝光 | roll_id, print_status |
| roll_card_click | 胶卷卡片 | click | 点击 | roll_id |

## 底片浏览
| 事件名 | 元素 | 类型 | 时机 | 携带信息
|---|---|---|---|---|
| film_strip_view | 底片浏览 | page_view | 曝光 | roll_id, shot_cnt |
| film_swipe | 胶片带滑动 | - | 停止 | photo_index |
| save_all_click | 保存全部 | click | 点击 | shot_cnt |
| share_click | 分享 | click | 点击 | shot_cnt |
| photo_click | 单张照片 | click | 点击 | photo_idx |
| select_click | 选择 | click | 点击 | - |

## 大图浏览
| 事件名 | 元素 | 类型 | 时机 | 携带信息
|---|---|---|---|---|
| photo_view_view | 大图浏览 | page_view | 曝光 | roll_id, photo_idx |
| photo_switch | 左右切换 | - | 切换 | photo_idx |
| set_cover_click | 设为封面 | click | 点击 | photo_idx |
| photo_save_click | 保存 | click | 点击 | photo_idx |

## 拼贴分享
| 事件名 | 元素 | 类型 | 时机 | 携带信息
|---|---|---|---|---|
| collage_view | 拼贴分享 | page_view | 曝光 | roll_id |
| collage_regen_click | 重新生成 | click | 点击 | photo_cnt |
| collage_save_click | 保存 | click | 点击 | photo_cnt |
| collage_share_click | 分享 | click | 点击 | photo_cnt |
