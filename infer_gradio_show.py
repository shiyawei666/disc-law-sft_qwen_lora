import gradio as gr
import requests
import json
from typing import Optional


class VLLMClient:
    def __init__(self, server_url="http://localhost:8000",
                 model_name="qwen-lora-awq", api_key: Optional[str] = None):
        self.server_url = server_url
        self.model_name = model_name
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def stream_generation(self, messages, temperature=0.7, max_tokens=800,
                          top_p=0.9):
        """流式生成文本"""
        url = f"{self.server_url}/v1/chat/completions"

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": True
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers,
                                     stream=True)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data != '[DONE]':
                            try:
                                chunk = json.loads(data)
                                if 'choices' in chunk and chunk['choices']:
                                    delta = chunk['choices'][0].get('delta',
                                                                    {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield f"错误: {str(e)}"


# 创建客户端实例 - 微调前和微调后
client_before = VLLMClient(server_url="http://192.168.182.79:8099",
                           model_name="qwen32-ds-v3-icf-int4",
                           api_key="gpustack_7a1039ec63b76881_ec45a4f760292ce227970bc4306db740")  # 微调前模型
client_after = VLLMClient(model_name="qwen-lora-awq")  # 微调后模型

# 模型显示名称
MODEL_NAMES = {
    "before": {
        "display_name": "🎯 微调前模型",
        "server_info": f"服务地址: {client_before.server_url}",
        "model_info": f"模型名称: {client_before.model_name}"
    },
    "after": {
        "display_name": "🚀 微调后模型",
        "server_info": f"服务地址: {client_after.server_url}",
        "model_info": f"模型名称: {client_after.model_name}"
    }
}


def convert_to_gradio_format(history):
    """将历史记录转换为 Gradio 格式"""
    gradio_history = []
    for user_msg, assistant_msg in history:
        gradio_history.append({"role": "user", "content": user_msg})
        gradio_history.append({"role": "assistant", "content": assistant_msg})
    return gradio_history


def convert_from_gradio_format(gradio_history):
    """将 Gradio 格式转换回内部列表格式"""
    history = []
    for i in range(0, len(gradio_history), 2):
        if i + 1 < len(gradio_history):
            user_msg = gradio_history[i]["content"]
            assistant_msg = gradio_history[i + 1]["content"]
            history.append([user_msg, assistant_msg])
    return history


def stream_chat_compare(message, history_before, history_after, temperature,
                        max_tokens):
    """流式聊天函数 - 对比模式"""
    # 将 Gradio 格式转换回内部格式
    history_before_internal = convert_from_gradio_format(history_before)
    history_after_internal = convert_from_gradio_format(history_after)

    # 构建消息历史
    messages_before = []
    for user_msg, assistant_msg in history_before_internal:
        messages_before.append({"role": "user", "content": user_msg})
        messages_before.append({"role": "assistant", "content": assistant_msg})
    messages_before.append({"role": "user", "content": message})

    messages_after = []
    for user_msg, assistant_msg in history_after_internal:
        messages_after.append({"role": "user", "content": user_msg})
        messages_after.append({"role": "assistant", "content": assistant_msg})
    messages_after.append({"role": "user", "content": message})

    # 同时生成两个模型的响应
    full_response_before = ""
    full_response_after = ""

    # 创建生成器
    gen_before = client_before.stream_generation(
        messages=messages_before,
        temperature=temperature,
        max_tokens=max_tokens
    )

    gen_after = client_after.stream_generation(
        messages=messages_after,
        temperature=temperature,
        max_tokens=max_tokens
    )

    # 交替获取两个模型的响应
    while True:
        try:
            chunk_before = next(gen_before)
            full_response_before += chunk_before
        except StopIteration:
            pass

        try:
            chunk_after = next(gen_after)
            full_response_after += chunk_after
        except StopIteration:
            pass

        # 转换为 Gradio 格式
        history_before_new = history_before_internal + [
            [message, full_response_before]]
        history_after_new = history_after_internal + [
            [message, full_response_after]]

        gradio_before = convert_to_gradio_format(history_before_new)
        gradio_after = convert_to_gradio_format(history_after_new)

        # 检查是否都完成生成
        both_done = False
        try:
            next(gen_before)
        except StopIteration:
            try:
                next(gen_after)
            except StopIteration:
                both_done = True

        yield gradio_before, gradio_after

        if both_done:
            break


def stream_chat_single(message, gradio_history, temperature, max_tokens,
                       client_type="before"):
    """单模型流式聊天函数"""
    client = client_before if client_type == "before" else client_after

    # 将 Gradio 格式转换回内部格式
    history = convert_from_gradio_format(gradio_history)

    # 构建消息历史
    messages = []
    for user_msg, assistant_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})
    messages.append({"role": "user", "content": message})

    # 流式生成
    full_response = ""
    for chunk in client.stream_generation(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
    ):
        full_response += chunk
        # 转换为 Gradio 格式
        history_new = history + [[message, full_response]]
        gradio_history_new = convert_to_gradio_format(history_new)
        yield gradio_history_new


def generate_text_compare(prompt_text, temp, tokens):
    """对比文本生成"""
    messages = [{"role": "user", "content": prompt_text}]

    result_before = ""
    result_after = ""

    # 生成微调前模型响应
    for chunk in client_before.stream_generation(
            messages=messages,
            temperature=temp,
            max_tokens=tokens
    ):
        result_before += chunk

    # 生成微调后模型响应
    for chunk in client_after.stream_generation(
            messages=messages,
            temperature=temp,
            max_tokens=tokens
    ):
        result_after += chunk

    return result_before, result_after


# 创建高级界面
with gr.Blocks(theme=gr.themes.Monochrome(),
               title="模型微调对比系统") as advanced_demo:
    gr.Markdown("""
    # 🤖 模型微调对比系统

    **对比微调前后模型的性能差异**
    """)

    with gr.Tab("🔄 实时对比模式"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 参数配置")
                temperature = gr.Slider(0.1, 2.0, value=0.7, label="创造性")
                max_tokens = gr.Slider(100, 2000, value=800, label="生成长度")
                top_p = gr.Slider(0.1, 1.0, value=0.9, label="Top-P")

                # 模型信息展示
                gr.Markdown("### 📋 模型信息")
                with gr.Group():
                    gr.Markdown(f"**{MODEL_NAMES['before']['display_name']}**")
                    gr.Markdown(MODEL_NAMES['before']['server_info'])
                    gr.Markdown(MODEL_NAMES['before']['model_info'])

                    gr.Markdown("---")

                    gr.Markdown(f"**{MODEL_NAMES['after']['display_name']}**")
                    gr.Markdown(MODEL_NAMES['after']['server_info'])
                    gr.Markdown(MODEL_NAMES['after']['model_info'])

            with gr.Column(scale=2):
                gr.Markdown(f"### {MODEL_NAMES['before']['display_name']}")
                chatbot_before = gr.Chatbot(
                    label=f"{MODEL_NAMES['before']['display_name']} - {MODEL_NAMES['before']['model_info']}",
                    height=400,
                    type="messages",
                    show_copy_button=True
                )

            with gr.Column(scale=2):
                gr.Markdown(f"### {MODEL_NAMES['after']['display_name']}")
                chatbot_after = gr.Chatbot(
                    label=f"{MODEL_NAMES['after']['display_name']} - {MODEL_NAMES['after']['model_info']}",
                    height=400,
                    type="messages",
                    show_copy_button=True
                )

        with gr.Row():
            msg_compare = gr.Textbox(
                label="输入消息",
                placeholder="输入问题，同时对比两个模型的回答...",
                scale=4
            )
            send_compare_btn = gr.Button("发送对比", scale=1,
                                         variant="primary")

    with gr.Tab("📊 独立测试模式"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 参数配置")
                temp_single = gr.Slider(0.1, 2.0, value=0.7, label="创造性")
                max_tokens_single = gr.Slider(100, 2000, value=800,
                                              label="生成长度")
                model_choice = gr.Radio(
                    choices=[
                        f"{MODEL_NAMES['before']['display_name']} ({MODEL_NAMES['before']['model_info']})",
                        f"{MODEL_NAMES['after']['display_name']} ({MODEL_NAMES['after']['model_info']})"
                    ],
                    label="选择测试模型",
                    value=f"{MODEL_NAMES['before']['display_name']} ({MODEL_NAMES['before']['model_info']})"
                )
                clear_single_btn = gr.Button("清空对话", variant="secondary")

                # 当前选中模型信息
                gr.Markdown("### 🔍 当前模型信息")
                model_info_display = gr.Markdown()

            with gr.Column(scale=2):
                chatbot_single = gr.Chatbot(
                    label="对话历史",
                    height=500,
                    type="messages",
                    show_copy_button=True
                )

        with gr.Row():
            msg_single = gr.Textbox(
                label="输入消息",
                placeholder="与选定模型对话...",
                scale=4
            )
            send_single_btn = gr.Button("发送", scale=1, variant="primary")

    with gr.Tab("📝 文本生成对比"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 生成参数")
                temp_gen = gr.Slider(0.1, 2.0, value=0.7, label="创造性")
                max_tokens_gen = gr.Slider(100, 2000, value=800,
                                           label="生成长度")
                generate_compare_btn = gr.Button("生成对比", variant="primary")

                # 模型信息
                gr.Markdown("### 📋 对比模型")
                with gr.Group():
                    gr.Markdown(f"**{MODEL_NAMES['before']['display_name']}**")
                    gr.Markdown(MODEL_NAMES['before']['server_info'])
                    gr.Markdown(MODEL_NAMES['before']['model_info'])

                    gr.Markdown("---")

                    gr.Markdown(f"**{MODEL_NAMES['after']['display_name']}**")
                    gr.Markdown(MODEL_NAMES['after']['server_info'])
                    gr.Markdown(MODEL_NAMES['after']['model_info'])

            with gr.Column(scale=1):
                prompt_compare = gr.Textbox(
                    label="输入提示词",
                    placeholder="描述您想要生成的内容...",
                    lines=5
                )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown(f"### {MODEL_NAMES['before']['display_name']}")
                generated_before = gr.Textbox(
                    label=f"{MODEL_NAMES['before']['model_info']}",
                    lines=8,
                    show_copy_button=True
                )

            with gr.Column(scale=1):
                gr.Markdown(f"### {MODEL_NAMES['after']['display_name']}")
                generated_after = gr.Textbox(
                    label=f"{MODEL_NAMES['after']['model_info']}",
                    lines=8,
                    show_copy_button=True
                )

        clear_gen_btn = gr.Button("清空所有", variant="secondary")


    # 更新模型信息显示的函数
    def update_model_info(choice):
        if "微调前模型" in choice:
            return f"""
            **当前选中模型信息:**
            - {MODEL_NAMES['before']['display_name']}
            - {MODEL_NAMES['before']['server_info']}
            - {MODEL_NAMES['before']['model_info']}
            """
        else:
            return f"""
            **当前选中模型信息:**
            - {MODEL_NAMES['after']['display_name']}
            - {MODEL_NAMES['after']['server_info']}
            - {MODEL_NAMES['after']['model_info']}
            """


    # 事件处理 - 实时对比模式
    send_compare_btn.click(
        fn=stream_chat_compare,
        inputs=[msg_compare, chatbot_before, chatbot_after, temperature,
                max_tokens],
        outputs=[chatbot_before, chatbot_after]
    ).then(lambda: "", outputs=msg_compare)


    # 事件处理 - 独立测试模式
    def get_single_model_type(choice):
        return "before" if "微调前模型" in choice else "after"


    # 绑定模型选择变化事件
    model_choice.change(
        fn=update_model_info,
        inputs=model_choice,
        outputs=model_info_display
    )

    # 初始化模型信息显示
    advanced_demo.load(
        fn=lambda: update_model_info(model_choice.value),
        outputs=model_info_display
    )

    send_single_btn.click(
        fn=stream_chat_single,
        inputs=[msg_single, chatbot_single, temp_single, max_tokens_single,
                gr.State(value=get_single_model_type(model_choice.value))],
        outputs=chatbot_single
    ).then(lambda: "", outputs=msg_single)

    # 清空独立测试模式对话
    clear_single_btn.click(
        fn=lambda: [],
        outputs=[chatbot_single]
    )

    # 事件处理 - 文本生成对比
    generate_compare_btn.click(
        fn=generate_text_compare,
        inputs=[prompt_compare, temp_gen, max_tokens_gen],
        outputs=[generated_before, generated_after]
    )


    # 清空文本生成对比
    def clear_all():
        return "", "", "", ""


    clear_gen_btn.click(
        fn=clear_all,
        outputs=[prompt_compare, generated_before, generated_after]
    )

    # 添加一些使用说明
    with gr.Accordion("📖 使用说明", open=False):
        gr.Markdown(f"""
        ## 使用指南

        ### 🔄 实时对比模式
        - 同时向微调前后的两个模型发送相同的问题
        - 实时观察两个模型的响应差异
        - 适合快速比较模型性能

        ### 📊 独立测试模式  
        - 单独测试某个模型的性能
        - 可以更深入地了解特定模型的行为
        - 适合详细的功能测试

        ### 📝 文本生成对比
        - 对比两个模型在文本生成任务上的表现
        - 适合创意写作、内容生成等场景

        ## 模型信息
        - **{MODEL_NAMES['before']['display_name']}**: 
          - {MODEL_NAMES['before']['server_info']}
          - {MODEL_NAMES['before']['model_info']}

        - **{MODEL_NAMES['after']['display_name']}**: 
          - {MODEL_NAMES['after']['server_info']}
          - {MODEL_NAMES['after']['model_info']}
        """)

if __name__ == "__main__":
    advanced_demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
    )