"""
Airtable API 模块
负责与 Airtable 数据库交互,提交客户表单数据
"""

import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Airtable 配置(示例配置,使用时请替换为实际值)
AIRTABLE_API_TOKEN = os.getenv('AIRTABLE_API_TOKEN', 'YOUR_AIRTABLE_API_TOKEN')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID', 'YOUR_BASE_ID')
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'Customers')

# API 端点
AIRTABLE_API_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"


class AirtableAPI:
    """Airtable API 封装类"""
    
    def __init__(self, api_token=None, base_id=None, table_name=None):
        """初始化 Airtable API"""
        self.api_token = api_token or AIRTABLE_API_TOKEN
        self.base_id = base_id or AIRTABLE_BASE_ID
        self.table_name = table_name or AIRTABLE_TABLE_NAME
        
        self.api_url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def submit_customer_record(self, name, phone, wechat=None, address=None, summary=None, intention=None):
        """
        提交客户记录到 Airtable
        
        参数:
            name: 客户姓名 (必填)
            phone: 联系电话 (必填)
            wechat: 微信号 (可选)
            address: 地址 (可选)
            summary: 咨询摘要 (可选,可由 AI 生成)
            intention: 咨询意图 (可选)
        
        返回:
            dict: 包含提交状态和记录 ID
        """
        # 构建记录数据
        fields = {
            "Name": name,
            "Phone": phone,
        }
        
        # 添加可选字段
        if wechat:
            fields["WeChat"] = wechat
        if address:
            fields["Address"] = address
        if summary:
            fields["Summary"] = summary
        if intention:
            fields["Intention"] = intention
        
        # 构建请求体
        payload = {
            "records": [
                {
                    "fields": fields
                }
            ]
        }
        
        try:
            # 发送 POST 请求
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            
            # 检查响应
            if response.status_code == 200:
                result = response.json()
                record_id = result['records'][0]['id']
                print(f"✓ 客户记录提交成功, ID: {record_id}")
                return {
                    "success": True,
                    "record_id": record_id,
                    "message": "记录已成功提交"
                }
            else:
                error_msg = response.json().get('error', {}).get('message', '未知错误')
                print(f"✗ 提交失败: {error_msg}")
                return {
                    "success": False,
                    "record_id": None,
                    "message": f"提交失败: {error_msg}"
                }
                
        except Exception as e:
            print(f"✗ 提交异常: {e}")
            return {
                "success": False,
                "record_id": None,
                "message": f"提交异常: {str(e)}"
            }
    
    def get_record(self, record_id):
        """获取单条记录"""
        url = f"{self.api_url}/{record_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"获取记录失败: {e}")
            return None
    
    def list_records(self, max_records=100):
        """列出记录"""
        params = {"maxRecords": max_records}
        try:
            response = requests.get(self.api_url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"获取记录列表失败: {e}")
            return None


# 全局实例
_airtable_api = None

def get_airtable_api():
    """获取 Airtable API 单例"""
    global _airtable_api
    if _airtable_api is None:
        _airtable_api = AirtableAPI()
    return _airtable_api


# 便捷函数
def submit_form(name, phone, wechat=None, address=None, summary=None, intention=None):
    """便捷函数:直接提交表单"""
    api = get_airtable_api()
    return api.submit_customer_record(name, phone, wechat, address, summary, intention)
