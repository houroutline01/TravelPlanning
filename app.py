import streamlit as st
from audiorecorder import audiorecorder
import pandas as pd
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from database import init_db, register_user, authenticate_user, save_itinerary, get_user_itineraries, get_latest_itinerary, get_total_budget, add_expense, get_user_expenses, delete_expense, delete_itinerary

load_dotenv()

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("API_KEY", "")
if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = os.getenv("API_BASE_URL", "")
if "current_itinerary_id" not in st.session_state:
    st.session_state.current_itinerary_id = None


def call_llm(prompt: str) -> dict:
    try:
        client = OpenAI(
            api_key=st.session_state.api_key,
            base_url=st.session_state.api_base_url
        )
        
        system_prompt = """你是一个专业的旅行规划助手。请根据用户的需求生成旅行计划。
必须返回纯 JSON 格式，不要包含任何其他文字。
JSON 格式如下：
{
    "itinerary_text": "详细的旅行计划文本，包括每天的行程安排、交通方式、住宿建议等，以及详细的费用预算分析",
    "coordinates": [
        {"name": "地点名称", "lat": 纬度, "lon": 经度}
    ]
}
coordinates 数组包含行程中主要地点的经纬度坐标，用于在地图上展示。"""

        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        return json.loads(content)
    except Exception as e:
        st.error(f"调用 LLM 失败: {str(e)}")
        return None


st.set_page_config(page_title="旅行规划助手", layout="wide")

with st.sidebar:
    st.title("旅行规划助手")
    
    st.divider()
    
    if not st.session_state.logged_in:
        st.subheader("用户登录")
        auth_option = st.radio("", ["登录", "注册"])
        
        if auth_option == "登录":
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            if st.button("登录"):
                user = authenticate_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_id = user.id
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
        else:
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            if st.button("注册"):
                if register_user(username, password):
                    st.success("注册成功！请登录")
                else:
                    st.error("用户名已存在")
    else:
        st.success(f"欢迎, {st.session_state.username}!")
        if st.button("退出登录"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_id = None
            st.session_state.current_itinerary_id = None
            st.rerun()
    
    st.divider()
    
    st.subheader("AI 设置")
    api_key = st.text_input("API Key", value=st.session_state.api_key, type="password")
    api_base_url = st.text_input("API Base URL", value=st.session_state.api_base_url)
    
    if st.button("保存设置"):
        st.session_state.api_key = api_key
        st.session_state.api_base_url = api_base_url
        st.success("设置已保存")


if not st.session_state.logged_in:
    st.info("请在侧边栏登录或注册以使用完整功能")
else:
    st.title("旅行规划助手")
    
    tab1, tab2 = st.tabs(["行程生成", "记账"])
    
    with tab1:
        st.header("生成旅行计划")
        
        st.subheader("输入方式")
        input_method = st.radio("选择输入方式", ["文本输入", "语音录制"])
        
        user_input = ""
        
        if input_method == "文本输入":
            user_input = st.text_area("请输入您的旅行需求", placeholder="例如：去日本5天，预算1万", height=100)
        else:
            st.write("点击下方按钮开始录制语音")
            audio = audiorecorder("点击录制", "点击停止")
            
            if len(audio) > 0:
                st.audio(audio.export().read())
                st.success("语音录制完成！")
                st.info("提示：语音转文字功能需要额外的 API 支持，当前仅支持文本输入")
        
        if st.button("生成行程") and user_input:
            if not st.session_state.api_key:
                st.error("请先在侧边栏设置 API Key")
            else:
                with st.spinner("正在生成旅行计划..."):
                    result = call_llm(user_input)
                    
                    if result:
                        st.subheader("旅行计划")
                        st.markdown(result.get("itinerary_text", ""))
                        
                        coordinates = result.get("coordinates", [])
                        if coordinates:
                            st.subheader("行程地图")
                            df = pd.DataFrame(coordinates)
                            st.map(df, latitude="lat", longitude="lon", size=200, color="#0044ff")
                            
                            content_json = json.dumps(result, ensure_ascii=False)
                            save_itinerary(st.session_state.user_id, content_json)
                            
                            latest = get_latest_itinerary(st.session_state.user_id)
                            if latest:
                                st.session_state.current_itinerary_id = latest.id
                                st.success("行程已保存！")
        
        st.divider()
        
        st.subheader("历史行程")
        itineraries = get_user_itineraries(st.session_state.user_id)
        if itineraries:
            for idx, itinerary in enumerate(reversed(itineraries[-5:])):
                with st.expander(f"行程 #{len(itineraries) - idx}"):
                    try:
                        content = json.loads(itinerary.content)
                        st.markdown(content.get("itinerary_text", ""))
                    except:
                        st.text(itinerary.content)
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button(f"删除此行程", key=f"del_itinerary_{itinerary.id}"):
                            if delete_itinerary(itinerary.id):
                                st.success("行程已删除！")
                                st.rerun()
                            else:
                                st.error("删除失败")
                    with col2:
                        if st.button(f"为此行程记账", key=f"expense_{itinerary.id}"):
                            st.session_state.current_itinerary_id = itinerary.id
                            st.success(f"已选择行程 #{len(itineraries) - idx} 进行记账")
        else:
            st.info("暂无历史行程")
    
    with tab2:
        st.header("费用记账")
        
        st.subheader("添加费用记录")
        col1, col2 = st.columns([2, 1])
        with col1:
            expense_item = st.text_input("项目", placeholder="例如：吃饭、交通、住宿")
        with col2:
            expense_amount = st.number_input("费用（元）", min_value=0.0, step=0.01, format="%.2f")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("添加记录"):
                if not expense_item:
                    st.error("请输入项目名称")
                elif expense_amount <= 0:
                    st.error("请输入有效的费用金额")
                else:
                    if add_expense(st.session_state.user_id, expense_item, expense_amount, st.session_state.current_itinerary_id):
                        st.success("费用记录已添加！")
                    else:
                        st.error("添加失败")
        with col2:
            if st.button("清除当前行程"):
                st.session_state.current_itinerary_id = None
                st.info("已清除当前行程选择")
        
        if st.session_state.current_itinerary_id:
            st.info(f"当前正在为行程 #{st.session_state.current_itinerary_id} 记账")
        
        st.divider()
        
        st.subheader("总花销")
        total = get_total_budget(st.session_state.user_id)
        st.metric("总花销", f"{total} 元")
        
        st.subheader("费用明细")
        expenses = get_user_expenses(st.session_state.user_id, st.session_state.current_itinerary_id)
        if expenses:
            for idx, expense in enumerate(expenses):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{expense.item}**")
                with col2:
                    st.write(f"¥{expense.amount:.2f}")
                with col3:
                    if st.button("删除", key=f"del_expense_{expense.id}"):
                        if delete_expense(expense.id):
                            st.success("费用记录已删除！")
                            st.rerun()
                        else:
                            st.error("删除失败")
                st.divider()
        else:
            st.info("暂无费用记录")
