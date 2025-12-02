#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调查结果统计与分析工具
功能：
1. 读取survey_results.json文件
2. 为单选题生成饼图
3. 为多选题生成条形图
4. 为开放题生成词云图
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud
import jieba
from collections import Counter
import os
from PIL import Image
import matplotlib.font_manager as fm

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

# 问题映射表
QUESTION_MAP = {
    'q1': "1. 您目前主要任教的学段是？",
    'q2': "2. 您任教的主要学科专业领域是？",
    'q3': "3. 您使用本助教智能体的频率是？",
    'q4': "4. 总体而言，您对本助教智能体的满意度如何？",
    'q5': "5. 您认为智能体生成的大纲/讲义内容质量如何？",
    'q6': "6. 您认为智能体生成的PPT内容与美观度如何？",
    'q7': "7. 智能体回复您需求的速度如何？",
    'q8': "8. 您最常使用本智能体的哪些功能？",
    'q9': "9. 您希望未来智能体增加哪些功能？",
    'q10': "10. 您有多大可能将本助教智能体推荐给您的同事或朋友？",
    'q11': "11. 您认为我们还有什么需要改进地方？请提出您宝贵的建议。"
}

def load_survey_data(file_path='survey_results.json'):
    """加载调查结果数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"成功加载 {len(data)} 条调查结果")
        return data
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"错误：文件 {file_path} 格式不正确")
        return []

def analyze_single_choice(data, question_key):
    """分析单选题数据"""
    counts = {}
    for result in data:
        if question_key in result and result[question_key]:
            answer = result[question_key]
            counts[answer] = counts.get(answer, 0) + 1
    
    # 计算百分比
    total = sum(counts.values())
    percentages = {k: round(v/total*100, 1) for k, v in counts.items()}
    
    return counts, percentages

def analyze_multi_choice(data, question_key):
    """分析多选题数据"""
    option_counts = {}
    for result in data:
        if question_key in result and result[question_key]:
            for option in result[question_key]:
                option_counts[option] = option_counts.get(option, 0) + 1
    
    # 计算百分比（基于总回答人数）
    total = len(data)
    percentages = {k: round(v/total*100, 1) for k, v in option_counts.items()}
    
    return option_counts, percentages

def analyze_open_question(data, question_key):
    """分析开放题数据"""
    responses = []
    for result in data:
        if question_key in result and result[question_key]:
            responses.append(result[question_key])
    
    return responses

def create_pie_chart(counts, percentages, title, filename):
    """创建饼图"""
    if not counts:
        print(f"警告：{title} 没有数据，跳过生成饼图")
        return
    
    # 准备数据
    labels = list(counts.keys())
    sizes = list(counts.values())
    
    # 创建饼图
    fig, ax = plt.subplots(figsize=(10, 8))
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=labels, 
        autopct='%1.1f%%',
        startangle=90,
        colors=plt.cm.Paired(np.linspace(0, 1, len(labels)))
    )
    
    # 美化文本
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # 保存图表
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"已保存饼图: {filename}")

def create_bar_chart(counts, percentages, title, filename):
    """创建条形图"""
    if not counts:
        print(f"警告：{title} 没有数据，跳过生成条形图")
        return
    
    # 准备数据
    options = list(counts.keys())
    values = list(counts.values())
    
    # 按值排序
    sorted_data = sorted(zip(options, values), key=lambda x: x[1], reverse=True)
    options, values = zip(*sorted_data)
    
    # 创建条形图
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(options, values, color='skyblue')
    ax.set_xlabel('选择次数', fontsize=12)
    ax.set_title(title, fontsize=16, fontweight='bold')
    
    # 在条形上添加数值标签
    for i, (option, value) in enumerate(zip(options, values)):
        percent = percentages[option]
        ax.text(value + 0.1, i, f'{value}次 ({percent}%)', va='center', fontsize=10)
    
    plt.tight_layout()
    
    # 保存图表
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"已保存条形图: {filename}")

def create_word_cloud(responses, title, filename):
    """创建词云图 - 修复字体问题版本"""
    print(f"开始生成词云图，回答数量: {len(responses)}")
    
    if not responses:
        print(f"警告：{title} 没有数据，跳过生成词云图")
        return False
    
    try:
        # 合并所有回答
        text = ' '.join([str(r) for r in responses if r])
        print(f"合并文本长度: {len(text)}")
        
        if len(text.strip()) < 5:
            print("文本太短，无法生成有意义的词云")
            return False
        
        # 中文分词
        words = jieba.cut(text)
        word_list = []
        
        # 停用词列表
        stop_words = {'自己','希望','的', '了', '和', '是', '就', '都', '而', '及', '与', '这', '那', '你', '我', '他', '就', '也', '还'}
        
        for word in words:
            word = word.strip()
            if (len(word) > 1 and  # 只保留长度大于1的词
                word not in stop_words and  # 过滤停用词
                not word.isdigit()):  # 过滤纯数字
                word_list.append(word)
        
        print(f"分词后有效词汇数: {len(word_list)}")
        
        if not word_list:
            print("没有有效的词汇可用于生成词云")
            return False
        
        # 统计词频
        word_freq = Counter(word_list)
        top_words = word_freq.most_common(10)
        print(f"前10个高频词: {top_words}")
        
        # 更可靠的字体路径查找方法
        font_path = find_chinese_font()
        if font_path:
            print(f"使用字体: {font_path}")
        else:
            print("警告：未找到中文字体，尝试使用默认字体")
            # 如果不指定字体路径，让wordcloud使用默认字体
            font_path = None
        
        # 创建词云配置
        wc_config = {
            'width': 800,
            'height': 600,
            'background_color': 'white',
            'max_words': 50,
            'colormap': 'viridis',
            'relative_scaling': 0.5,
            'collocations': False
        }
        
        # 只有在找到有效字体时才设置font_path
        if font_path and os.path.exists(font_path):
            wc_config['font_path'] = font_path
        
        wordcloud = WordCloud(**wc_config)
        
        # 生成词云
        if word_freq:
            wordcloud = wordcloud.generate_from_frequencies(word_freq)
        else:
            wordcloud = wordcloud.generate(text)
        
        # 绘制词云
        plt.figure(figsize=(10, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=14, pad=20)
        
        # 保存词云图
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✓ 成功保存词云图: {filename}")
        return True
        
    except Exception as e:
        print(f"生成词云图时出错: {e}")
        # 尝试使用不指定字体的简化版本
        return create_simple_word_cloud(responses, title, filename)

def find_chinese_font():
    """查找系统中可用的中文字体"""
    # Windows 字体路径
    windows_paths = [
        'C:/Windows/Fonts/simhei.ttf',      # 黑体
        'C:/Windows/Fonts/msyh.ttc',        # 微软雅黑
        'C:/Windows/Fonts/simsun.ttc',      # 宋体
        'C:/Windows/Fonts/simkai.ttf',      # 楷体
    ]
    
    # 检查常见中文字体是否存在
    for font_path in windows_paths:
        if os.path.exists(font_path):
            return font_path
    
    # 如果常见路径都没有，尝试使用matplotlib的字体
    try:
        import matplotlib.font_manager as fm
        # 获取所有字体
        fonts = fm.findSystemFonts()
        # 查找包含中文字体名称的字体
        chinese_fonts = [f for f in fonts if any(name in f.lower() for name in 
                          ['simhei', 'msyh', 'simsun', 'simkai', 'st', 'hei', 'kai'])]
        if chinese_fonts:
            return chinese_fonts[0]
    except:
        pass
    
    return None

def create_simple_word_cloud(responses, title, filename):
    """创建简化版词云（不依赖中文字体）"""
    print("尝试创建简化版词云...")
    
    try:
        # 合并文本
        text = ' '.join([str(r) for r in responses if r])
        
        if len(text.strip()) < 5:
            return False
        
        # 创建英文词云（不指定中文字体）
        wordcloud = WordCloud(
            width=800,
            height=600,
            background_color='white',
            max_words=50
        ).generate(text)
        
        plt.figure(figsize=(10, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=14, pad=20)
        
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ 简化版词云图已保存: {filename}")
        return True
        
    except Exception as e:
        print(f"简化版词云也失败: {e}")
        return False

def generate_text_analysis(responses, output_dir, question_key):
    """生成文本分析报告（作为词云图的备选）"""
    if not responses:
        return
    
    report_path = os.path.join(output_dir, f'{question_key}_text_analysis.txt')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("开放题文本分析报告\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"问题: {QUESTION_MAP.get(question_key, question_key)}\n")
        f.write(f"有效回答数: {len(responses)}\n\n")
        
        # 简单的词频统计
        all_text = ' '.join(responses)
        words = jieba.cut(all_text)
        word_list = [word for word in words if len(word) > 1]
        
        if word_list:
            word_freq = Counter(word_list)
            f.write("词频统计:\n")
            f.write("-" * 20 + "\n")
            for word, count in word_freq.most_common(20):
                f.write(f"{word}: {count}次\n")
        
        f.write("\n详细回答内容:\n")
        f.write("-" * 20 + "\n")
        for i, response in enumerate(responses, 1):
            f.write(f"{i}. {response}\n")
    
    print(f"✓ 文本分析报告已保存: {report_path}")
def main():
    """主函数 - 修复版本"""
    # 创建输出目录
    output_dir = 'survey_analysis_results'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 加载数据
    data = load_survey_data()
    if not data:
        return
    
    # 分析单选题 (q1-q7, q10)
    single_choice_questions = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q10']
    for q_key in single_choice_questions:
        counts, percentages = analyze_single_choice(data, q_key)
        title = QUESTION_MAP.get(q_key, q_key)
        filename = os.path.join(output_dir, f"{q_key}_pie_chart.png")
        create_pie_chart(counts, percentages, title, filename)
    
    # 分析多选题 (q8, q9)
    multi_choice_questions = ['q8', 'q9']
    for q_key in multi_choice_questions:
        counts, percentages = analyze_multi_choice(data, q_key)
        title = QUESTION_MAP.get(q_key, q_key)
        filename = os.path.join(output_dir, f"{q_key}_bar_chart.png")
        create_bar_chart(counts, percentages, title, filename)
    
    # 分析开放题 (q11)
    open_question = 'q11'
    responses = analyze_open_question(data, open_question)
    
    if responses:
        title = QUESTION_MAP.get(open_question, open_question)
        filename = os.path.join(output_dir, f"{open_question}_word_cloud.png")
        
        print(f"\n=== 处理开放题 ===")
        print(f"回答数量: {len(responses)}")
        
        # 尝试生成词云图
        success = create_word_cloud(responses, title, filename)
        
        # 无论词云是否成功，都生成文本分析报告
        generate_text_analysis(responses, output_dir, open_question)
        
        if not success:
            print("词云图生成失败，但已生成文本分析报告作为替代")
    else:
        print("开放题没有有效数据")
    
    # 生成统计摘要
    generate_summary_report(data, output_dir)
    
    print(f"\n所有图表已保存到 {output_dir} 目录")

def generate_summary_report(data, output_dir):
    """生成统计摘要报告"""
    report_path = os.path.join(output_dir, 'survey_summary.txt')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("满意度调查统计摘要\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"总评价数: {len(data)}\n\n")
        
        # 单选题统计
        f.write("单选题统计:\n")
        f.write("-" * 20 + "\n")
        
        single_choice_questions = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q10']
        for q_key in single_choice_questions:
            counts, percentages = analyze_single_choice(data, q_key)
            title = QUESTION_MAP.get(q_key, q_key)
            
            f.write(f"\n{title}\n")
            for option, count in counts.items():
                percent = percentages[option]
                f.write(f"  {option}: {count}人 ({percent}%)\n")
        
        # 多选题统计
        f.write("\n多选题统计:\n")
        f.write("-" * 20 + "\n")
        
        multi_choice_questions = ['q8', 'q9']
        for q_key in multi_choice_questions:
            counts, percentages = analyze_multi_choice(data, q_key)
            title = QUESTION_MAP.get(q_key, q_key)
            
            f.write(f"\n{title}\n")
            for option, count in counts.items():
                percent = percentages[option]
                f.write(f"  {option}: {count}次 ({percent}%)\n")
        
        # 开放题统计
        f.write("\n开放题回答摘要:\n")
        f.write("-" * 20 + "\n")
        
        open_question = 'q11'
        responses = analyze_open_question(data, open_question)
        f.write(f"\n共收到 {len(responses)} 条改进建议\n\n")
        
        for i, response in enumerate(responses, 1):
            f.write(f"建议 {i}:\n{response}\n\n")
    
    print(f"已保存统计摘要: {report_path}")

if __name__ == "__main__":
    main()