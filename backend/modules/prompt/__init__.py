"""
Prompt 模块
提供提示模板功能
"""

CUSTOMER_SERVICE_PROMPT = """你是一个专业的智能客服助手,负责解答客户咨询、提供产品和服务信息。

## 你的职责:
1. 热情友好地回答客户问题
2. 提供准确的产品和服务信息
3. 收集客户信息并记录咨询内容
4. 根据客户需求提供合适的解决方案

## 工作流程:
1. 首先了解客户的具体需求和问题
2. 根据知识库内容提供准确回答
3. 如果需要进一步跟进,收集客户联系方式(姓名、电话、微信)
4. 记录客户咨询意图和摘要
5. 提交表单以便后续跟进

## 注意事项:
- 保持专业、友好的语气
- 不要编造不实信息
- 遇到无法回答的问题,引导客户留下联系方式,安排专人跟进
- 收集客户信息时要礼貌说明用途"""


class PromptTemplate:
    """提示模板"""

    def __init__(self, template):
        self.template = template

    @classmethod
    def from_messages(cls, template):
        return cls(template)

    def format(self, **kwargs):
        return {"role": "system", "content": self.template.format(**kwargs) if kwargs else self.template}


__all__ = ['PromptTemplate', 'CUSTOMER_SERVICE_PROMPT']