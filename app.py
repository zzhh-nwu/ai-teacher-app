# app.py - 课程内容辅助生成智能体
import streamlit as st
import json
import time
import pandas as pd
import glob
import matplotlib.pyplot as plt 
import numpy as np
import streamlit as st
from PIL import Image
from utils import generate_course_outline, generate_lecture_content, recommend_resources
from utils import generate_mock_course_outline, generate_mock_lecture_content, recommend_mock_resources
from utils import update_lecture_content, save_survey_result, load_survey_results
from utils import save_lecture_to_word, save_lecture_to_ppt  
import re  # 新增导入

# 在导入后立即定义辅助函数
def _format_resource_item(item):
    """格式化资源项目为HTML显示"""
    if not isinstance(item, dict):
        return str(item)
    
    formatted_text = ""
    for key, value in item.items():
        if key == "书名" or key == "视频标题" or key == "工具名称" or key == "案例名称":
            formatted_text += f"<strong>{value}</strong><br>"
        elif key == "作者" or key == "主讲人/机构":
            formatted_text += f"<em>{value}</em><br>"
        elif key == "链接" and value:
            formatted_text += f'<a href="{value}" target="_blank">访问链接</a><br>'
        elif value:
            formatted_text += f"{key}: {value}<br>"
    
    return formatted_text

# 将函数赋值给st对象
st._format_resource_item = _format_resource_item

# 设置页面标题和图标
st.set_page_config(
    page_title="小优 - AI课程设计助手",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 更现代化的设计
st.markdown("""
<style>
    /* 全局样式 */
    .stApp {
        background-color: #f8f9fa;
    }
     /* 新增：标题动画效果 */
    @keyframes titleGlow {
        0% {
            text-shadow: 0 0 10px rgba(26, 115, 232, 0.5), 0 0 20px rgba(26, 115, 232, 0.3);
        }
        50% {
            text-shadow: 0 0 20px rgba(26, 115, 232, 0.8), 0 0 30px rgba(26, 115, 232, 0.5), 0 0 40px rgba(26, 115, 232, 0.3);
        }
        100% {
            text-shadow: 0 0 10px rgba(26, 115, 232, 0.5), 0 0 20px rgba(26, 115, 232, 0.3);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes float {
        0% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-8px);
        }
        100% {
            transform: translateY(0px);
        }
    }
    .main-header {
        font-size: 2.5rem;
        color: #1a73e8;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1a73e8;
        border-bottom: 2px solid #1a73e8;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
        font-weight: 600;
    }
    .highlight {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #2196F3;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .success-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .warning-box {
        background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #FFC107;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .error-box {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #F44336;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stButton button {
        background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        transition: all 0.3s;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .chat-container {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .user-message {
        background-color: #e3f2fd;
        padding: 12px 16px;
        border-radius: 18px 18px 0 18px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
        text-align: right;
    }
    .assistant-message {
        background-color: #f1f3f4;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 0;
        margin: 8px 0;
        max-width: 80%;
    }
    .step-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 4px solid #1a73e8;
    }
    .resource-card {
        background-color: #FFF;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 12px;
        transition: all 0.2s;
    }
    .resource-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    /* 引导流程样式 */
    .welcome-container {
        border-radius: 16px;
        margin-bottom: 30px;
        min-height: 300px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
    }
    /* 修改：右下角按钮样式 */
    .fixed-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 999;
    }
    .fixed-button button {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%) !important;
        color: white !important;
        border: none !important;
        padding: 14px 28px !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
        cursor: pointer !important;
        transition: all 0.3s !important;
        font-size: 16px !important;
    }
    .fixed-button button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.3) !important;
    }
  
    /* 新增：AI助手消息字体放大 */
    .assistant-intro {
        font-size: 20px !important;
        font-weight: bold;
    }
    /* 修改：加粗修改内容 */
    .modified-content {
        font-weight: bold;
        background-color: #fff3cd;
        padding: 2px 4px;
        border-radius: 3px;
        border: 1px solid #ffeaa7;
    }
    /* 新增：提交问卷按钮样式 */
    .submit-button {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%) !important;
        color: white !important;
        border: none !important;
        padding: 14px 28px !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
        cursor: pointer !important;
        transition: all 0.3s !important;
        font-size: 16px !important;
        width: 100% !important;
        margin-top: 20px !important;
    }
    .submit-button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.3) !important;
    }
    
    .upload-area {
        border: 2px dashed #1a73e8;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        background-color: #f8f9fa;
        margin-bottom: 20px;
    }
    .upload-area:hover {
        background-color: #e3f2fd;
    }        
    
</style>
""", unsafe_allow_html=True)

# 初始化session状态变量 - 修复：确保讲义内容持久化
if "course_outline" not in st.session_state:
    st.session_state.course_outline = None
    
if "resources" not in st.session_state:
    st.session_state.resources = None
    
if "generated_lectures" not in st.session_state:
    st.session_state.generated_lectures = {}
    
if "api_error" not in st.session_state:
    st.session_state.api_error = None
    
if "use_fallback" not in st.session_state:
    st.session_state.use_fallback = False

# 新增：多轮对话状态
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = {}

# 新增：引导流程状态
if "current_step" not in st.session_state:
    st.session_state.current_step = "welcome"  # welcome, course_info, objectives, hours, complete

# 新增：课程信息收集
if "course_info" not in st.session_state:
    st.session_state.course_info = {
        "name": "",
        "education_stage": "小学",  # 新增默认值
        "generation_language": "中文",  # 新增：生成语言默认值
        "objectives": "",
        "hours": 32
    }

# 新增：满意度调查状态
if "current_page" not in st.session_state:
    st.session_state.current_page = "main"  # 可以是 "main"、"survey" 或 "results"

# 新增：API状态监控
if "api_status" not in st.session_state:
    st.session_state.api_status = {
        "last_success": None,
        "error_count": 0,
        "last_error": None
    }

# 新增：标签页状态
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "课程大纲与讲义"

# 新增：PPT模板选择状态
if "show_template_selection" not in st.session_state:
    st.session_state.show_template_selection = False
if "selected_template" not in st.session_state:
    st.session_state.selected_template = None
if "current_lecture_for_ppt" not in st.session_state:
    st.session_state.current_lecture_for_ppt = None
    
# 新增：修复讲义持久化的关键状态
if "lecture_generation_status" not in st.session_state:
    st.session_state.lecture_generation_status = {}  # 记录每个章节的生成状态

# 新增：政策文件状态
if "policy_file" not in st.session_state:
    st.session_state.policy_file = None
if "policy_content" not in st.session_state:
    st.session_state.policy_content = ""
if "policy_requirements" not in st.session_state:
    st.session_state.policy_requirements = ""

# 显示满意度调查
def show_satisfaction_survey():
    """显示满意度调查页面"""
    st.markdown('<h1 class="main-header">📝 教师满意度调查</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="highlight">
    尊敬的老师，您好！为了持续优化我们的助教智能体，为您提供更高效、更贴心的教学辅助服务，我们诚挚地邀请您花费3-5分钟时间填写此份问卷。您的所有反馈都将被严格保密，并仅用于产品改进。感谢您的支持！
    </div>
    """, unsafe_allow_html=True)
    
    # 使用表单收集所有答案
    with st.form("satisfaction_survey"):
        # 第一部分：基本情况
        st.markdown("### 第一部分：基本情况")
        
        # 问题1 - 添加序号显示
        st.write("1. 您目前主要任教的学段是？")
        q1 = st.radio(
            "",  # 标签设为空，因为上面已经显示了问题
            ["A. 小学", "B. 初中", "C. 高中", "D. 高职/中职", "E. 大学本科及以上", "F. 其他"],
            index=None,
            key="q1_radio"
        )
        
        if q1 == "F. 其他":
            q1_other = st.text_input("请简要说明:", key="q1_other")
        else:
            q1_other = ""
            
        # 问题2 - 添加序号显示
        st.write("2. 您任教的主要学科专业领域是？")
        q2 = st.radio(
            "",
            ["A. 语文/文学/外语类", "B. 数学/科学/工程类", "C. 历史/地理/政治等社科类", 
             "D. 物理/化学/生物等理科类", "E. 艺术/音乐/体育类", "F. 计算机/信息技术类", "G. 其他"],
            index=None,
            key="q2_radio"
        )
        
        if q2 == "G. 其他":
            q2_other = st.text_input("请简要说明:", key="q2_other")
        else:
            q2_other = ""
        
        # 第二部分：使用体验与满意度
        st.markdown("### 第二部分：使用体验与满意度")
        
        # 问题3 - 添加序号显示
        st.write("3. 您使用本助教智能体的频率是？")
        q3 = st.radio(
            "",
            ["A. 每天多次", "B. 每天一次", "C. 每周几次", "D. 偶尔使用（每月几次）", "E. 这是第一次使用"],
            index=None,
            key="q3_radio"
        )
        
        # 问题4 - 添加序号显示
        st.write("4. 总体而言，您对本助教智能体的满意度如何？")
        q4 = st.radio(
            "",
            ["A. 非常满意", "B. 比较满意", "C. 一般", "D. 不太满意", "E. 非常不满意"],
            index=None,
            key="q4_radio"
        )
        
        # 问题5 - 添加序号显示
        st.write("5. 您认为智能体生成的大纲/讲义内容质量如何？")
        q5 = st.radio(
            "",
            ["A. 专业准确，结构清晰，可直接使用", "B. 内容良好，只需少量修改即可使用", 
             "C. 内容一般，需要较多修改和补充", "D. 内容存在较多错误，参考价值有限"],
            index=None,
            key="q5_radio"
        )
        
        # 问题6 - 添加序号显示
        st.write("6. 您认为智能体生成的PPT内容与美观度如何？")
        q6 = st.radio(
            "",
            ["A. 内容精炼，设计美观，非常满意", "B. 内容不错，但设计模板较为普通", 
             "C. 内容需要调整，设计也需要优化", "D. 内容和设计都达不到使用标准"],
            index=None,
            key="q6_radio"
        )
        
        # 问题7 - 添加序号显示
        st.write("7. 智能体回复您需求的速度如何？")
        q7 = st.radio(
            "",
            ["A. 非常快，几乎瞬间响应", "B. 比较快，在可接受范围内", 
             "C. 一般，有时需要等待", "D. 较慢，影响使用体验"],
            index=None,
            key="q7_radio"
        )
        
        # 第三部分：功能价值与需求
        st.markdown("### 第三部分：功能价值与需求")
        
        # 问题8 - 保持原有格式（多选题已有序号）
        st.write("8. 您最常使用本智能体的哪些功能？（最多选3项）")
        q8_options = [
            "A. 生成课程教学大纲",
            "B. 生成课时讲义/教案",
            "C. 制作教学PPT",
            "D. 设计课堂活动/讨论题",
            "E. 生成测验试题和作业",
            "F. 获取教学灵感或思路",
            "G. 其他"
        ]
        q8 = st.multiselect("选择最多3项", q8_options, max_selections=3, key="q8_multiselect")
        
        if "G. 其他" in q8:
            q8_other = st.text_input("请简要说明:", key="q8_other")
        else:
            q8_other = ""
            
        # 问题9 - 保持原有格式（多选题已有序号）
        st.write("9. 您希望未来智能体增加哪些功能？（最多选3项）")
        q9_options = [
            "A. 生成教学视频脚本或字幕",
            "B. 自动生成学生评语",
            "C. 分析学生学习数据并提供见解",
            "D. 创建差异化的教学材料（针对不同水平学生）",
            "E. 集成更多学科专用的工具（如公式编辑器、代码示例等）",
            "F. 其他"
        ]
        q9 = st.multiselect("选择最多3项", q9_options, max_selections=3, key="q9_multiselect")
        
        if "F. 其他" in q9:
            q9_other = st.text_input("请简要说明:", key="q9_other")
        else:
            q9_other = ""
        
        # 第四部分：推荐倾向
        st.markdown("### 第四部分：推荐倾向")
        
        # 问题10 - 添加序号显示
        st.write("10. 您有多大可能将本助教智能体推荐给您的同事或朋友？")
        q10 = st.radio(
            "",
            ["A. 非常可能（10分）", "B. 可能（8-9分）", "C. 一般（6-7分）", "D. 不太可能（4-5分）", "E. 完全不可能（0-3分）"],
            index=None,
            key="q10_radio"
        )
        
        # 第五部分：开放问答
        st.markdown("### 第五部分：开放问答")
        
        # 问题11 - 添加序号显示
        st.write("11. 您认为我们还有什么需要改进地方？请提出您宝贵的建议。")
        q11 = st.text_area(
            "",  # 标签设为空
            height=100,
            placeholder="请在此输入您的建议...",
            key="q11_textarea"
        )
        
        # 提交按钮 - 使用自定义样式
        st.markdown('<div class="submit-button-container">', unsafe_allow_html=True)
        submitted = st.form_submit_button("提交问卷", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if submitted:
            # 检查必填字段
            required_fields = [q1, q2, q3, q4, q5, q6, q7, q10]
            if any(field is None for field in required_fields):
                st.error("请填写所有问题")
            elif len(q8) == 0:  # 检查多选题8是否至少选择一项
                st.error("请至少选择一项问题8的选项")
            elif len(q9) == 0:  # 检查多选题9是否至少选择一项
                st.error("请至少选择一项问题9的选项")
            elif not q11.strip():  # 检查开放题11是否填写
                st.error("请填写问题11的建议")
            else:
                # 收集所有答案
                survey_data = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "q1": q1,
                    "q1_other": q1_other,
                    "q2": q2,
                    "q2_other": q2_other,
                    "q3": q3,
                    "q4": q4,
                    "q5": q5,
                    "q6": q6,
                    "q7": q7,
                    "q8": q8,
                    "q8_other": q8_other,
                    "q9": q9,
                    "q9_other": q9_other,
                    "q10": q10,
                    "q11": q11
                }
                
                # 保存调查结果
                success = save_survey_result(survey_data)
                if success:
                    st.success("感谢您完成问卷！您的反馈对我们非常重要。")
                    time.sleep(2)
                    st.session_state.current_page = "main"
                    st.rerun()
                else:
                    st.error("保存调查结果时出错，请稍后重试")
    
    # 添加返回按钮
    if st.button("返回主页面", key="back_to_main_from_survey", use_container_width=True):
        st.session_state.current_page = "main"
        st.rerun()

# 保存调查结果
# 在 app.py 中修改 show_survey_results 函数
def show_survey_results():
    """显示评价结果页面 - 只显示用户填写的累计内容"""
    st.markdown('<h1 class="main-header">📊 评价结果统计</h1>', unsafe_allow_html=True)
    
    # 加载评价结果
    results = load_survey_results()
    
    if not results:
        st.info("暂无评价结果")
        if st.button("返回主页面", use_container_width=True):
            st.session_state.current_page = "main"
            st.rerun()
        return
    
    # 显示总评价数
    st.markdown(f"### 总评价数: {len(results)}")
    
    # 显示所有评价记录的累计内容
    st.markdown("### 所有评价记录")
    
    for i, result in enumerate(results):
        with st.expander(f"评价记录 {i+1} - {result.get('timestamp', '未知时间')}"):
            st.write(f"**提交时间:** {result.get('timestamp', '未知时间')}")
            
            # 显示所有问题的回答
            for q_key in ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q10']:
                if q_key in result and result[q_key]:
                    question_text = {
                        'q1': "1. 您目前主要任教的学段是？",
                        'q2': "2. 您任教的主要学科专业领域是？",
                        'q3': "3. 您使用本助教智能体的频率是？",
                        'q4': "4. 总体而言，您对本助教智能体的满意度如何？",
                        'q5': "5. 您认为智能体生成的大纲/讲义内容质量如何？",
                        'q6': "6. 您认为智能体生成的PPT内容与美观度如何？",
                        'q7': "7. 智能体回复您需求的速度如何？",
                        'q10': "10. 您有多大可能将本助教智能体推荐给您的同事或朋友？"
                    }.get(q_key, q_key)
                    
                    st.write(f"**{question_text}**")
                    st.write(result[q_key])
                    
                    # 显示其他选项（如果有）
                    if f"{q_key}_other" in result and result[f"{q_key}_other"]:
                        st.write(f"其他说明: {result[f'{q_key}_other']}")
            
            # 显示多选题
            for q_key in ['q8', 'q9']:
                if q_key in result and result[q_key]:
                    question_text = {
                        'q8': "8. 您最常使用本智能体的哪些功能？",
                        'q9': "9. 您希望未来智能体增加哪些功能？"
                    }.get(q_key, q_key)
                    
                    st.write(f"**{question_text}**")
                    for option in result[q_key]:
                        st.write(f"- {option}")
                    
                    # 显示其他选项（如果有）
                    if f"{q_key}_other" in result and result[f"{q_key}_other"]:
                        st.write(f"其他说明: {result[f'{q_key}_other']}")
            
            # 显示开放题
            if 'q11' in result and result['q11']:
                st.write("**11. 您认为我们还有什么需要改进地方？请提出您宝贵的建议。**")
                st.write(result['q11'])
    
    # 添加导出数据按钮
    if st.button("导出数据为JSON", use_container_width=True):
        # 将数据转换为JSON字符串
        json_data = json.dumps(results, ensure_ascii=False, indent=2)
        
        st.download_button(
            label="下载JSON文件",
            data=json_data,
            file_name="survey_results.json",
            mime="application/json",
            use_container_width=True
        )
    
    if st.button("返回主页面", use_container_width=True):
        st.session_state.current_page = "main"
        st.rerun()

# 显示PPT模板选择页面
def show_ppt_template_selection():
    """显示PPT模板选择页面"""
    st.markdown('<h1 class="main-header">🎨 选择PPT模板</h1>', unsafe_allow_html=True)
    
    st.markdown(f"**正在为章节生成PPT:** {st.session_state.current_chapter_for_ppt}")
    
    # 获取模板文件夹中的所有模板
    template_files = glob.glob("templates/*.pptx")
    template_images = glob.glob("templates/*.png") + glob.glob("templates/*.jpg")
    
    if not template_files:
        st.error("未找到任何PPT模板文件！请在templates文件夹中放置.pptx模板文件")
        if st.button("返回", use_container_width=True):
            st.session_state.show_template_selection = False
            st.rerun()
        return
    
    # 显示模板选择
    st.markdown("### 可用模板")
    
    # 为每个模板创建一个卡片
    cols = st.columns(3)
    for i, template_file in enumerate(template_files):
        col_idx = i % 3
        template_name = template_file.split("/")[-1].replace(".pptx", "")
        
        with cols[col_idx]:
            # 查找对应的预览图
            preview_image = None
            for img_file in template_images:
                if template_name in img_file:
                    preview_image = img_file
                    break
            
            # 显示模板卡片
            st.markdown(f'<div class="resource-card">', unsafe_allow_html=True)
            
            if preview_image:
                try:
                    image = Image.open(preview_image)
                    st.image(image, use_container_width=True, caption=template_name)
                except:
                    st.write(f"**{template_name}**")
            else:
                st.write(f"**{template_name}**")
            
            # 选择按钮
            if st.button(f"选择 {template_name}", key=f"select_{i}", use_container_width=True):
                st.session_state.selected_template = template_file
                st.success(f"已选择模板: {template_name}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 生成按钮
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.selected_template and st.button("生成PPT", use_container_width=True):
            with st.spinner("正在使用选定模板生成PPT..."):
                file_stream, filename = save_lecture_to_ppt(
                    st.session_state.current_lecture_for_ppt,
                    st.session_state.current_chapter_for_ppt,
                    st.session_state.selected_template
                )
                
                if file_stream:
                    st.success("PPT生成完成！")
                    st.download_button(
                        label="下载PPT文档",
                        data=file_stream,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        key="download_ppt_with_template",
                        use_container_width=True
                    )
                else:
                    st.error("生成PPT失败")
    
    with col2:
        if st.button("返回", use_container_width=True):
            st.session_state.show_template_selection = False
            st.rerun()

# 欢迎和引导页面
def show_welcome_and_guide():
    """显示欢迎和引导页面"""
    
    # 读取图片并转换为base64
    def get_base64_of_image(image_path):
        import base64
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
        except Exception as e:
            print(f"图片加载失败: {e}")
            return None
    
    # 处理背景样式
    try:
        image_base64 = get_base64_of_image("background.jpg")
        if image_base64:
            background_style = f"""
                background-image: url('data:image/jpg;base64,{image_base64}'); 
                background-size: cover; 
                background-position: center;
                position: relative;
                min-height: 400px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                border-radius: 15px;
                overflow: hidden;
            """
        else:
            background_style = """
                background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                border-radius: 15px;
                overflow: hidden;
            """
    except:
        background_style = """
            background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border-radius: 15px;
            overflow: hidden;
        """

    st.markdown(f"""
        <div class="welcome-container" style="{background_style} min-height: 150px !important; animation: fadeInUp 1s ease-out;">
            <div style="
                position: absolute;
                left: 20%;
                top: 30%;
                transform: translateY(-50%);
                text-align: left;
                max-width: 60%;
                color: white;
                animation: fadeInUp 1.2s ease-out 0.2s both;
            ">
                <h1 style="
                    color: white; 
                    font-size: 2.4rem;
                    margin: 0; 
                    text-shadow: 3px 3px 15px rgba(0,0,0,0.7), 0 0 20px rgba(255,255,255,0.3);
                    font-weight: bold;
                    line-height: 1.1;
                    animation: float 6s ease-in-out infinite;
                ">🎓 小优——您的课程设计助手</h1>
                <p style="
                    color: white; 
                    font-size: 1.8rem;
                    margin: 10px 0 0 0;
                    text-shadow: 2px 2px 10px rgba(0,0,0,0.6);
                    font-weight: 500;
                    line-height: 1.2;
                    animation: fadeInUp 1.4s ease-out 0.4s both;
                ">基于DeepSeek大模型的智能课程内容生成平台</p>
            </div>
            <!-- 添加一些装饰性元素 -->
            <div style="
                position: absolute;
                right: 10%;
                top: 20%;
                font-size: 4rem;
                opacity: 0.1;
                animation: float 8s ease-in-out infinite;
            ">📚</div>
            <div style="
                position: absolute;
                right: 15%;
                bottom: 30%;
                font-size: 3rem;
                opacity: 0.1;
                animation: float 10s ease-in-out infinite 0.5s;
            ">🎨</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="highlight">
    <h3>👋 快与小优一起踏上课程设计之旅吧</h3>
    <p>我将帮助您快速创建高质量的课程内容，包括：</p>
    <ul>
        <li>生成结构化的课程大纲</li>
        <li>编写详细的章节讲义</li>
        <li>推荐相关教学资源</li>
        <li>通过对话完善课程内容</li>
    </ul>
    <p>现在，让我们开始创建您的第一门课程!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 功能特点展示
    st.markdown("### ✨ 主要功能")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <h3>课程大纲生成</h3>
            <p>根据课程信息自动生成结构合理的大纲</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📖</div>
            <h3>详细讲义编写</h3>
            <p>为每个章节生成包含知识点和例题的讲义</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <h3>教学资源推荐</h3>
            <p>推荐相关教材、视频、工具和案例</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💬</div>
            <h3>多轮对话完善</h3>
            <p>通过对话方式不断优化和完善课程内容</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 开始创建课程按钮
    if st.button("🚀 开始创建课程", use_container_width=True, type="primary"):
        st.session_state.current_step = "course_info"
        st.rerun()

# 课程信息收集页面
def show_course_info_collection():
    """显示课程信息收集页面"""
    st.markdown('<h2 class="sub-header">📋 课程基本信息</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chat-container">
        <div class="assistant-message assistant-intro">
            <strong>小优:</strong> 您好！请告诉我您要创建什么课程？我会根据教育阶段为您生成合适的课程内容。
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 使用表单收集课程信息
    with st.form("course_info_form"):
        st.markdown("### 请输入课程信息")
        
        # 新增：教育阶段选择
        education_stage = st.selectbox(
            "教育阶段",
            ["小学", "初中", "高中", "大学"],
            index=0,
            help="选择课程面向的教育阶段，系统将根据阶段特点生成相应内容"
        )
        
        # 新增：生成语言选择
        generation_language = st.selectbox(
            "生成语言",
            ["中文", "英文"],
            index=0,
            help="选择讲义内容的生成语言"
        )
        
        course_name = st.text_input(
            "课程名称", 
            value=st.session_state.course_info["name"],
            placeholder="例如：数字经济导论、Python编程基础等",
            help="请输入您要创建的课程名称"
        )
        
        objectives = st.text_area(
            "教学目标", 
            value=st.session_state.course_info["objectives"],
            placeholder="例如：理解基本概念、掌握核心技能、培养相关能力等",
            height=100,
            help="请详细描述本课程的教学目标和学习成果"
        )
        
        # 学时数滑块
        hours = st.slider(
            "学时数", 
            min_value=10, 
            max_value=60, 
            value=st.session_state.course_info["hours"], 
            help="选择本课程的总学时数"
        )
        
        # 新增：上传教育政策/考试大纲
        st.markdown("### 上传教育政策/考试大纲（可选）")
        policy_file = st.file_uploader(
            "上传Word或PDF文件",
            type=['docx', 'doc', 'pdf'],
            help="上传教育政策文件或考试大纲，生成的讲义将严格符合这些要求"
        )
        
        # 处理上传的文件
        if policy_file is not None:
            if policy_file != st.session_state.policy_file:
                # 新文件上传，进行解析
                with st.spinner("正在解析政策文件..."):
                    from utils import parse_uploaded_file, extract_key_requirements
                    
                    result = parse_uploaded_file(policy_file)
                    
                    if "error" in result:
                        st.error(f"文件解析失败: {result['error']}")
                        st.session_state.policy_content = ""
                        st.session_state.policy_requirements = ""
                    else:
                        st.session_state.policy_content = result["content"]
                        st.session_state.policy_requirements = extract_key_requirements(result["content"])
                        st.success(f"成功解析{policy_file.type}文件，已提取关键要求")
                        
                        # 显示提取的内容预览
                        with st.expander("查看提取的政策要求预览"):
                            st.text_area("政策要求预览", 
                                       value=st.session_state.policy_requirements, 
                                       height=200,
                                       key="policy_preview",
                                       disabled=True)
                
                st.session_state.policy_file = policy_file
        
        # 显示当前政策要求状态
        if st.session_state.policy_requirements:
            st.markdown(f'<div class="success-box">✅ 已加载文件，生成的讲义将严格符合这些标准</div>', unsafe_allow_html=True)

        
        # 表单提交按钮和返回按钮
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("生成课程内容", type="primary", use_container_width=True)
        
        with col2:
            # 添加返回按钮
            return_clicked = st.form_submit_button("返回上一步", use_container_width=True)
        
        if submitted:
            if not course_name:
                st.error("请输入课程名称")
            else:
                # 保存课程信息（新增教育阶段和生成语言）
                st.session_state.course_info = {
                    "name": course_name,
                    "education_stage": education_stage,
                    "generation_language": generation_language,
                    "objectives": objectives,
                    "hours": hours,
                    "policy_requirements": st.session_state.policy_requirements  # 保存政策要求
                }
                
                # 生成课程大纲（传入教育阶段信息和政策要求）
                with st.spinner("正在生成课程大纲..."):
                    if st.session_state.use_fallback:
                        outline = generate_mock_course_outline(course_name, objectives, hours, education_stage, st.session_state.policy_requirements)
                        st.session_state.course_outline = outline
                        st.session_state.api_error = None
                    else:
                        outline = generate_course_outline(course_name, objectives, hours, education_stage, st.session_state.policy_requirements)
                        
                        if isinstance(outline, dict) and "error" in outline:
                            st.session_state.api_error = outline["error"]
                            st.error("生成课程大纲失败，正在使用备用方案...")
                            outline = generate_mock_course_outline(course_name, objectives, hours, education_stage, st.session_state.policy_requirements)
                            st.session_state.course_outline = outline
                        else:
                            st.session_state.course_outline = outline
                            st.session_state.api_error = None

                # 生成教学资源（传入教育阶段信息）
                with st.spinner("正在推荐教学资源..."):
                    try:
                        if st.session_state.use_fallback:
                            resources = recommend_mock_resources(course_name, education_stage)
                            st.session_state.resources = resources
                        else:
                            resources = recommend_resources(course_name, education_stage)
                            
                            if isinstance(resources, dict) and "error" in resources:
                                st.warning("推荐教学资源失败，正在使用备用方案...")
                                resources = recommend_mock_resources(course_name, education_stage)
                                st.session_state.resources = resources
                            else:
                                st.session_state.resources = resources
                    except Exception as e:
                        st.error(f"生成教学资源时出错: {e}")
                        resources = recommend_mock_resources(course_name, education_stage)
                        st.session_state.resources = resources
                
                st.session_state.current_step = "complete"
                st.rerun()
        
        # 处理返回按钮点击事件
        if return_clicked:
            st.session_state.current_step = "welcome"
            st.rerun()

# 生成讲义内容，带有自动降级策略
def generate_lecture_with_fallback(chapter_name, key_points, hours, education_stage="小学", generation_language="中文", policy_requirements=""):
    """生成讲义内容，带有自动降级策略"""
    # 如果API错误次数过多，自动使用备用方案
    if st.session_state.api_status["error_count"] > 3:
        st.warning("API错误次数过多，自动切换到备用方案")
        return generate_mock_lecture_content(chapter_name, key_points, hours, education_stage, generation_language, policy_requirements)
    
    try:
        response = generate_lecture_content(chapter_name, key_points, hours, education_stage, generation_language, policy_requirements)
        
        if isinstance(response, dict) and "error" in response:
            # 更新API状态
            st.session_state.api_status["error_count"] += 1
            st.session_state.api_status["last_error"] = response["error"]
            
            # 如果错误次数超过阈值，使用备用方案
            if st.session_state.api_status["error_count"] > 2:
                st.warning("API调用失败，使用备用方案")
                return generate_mock_lecture_content(chapter_name, key_points, hours, education_stage, generation_language, policy_requirements)
            else:
                # 重试
                st.warning("API调用失败，正在重试...")
                time.sleep(1)
                return generate_lecture_with_fallback(chapter_name, key_points, hours, education_stage, generation_language, policy_requirements)
        else:
            # 重置错误计数
            st.session_state.api_status["error_count"] = 0
            st.session_state.api_status["last_success"] = time.time()
            return response
            
    except Exception as e:
        st.session_state.api_status["error_count"] += 1
        st.session_state.api_status["last_error"] = str(e)
        
        if st.session_state.api_status["error_count"] > 2:
            st.warning("API调用异常，使用备用方案")
            return generate_mock_lecture_content(chapter_name, key_points, hours, education_stage, generation_language, policy_requirements)
        else:
            st.warning("API调用异常，正在重试...")
            time.sleep(1)
            return generate_lecture_with_fallback(chapter_name, key_points, hours, education_stage, generation_language, policy_requirements)

# 加粗显示修改的内容
def highlight_modified_content(old_content, new_content):
    """比较新旧内容并加粗显示修改的部分"""
    if not old_content:
        return new_content
    
    # 简单的文本比较（实际应用中可以使用更复杂的diff算法）
    old_lines = old_content.split('\n')
    new_lines = new_content.split('\n')
    
    result = []
    i, j = 0, 0
    
    while i < len(old_lines) and j < len(new_lines):
        if old_lines[i] == new_lines[j]:
            result.append(new_lines[j])
            i += 1
            j += 1
        else:
            # 找到修改的行，用加粗显示
            result.append(f'<span class="modified-content">{new_lines[j]}</span>')
            j += 1
    
    # 添加剩余的新行
    while j < len(new_lines):
        result.append(f'<span class="modified-content">{new_lines[j]}</span>')
        j += 1
    
    return '\n'.join(result)

# 获取章节的唯一标识符
def get_chapter_key(chapter_name):
    """为章节生成唯一的键，用于在session_state中存储讲义内容"""
    # 使用正则表达式清理章节名称，创建有效的键
    clean_name = re.sub(r'[^\w]', '_', chapter_name)
    return f"lecture_{clean_name}"

# 主内容区域
def main_content():
    """显示主页面内容"""
    # 根据当前步骤显示不同内容
    if st.session_state.current_step == "welcome":
        show_welcome_and_guide()
        return
    
    if st.session_state.current_step == "course_info":
        show_course_info_collection()
        return
    
    # 显示课程大纲和内容
    st.markdown(f'<h1 class="main-header">📘 {st.session_state.course_info["name"]}</h1>', unsafe_allow_html=True)
    
    # 侧边栏 - 课程信息显示和操作
    with st.sidebar:
        st.markdown('<div class="sub-header">导航</div>', unsafe_allow_html=True)
        
        # 添加返回欢迎页面按钮
        if st.button("返回首页", use_container_width=True, help="返回欢迎页面重新开始"):
            st.session_state.current_step = "welcome"
            st.rerun()
            
        # 添加重新生成按钮
        if st.button("重新生成课程内容", use_container_width=True, help="重新生成课程大纲和资源"):
            st.session_state.current_step = "course_info"
            st.rerun()
        
        st.markdown('<div class="sub-header">课程信息</div>', unsafe_allow_html=True)
        
        st.info(f"**课程名称:** {st.session_state.course_info['name']}")
        st.info(f"**总学时:** {st.session_state.course_info['hours']}")
        
        st.markdown("**教学目标:**")
        st.markdown(f'<div class="highlight">{st.session_state.course_info["objectives"]}</div>', unsafe_allow_html=True)
        
        # 显示API密钥状态
        from config import DEEPSEEK_API_KEY
        if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "你的API密钥":
            st.markdown('<div class="warning-box">⚠️ 未设置DeepSeek API密钥</div>', unsafe_allow_html=True)
            st.info("请在.env文件中设置DEEPSEEK_API_KEY")
            st.session_state.use_fallback = True
        else:
            st.markdown('<div class="success-box">✅ DeepSeek API密钥已设置</div>', unsafe_allow_html=True)
        
        # 添加网络诊断功能
        st.markdown('<div class="sub-header">网络诊断</div>', unsafe_allow_html=True)
        
        if st.button("基本网络检查", help="检查基本网络连接状态"):
            try:
                import requests
                test_response = requests.get("https://www.baidu.com", timeout=5)
                if test_response.status_code == 200:
                    st.markdown('<div class="success-box">✅ 基本网络连接正常</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="warning-box">⚠️ 基本网络连接可能存在问题</div>', unsafe_allow_html=True)
            except:
                st.markdown('<div class="error-box">❌ 基本网络连接异常</div>', unsafe_allow_html=True)
        
        # 添加快速导航区域
        st.markdown('<div class="sub-header">快速导航</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("课程大纲", use_container_width=True, help="跳转到课程大纲页面"):
                st.session_state.active_tab = "课程大纲与讲义"
                st.rerun()
        with col2:
            if st.button("教学资源", use_container_width=True, help="跳转到教学资源页面"):
                st.session_state.active_tab = "教学资源"
                st.rerun()
                
        if st.button("多轮对话完善", use_container_width=True, help="跳转到多轮对话页面"):
            st.session_state.active_tab = "多轮对话完善"
            st.rerun()
        
        # 添加备用方案选项
        st.markdown('<div class="sub-header">高级选项</div>', unsafe_allow_html=True)
        use_fallback = st.checkbox("API不可用时使用备用方案", value=st.session_state.use_fallback, 
                                  help="当API调用失败时，使用模拟数据作为备用方案")
        st.session_state.use_fallback = use_fallback

    # 显示API错误信息
    if st.session_state.api_error:
        st.markdown('<div class="error-box">API调用错误</div>', unsafe_allow_html=True)
        with st.expander("查看错误详情"):
            st.code(st.session_state.api_error)
        st.info("建议：1. 检查网络连接 2. 检查API密钥 3. 启用备用方案")

    # 主内容区域 - 使用选择框模拟标签页
    tab_options = ["课程大纲与讲义", "教学资源", "多轮对话完善"]
    
    # 创建隐藏的选择框来控制标签页
    selected_tab = st.selectbox(
        "选择标签页",
        tab_options,
        index=tab_options.index(st.session_state.active_tab),
        label_visibility="collapsed"
    )
    
    # 更新活动标签页
    st.session_state.active_tab = selected_tab
    
    # 根据选中的标签页显示内容
    if st.session_state.active_tab == "课程大纲与讲义":
        # 课程大纲与讲义内容
        if st.session_state.course_outline:
            st.markdown('<div class="sub-header">课程大纲</div>', unsafe_allow_html=True)
            
            # 显示课程基本信息
            col1, col2, col3 = st.columns(3)
            with col1:
                if "课程名称" in st.session_state.course_outline:
                    st.info(f"**课程名称:** {st.session_state.course_outline['课程名称']}")
            
            with col2:
                if "总学时" in st.session_state.course_outline:
                    st.info(f"**总学时:** {st.session_state.course_outline['总学时']}")
            
            if "教学目标" in st.session_state.course_outline:
                st.markdown("**教学目标:**")
                st.markdown(f'<div class="highlight">{st.session_state.course_outline["教学目标"]}</div>', unsafe_allow_html=True)
            
            # 显示章节列表
            if "章节列表" in st.session_state.course_outline:
                st.markdown('<div class="sub-header">章节安排</div>', unsafe_allow_html=True)
                
                for i, chapter in enumerate(st.session_state.course_outline["章节列表"]):
                    # 使用章节名称生成唯一的键，而不是索引，确保讲义内容持久化
                    lecture_key = get_chapter_key(chapter['章节名称'])
                    
                    with st.expander(f"第{i+1}章: {chapter['章节名称']} - {chapter['学时']}学时", icon="📖"):
                        st.markdown(f'<div class="chapter-card">', unsafe_allow_html=True)
                        st.write("**重点内容:**", chapter.get("重点内容", "暂无"))
                        
                        # 为每个章节添加生成讲义的按钮
                        if st.button(f"生成{chapter['章节名称']}讲义", key=f"gen_{lecture_key}", help="生成该章节的详细讲义内容"):
                            with st.spinner(f"正在生成{chapter['章节名称']}讲义..."):
                                # 使用带降级策略的函数，传入教育阶段、生成语言和政策要求
                                content = generate_lecture_with_fallback(
                                    chapter["章节名称"],
                                    chapter.get("重点内容", ""),
                                    chapter["学时"],
                                    st.session_state.course_info["education_stage"],
                                    st.session_state.course_info["generation_language"],
                                    st.session_state.course_info.get("policy_requirements", "")  # 新增政策要求参数
                                )
                                # 修复：确保讲义内容正确保存到session_state
                                st.session_state.generated_lectures[lecture_key] = content
                                # 同时记录生成状态
                                st.session_state.lecture_generation_status[lecture_key] = True
                                st.markdown('<div class="success-box">讲义生成完成！</div>', unsafe_allow_html=True)
                                st.rerun()  # 立即刷新显示生成的讲义
                        
                        # 显示已生成的讲义 - 修复：检查讲义是否存在且不为空
                        if lecture_key in st.session_state.generated_lectures and st.session_state.generated_lectures[lecture_key]:
                            st.markdown("### 讲义内容")
                            st.markdown(st.session_state.generated_lectures[lecture_key])
                            
                            # 添加下载Word文档按钮
                            if st.button(f"导出Word文档", key=f"export_{lecture_key}"):
                                with st.spinner("正在生成Word文档..."):
                                    file_stream, filename = save_lecture_to_word(
                                        st.session_state.generated_lectures[lecture_key],
                                        chapter["章节名称"]
                                    )
                                    
                                    if file_stream:
                                        st.success("Word文档生成完成！")
                                        st.download_button(
                                            label="下载Word文档",
                                            data=file_stream,
                                            file_name=filename,
                                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                            key=f"download_{lecture_key}",
                                            use_container_width=True
                                        )
                                    else:
                                        st.error("生成Word文档失败")
                            
                            # 添加下载PPT文档按钮
                            if st.button(f"导出PPT文档", key=f"export_ppt_{lecture_key}"):
                                st.session_state.show_template_selection = True
                                st.session_state.current_lecture_for_ppt = st.session_state.generated_lectures[lecture_key]
                                st.session_state.current_chapter_for_ppt = chapter["章节名称"]
                                st.rerun()

                            # 添加跳转到对话页面的按钮
                            if st.button(f"进一步完善{chapter['章节名称']}讲义", key=f"goto_{lecture_key}", 
                                        help="通过多轮对话进一步完善讲义内容"):
                                st.session_state.current_lecture = lecture_key
                                st.session_state.current_chapter = chapter["章节名称"]
                                st.session_state.active_tab = "多轮对话完善"
                                st.rerun()
                        else:
                            # 显示提示信息
                            st.info("该章节的讲义尚未生成，请点击上方按钮生成讲义内容。")

                        st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.info("课程大纲生成中...")

    elif st.session_state.active_tab == "教学资源":
        # 教学资源内容 - 完全重写：支持多种数据格式
        st.markdown('<div class="sub-header">推荐教学资源</div>', unsafe_allow_html=True)
        
        # 调试信息：显示资源字典的内容
        if st.button("显示调试信息"):
            st.write("资源字典原始内容:", st.session_state.resources)
            st.write("资源类型:", type(st.session_state.resources))
        
        # 检查资源是否存在且不为空
        if st.session_state.resources:
            # 处理不同的资源格式
            if isinstance(st.session_state.resources, dict):
                # 标准字典格式处理
                resource_sections = {
                    "教材": "📚 推荐教材",
                    "在线视频": "🎥 在线视频资源", 
                    "工具/软件": "🛠️ 工具与软件",
                    "案例研究": "📊 案例研究"
                }
                
                for resource_key, display_name in resource_sections.items():
                    if resource_key in st.session_state.resources:
                        resources_data = st.session_state.resources[resource_key]
                        
                        st.markdown(f"### {display_name}")
                        
                        if isinstance(resources_data, list):
                            # 列表格式：直接显示每个项目
                            for i, item in enumerate(resources_data):
                                if isinstance(item, dict):
                                    # 字典项目：格式化显示
                                    display_text = _format_resource_item(item)
                                    st.markdown(f'<div class="resource-card">{display_text}</div>', unsafe_allow_html=True)
                                else:
                                    # 字符串项目：直接显示
                                    st.markdown(f'<div class="resource-card">{item}</div>', unsafe_allow_html=True)
                        elif isinstance(resources_data, dict):
                            # 单个字典项目
                            display_text = _format_resource_item(resources_data)
                            st.markdown(f'<div class="resource-card">{display_text}</div>', unsafe_allow_html=True)
                        else:
                            # 其他格式转换为字符串显示
                            st.markdown(f'<div class="resource-card">{str(resources_data)}</div>', unsafe_allow_html=True)
                    else:
                        st.info(f"暂无{resource_key}资源")
            
            elif isinstance(st.session_state.resources, list):
                # 列表格式：直接显示所有项目
                st.markdown("### 所有推荐资源")
                for item in st.session_state.resources:
                    if isinstance(item, dict):
                        display_text = _format_resource_item(item)
                        st.markdown(f'<div class="resource-card">{display_text}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="resource-card">{item}</div>', unsafe_allow_html=True)
            
            else:
                # 其他格式
                st.markdown("### 教学资源")
                st.markdown(f'<div class="resource-card">{str(st.session_state.resources)}</div>', unsafe_allow_html=True)
        
        else:
            # 如果资源为空，显示提示并提供重新生成按钮
            st.info("暂无教学资源，请先生成课程大纲")
            
            if st.button("重新生成教学资源", help="重新获取教学资源推荐"):
                with st.spinner("正在重新生成教学资源..."):
                    try:
                        if st.session_state.use_fallback:
                            resources = recommend_mock_resources(st.session_state.course_info["name"])
                        else:
                            resources = recommend_resources(st.session_state.course_info["name"])
                            
                            if isinstance(resources, dict) and "error" in resources:
                                st.warning("推荐教学资源失败，使用备用方案")
                                resources = recommend_mock_resources(st.session_state.course_info["name"])
                        
                        st.session_state.resources = resources
                        st.success("教学资源已更新！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"重新生成教学资源时出错: {e}")


    elif st.session_state.active_tab == "多轮对话完善":
        # 多轮对话完善内容
        st.markdown('<div class="sub-header">多轮对话完善讲义内容</div>', unsafe_allow_html=True)
        
        # 初始化当前对话章节
        if "current_lecture" not in st.session_state:
            st.info("请先从课程大纲页面选择一个章节进行完善")
        else:
            lecture_key = st.session_state.current_lecture
            chapter_name = st.session_state.current_chapter
            
            st.markdown(f'### 正在完善: {chapter_name}')
            
            # 显示当前讲义内容 - 修复：确保讲义内容存在
            if lecture_key in st.session_state.generated_lectures and st.session_state.generated_lectures[lecture_key]:
                st.markdown("#### 当前讲义内容")
                st.markdown(f'<div class="highlight">{st.session_state.generated_lectures[lecture_key]}</div>', unsafe_allow_html=True)
            else:
                st.warning("该章节的讲义内容不存在，请先返回课程大纲页面生成讲义")
                if st.button("返回课程大纲", use_container_width=True):
                    st.session_state.active_tab = "课程大纲与讲义"
                    st.rerun()
                return
            
            # 初始化对话历史
            if lecture_key not in st.session_state.conversation_history:
                st.session_state.conversation_history[lecture_key] = []
            
            # 显示对话历史
            if st.session_state.conversation_history[lecture_key]:
                st.markdown("#### 对话历史")
                for i, (role, message) in enumerate(st.session_state.conversation_history[lecture_key]):
                    if role == "user":
                        st.markdown(f'<div class="user-message"><b>您:</b> {message}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="assistant-message"><b>小优:</b> {message}</div>', unsafe_allow_html=True)
            
            # 用户输入区域
            st.markdown("#### 提出修改要求")
            user_input = st.text_area(
                "请输入您对讲义的修改要求或补充说明:",
                placeholder="例如：增加更多实际案例、补充相关数据、调整内容深度等",
                key=f"input_{lecture_key}",
                height=100
            )
            
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])  # 修改为4列
            with col1:
               
                if st.button("提交修改要求", use_container_width=True, help="提交您的修改要求"):
                    if user_input:
                        # 保存旧内容用于比较
                        old_content = st.session_state.generated_lectures.get(lecture_key, "")
                        
                        # 添加到对话历史
                        st.session_state.conversation_history[lecture_key].append(("user", user_input))
                        
                        with st.spinner("正在根据您的要求完善讲义..."):
                            if st.session_state.use_fallback:
                                # 使用备用方案
                                updated_content = generate_mock_lecture_content(
                                    chapter_name, 
                                    f"根据要求 '{user_input}' 完善的内容",
                                    st.session_state.course_outline["章节列表"][int(lecture_key.split("_")[1])]["学时"],
                                    st.session_state.course_info["education_stage"],
                                    st.session_state.course_info["generation_language"]  # 新增：传递语言参数
                                )
                                # 加粗显示修改的内容
                                highlighted_content = highlight_modified_content(old_content, updated_content)
                                st.session_state.generated_lectures[lecture_key] = updated_content
                                st.session_state.conversation_history[lecture_key].append(
                                    ("assistant", "已根据您的要求完善讲义内容 (使用备用方案)")
                                )
                                st.markdown('<div class="success-box">讲义已更新！(使用备用方案)</div>', unsafe_allow_html=True)
                            else:
                                # 使用真实API，传入教育阶段和语言
                                updated_content = update_lecture_content(
                                    st.session_state.generated_lectures[lecture_key],
                                    user_input,
                                    st.session_state.conversation_history[lecture_key],
                                    st.session_state.course_info["education_stage"],
                                    st.session_state.course_info["generation_language"],
                                    st.session_state.course_info.get("policy_requirements", "")  # 新增政策要求参数
                                )
                                
                                if isinstance(updated_content, dict) and "error" in updated_content:
                                    st.markdown(f'<div class="error-box">更新讲义失败: {updated_content["error"]}</div>', unsafe_allow_html=True)
                                    st.session_state.conversation_history[lecture_key].append(
                                        ("assistant", f"更新失败: {updated_content['error']}")
                                    )
                                else:
                                    # 加粗显示修改的内容
                                    highlighted_content = highlight_modified_content(old_content, updated_content)
                                    st.session_state.generated_lectures[lecture_key] = updated_content
                                    st.session_state.conversation_history[lecture_key].append(
                                        ("assistant", "已根据您的要求完善讲义内容")
                                    )
                                    st.markdown('<div class="success-box">讲义已更新！</div>', unsafe_allow_html=True)
                        
                        # 显示更新后的内容（带加粗）
                        st.markdown("#### 更新后的讲义内容")
                        st.markdown(f'<div class="highlight">{highlighted_content}</div>', unsafe_allow_html=True)
                        
                        # 清空输入框
                        st.rerun()
                    else:
                        st.warning("请输入修改要求")
            with col2:
                # 添加导出PPT文档按钮
                if st.button("导出PPT", use_container_width=True, help="导出当前讲义为PPT文档"):
                    st.session_state.show_template_selection = True
                    st.session_state.current_lecture_for_ppt = st.session_state.generated_lectures[lecture_key]
                    st.session_state.current_chapter_for_ppt = chapter_name
                    st.rerun()

            with col3:
                # 添加导出Word文档按钮
                if st.button("导出Word", use_container_width=True, help="导出当前讲义为Word文档"):
                    with st.spinner("正在生成Word文档..."):
                        file_stream, filename = save_lecture_to_word(
                            st.session_state.generated_lectures[lecture_key],
                            chapter_name
                        )
                        if file_stream:
                            st.success("Word文档生成完成！")
                            st.download_button(
                                label="下载Word文档",
                                data=file_stream,
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"download_modified_{lecture_key}",
                                use_container_width=True
                            )
                        else:
                            st.error("生成Word文档失败")

            with col4:
                if st.button("重置对话", use_container_width=True, help="清空当前对话历史"):
                    st.session_state.conversation_history[lecture_key] = []
                    st.success("对话历史已重置")
                    st.rerun()
                        

    # 页脚
    st.divider()
    st.caption("基于DeepSeek大模型开发的课程内容辅助生成 | 数据要素素质大赛参赛作品")

# 主程序逻辑
def main():
    """主程序入口"""
    # 根据当前页面状态显示不同内容
    if st.session_state.current_page == "survey":
        show_satisfaction_survey()
    elif st.session_state.current_page == "results":
        show_survey_results()
    elif st.session_state.show_template_selection:
        show_ppt_template_selection()
    else:
        main_content()

# 右下角满意度调查按钮 - 修改显示条件
if st.session_state.current_page == "main" and st.session_state.current_step != "welcome":
    st.markdown("""
    <style>
    .fixed-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 999;
    }
    .fixed-button button {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%) !important;
        color: white !important;
        border: none !important;
        padding: 14px 28px !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
        cursor: pointer !important;
        transition: all 0.3s !important;
        font-size: 16px !important;
    }
    .fixed-button button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="fixed-button">', unsafe_allow_html=True)
    if st.button("📊 满意度调查", key="survey_button"):
        st.session_state.current_page = "survey"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 运行主程序
if __name__ == "__main__":
    main()

# 在 app.py 的 CSS 部分添加对例题的特殊样式处理
    st.markdown("""
<style>
    /* 其他样式保持不变... */

    /* 新增：例题样式 */
    .example-container {
        background-color: #f8f9fa;
        border-left: 4px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .example-question {
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 8px;
    }
    
    .example-answer {
        color: #34495e;
        background-color: #ecf0f1;
        padding: 10px;
        border-radius: 3px;
        margin-top: 5px;
    }
    
    /* 确保Markdown列表正确显示 */
    .example-list {
        list-style-type: decimal;
        padding-left: 20px;
    }
    
    .example-list li {
        margin-bottom: 15px;
        padding: 10px;
        background-color: white;
        border-radius: 5px;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)