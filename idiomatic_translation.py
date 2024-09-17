import json
import time
import requests


OPENROUTER_API_KEY = ""

system_prompt="""
# Role: 专业翻译优化器

## Profile
- author: Linus Turing
- version: 3.0
- language: 中文/英文
- description: 你是一位精通简体中文和英文的翻译优化器，擅长分析直译结果中存在的问题，并给出优化后的意译结果，使其更加通俗易懂且符合中文表达习惯。你会进行两次反思迭代，确保最终输出的翻译结果最为精准。

## Skills
1. 精通简体中文和英文的翻译与优化能力。
2. 擅长分析并指出直译中的问题，提供更符合中文表达习惯的意译结果。
3. 对学术术语和专业内容有深入理解，能够准确传达原文的核心思想。
4. 拥有反思能力，能够对初步翻译结果进行深度分析与优化。

## Rules
1. 分析直译结果，找出不符合中文表达习惯的地方、语句不通顺的地方、晦涩难懂的地方，并进行优化。
2. 意译时要准确传达原文的事实和背景，但可以调整语序和表达方式，使其更易理解。
3. 保留术语和公司缩写，例如 FLAC，JPEG，Microsoft，Amazon，OpenAI 等。
4. 人名不翻译。
5. 保留引用的论文，例如 [20] 这样的引用。
6. 对于 Figure 和 Table，翻译的同时保留原有格式，例如：“Figure 1: ”翻译为“图 1: ”，“Table 1: ”翻译为“表 1: ”。
7. 全角括号换成半角括号，并在左括号前面加半角空格，右括号后面加半角空格。
8. 输入格式为 Markdown 格式，输出格式也必须保留原始 Markdown 格式。
9. 第一次出现的专业术语，要在括号里面写上英文原文，例如：“生成式 AI (Generative AI)”，之后可以只写中文。
10. 使用 AI 相关术语词汇对应表（比如：LLM/Large Language Model -> 大语言模型）进行翻译。

## Workflows
1. **分析直译**：对比英文原文和直译结果，指出直译中的具体问题，包括但不限于：
    - 不符合中文表达习惯的地方，明确指出不符合之处。
    - 语句不通顺的地方，指出位置。
    - 晦涩难懂的地方，尝试给出解释。
2. **优化意译**：根据第一次反思分析的结果，重新进行意译，保证原意的基础上，使其更易理解，更符合中文表达习惯，保持原有格式不变。
3. **反思意译**：对优化后的意译结果进行二次反思，分析其是否仍存在可以进一步优化的地方，例如：
    - 是否还有不符合中文表达习惯的地方。
    - 是否有可以进一步简化或优化的表达方式。
    - 是否有遗漏或误解原意的情况。
4. **最终输出**：根据第二次反思分析的结果，进一步优化翻译内容，确保其准确性和表达的自然流畅。

## OutputFormat
```json
{
    "OriginalText": "原文",
    "LiteralTranslation": "直译结果",
    "Issues": [
        "直译的具体问题1",
        "直译的具体问题2",
        "直译的具体问题3",
        "直译的具体问题4",
        "直译的具体问题5"
    ],
    "OptimizedTranslation": "优化后的意译结果",
    "ReflectionIssues": [
        "意译的具体问题1",
        "意译的具体问题2",
        "意译的具体问题3",
        "意译的具体问题4",
        "意译的具体问题5"
    ],
    "FinalTranslation": "最终优化后的翻译结果"
}
```
"""


def get_final_translation(OriginalText, LiteralTranslation):
    user_prompt = f"""
    英文原文: {OriginalText}
    直译结果: {LiteralTranslation}
    请根据具备的技能（Skills），基于工作流程（Workflow），来完成翻译任务。输出格式为(OutputFormat)，以json输出。
    """
    
    # Maximum number of retries
    max_retries = 3
    retry_delay = 2  # seconds between retries
    attempt = 0

    while attempt < max_retries:
        try:
            # Make the request to the translation API
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}"
                },
                data=json.dumps({
                    #"model": "openai/gpt-4o-2024-08-06",
                    #"model": "openai/gpt-4o-mini-2024-07-18",
                    "model": "qwen/qwen-2-72b-instruct",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt }
                    ]
                })
            )
            
            # Check if the response status code indicates an error
            response.raise_for_status()
            
            # Extract and return the final translation
            return response.json()["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            # Increment the attempt counter
            attempt += 1
            print(f"Attempt {attempt} failed: {e}")
            
            # If maximum retries reached, raise the exception
            if attempt >= max_retries:
                raise Exception("Maximum retry limit reached. Could not complete the request.") from e
            
            # Wait before retrying
            time.sleep(retry_delay)


def process_translations(input_file_name, output_file_name):
    # 读取 JSON 文件
    with open(input_file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 用于存放最终的字典数据
    final_data = []

    # 遍历列表中的每一个字典
    for index, item in enumerate(data, start=1):
        index_value = item.get('index')
        input_value = item.get('input')
        output_value = item.get('output')

        # 最大重试次数
        max_retries = 3

        # 初始化重试次数
        retry_count = 0

        while retry_count < max_retries:
            try:
                # 获取最终翻译
                final_translation = get_final_translation(input_value, output_value)
                
                # 去除开头的 ```json 和结尾的 ```
                final_translation = final_translation.strip()[7:-3]
                
                # 将字符串转换为 Python 字典
                final_translation = json.loads(final_translation)
                
                # 添加一个index字段
                final_translation['index'] = index_value
                
                # 成功时退出循环
                break
            
            except Exception as e:
                # 打印错误信息（可选）
                print(f"Error occurred: {e}")
                
                # 增加重试次数
                retry_count += 1
                
                # 检查是否达到最大重试次数
                if retry_count >= max_retries:
                    print("Reached maximum retries, skipping this translation.")
                    final_translation = { 
                                        "OriginalText": input_value, 
                                        "LiteralTranslation": output_value, 
                                        "final_translation": "Error occurred during translation.",
                                        "index": index_value
                                        }
                    break

        final_data.append(final_translation)

        # 每 5 个字典将数据写入文件
        if index % 5 == 0 or index == len(data):
            # 如果文件已经存在，读取现有内容
            try:
                with open(output_file_name, 'r', encoding='utf-8') as output_file:
                    existing_data = json.load(output_file)
            except FileNotFoundError:
                # 文件不存在时，初始化为空列表
                existing_data = []

            # 将新数据追加到现有内容中
            existing_data.extend(final_data)

            # 写回文件
            with open(output_file_name, 'w', encoding='utf-8') as output_file:
                json.dump(existing_data, output_file, ensure_ascii=False, indent=4)

            # 打印写入信息
            print(f"Written {len(final_data)} items to {output_file_name}. Total items so far: {len(existing_data)}")

            # 清空 final_data 列表以便继续处理下一个批次
            final_data = []

    print(f"Final translations have been written to {output_file_name}")

# 示例调用
if __name__ == "__main__":
    input_file = "arxiv_qwen2_7b_translated.json"
    output_file = "final_translations.json"
    process_translations(input_file, output_file)
