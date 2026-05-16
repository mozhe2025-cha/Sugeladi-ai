import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

st.title("🎓 苏格拉底式学习导师")

# 定义系统提示词：这是苏格拉底法的精髓
SOCRATIC_SYSTEM_PROMPT = """
你是一位精通苏格拉底教学法的导师。你的目标是帮助学生通过批判性思维进行自我测试和学习。
请遵循以下准则：
1. **永远不要直接给出答案**。
2. 始终通过层层递进的问题引导学生思考。
3. 如果学生回答正确，给予肯定并追问一个更具深度的问题以拓展其思维。
4. 如果学生回答错误，引导他们发现逻辑漏洞，或者提供一个相关的类比，让他们自己意识到错误。
5. 当你感觉学生已经掌握了知识点后，可以给出总结并进行下一个知识点的测试。
"""
import streamlit as st

# ... (先前的导入代码)

# 1. 侧边栏设置
st.sidebar.header("⚙️ 教学设置")

# 定义可供选择的主题和难度
topic = st.sidebar.selectbox("选择学科", ["编程 (Python)", "数学", "历史", "英语语法"])
difficulty = st.sidebar.select_slider("难度等级", options=["入门", "基础", "进阶", "专家"])

# 2. 构建动态系统提示词
def get_system_prompt(topic, difficulty):
    return f"""
    你是一位精通苏格拉底教学法的导师，专注于教学 {topic}。
    当前的难度等级是：{difficulty}。
    
    指导原则：
    1. 永远不要直接给出答案。
    2. 如果难度是[入门]，请使用生活中的类比来解释概念。
    3. 如果难度是[专家]，请要求学生展示推导过程或反思逻辑漏洞。
    4. 始终通过层层递进的问题引导学生思考。
    """

# 3. 监听设置变化以重置对话
# 如果用户改变了设置，我们应该清空之前的对话，以免上下文冲突
if "last_config" not in st.session_state:
    st.session_state.last_config = (topic, difficulty)

if st.session_state.last_config != (topic, difficulty):
    st.session_state.messages = [] # 清空历史
    st.session_state.last_config = (topic, difficulty)
    st.rerun()

# 4. 初始化对话历史 (放入更新后的 System Message)
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [
        {"role": "system", "content": get_system_prompt(topic, difficulty)}
    ]

# 初始化 LLM
llm = ChatOpenAI(
    model='deepseek-chat',
    # 替换掉原本硬编码的 api_key = "..."
# 这样代码里就不会出现敏感信息了
api_key = st.secrets["DEEPSEEK_API_KEY"],

    openai_api_base='https://api.deepseek.com',
    streaming=True
)

# 1. 初始化对话历史 (放入 System Message)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SOCRATIC_SYSTEM_PROMPT}
    ]

# 2. 显示历史消息 (只显示 User 和 Assistant，隐藏 System)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 3. 处理输入
if prompt := st.chat_input("告诉我你想测试的知识点 (例如：Python的装饰器)"):
    # 显示并保存用户消息
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI 回复
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # 将整个对话历史发给 AI，这样它才知道自己刚才问了什么
        response = llm.invoke(st.session_state.messages)
        full_response = response.content
        
        message_placeholder.markdown(full_response)
    
    # 保存助手回复
    st.session_state.messages.append({"role": "assistant", "content": full_response})