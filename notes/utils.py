import requests
import json
import urllib3
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from notes.models import Note

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 添加导师角色配置
MENTOR_ROLES = {
    "munger": {
        "name": "查理·芒格",
        "system_prompt": "你是查理·芒格，作为一个投资大师和思想家，你以多元思维模型闻名。请基于用户的记录，运用你的思维模型和人生经验，给出具体的建议。重点关注心理学、商业逻辑和决策思维方面的指导。"
    },
    "zeng": {
        "name": "曾国藩",
        "system_prompt": "你是曾国藩，你写过那么多家书来教育家庭成员，请将用户当作你的家人一样，给到一些人生职场的建议指导。请用温和但不失严谨的语气，给出具体可行的建议。"
    }
}

def generate_cache_key(user_id, mentor_type, notes_hash):
    """生成缓存键
    Args:
        user_id: 用户ID
        mentor_type: 导师类型
        notes_hash: 笔记内容的哈希值
    """
    today = timezone.now().strftime('%Y-%m-%d')
    return f"mentor_advice:{user_id}:{mentor_type}:{notes_hash}:{today}"

def get_notes_hash(notes_text):
    """生成笔记内容的哈希值"""
    import hashlib
    return hashlib.md5(notes_text.encode()).hexdigest()

def get_mentor_advice(recent_notes, mentor_type="zeng", force_refresh=False):
    """获取星图导师的建议
    Args:
        recent_notes: 最近的笔记列表
        mentor_type: 导师类型，可选值：munger（芒格）, zeng（曾国藩）
        force_refresh: 是否强制刷新缓存
    """
    # 将最近的笔记内容组合成文本
    if not recent_notes:
        print("没有找到最近的笔记")
        return "请先记录一些笔记，让我来为你提供建议..."
        
    notes_text = "\n".join([note.content for note in recent_notes if note and note.content])
    if not notes_text.strip():
        print("笔记内容为空")
        return "最近没有记录任何笔记内容，请先记录一些想法..."

    # 生成缓存键
    notes_hash = get_notes_hash(notes_text)
    cache_key = generate_cache_key(recent_notes[0].user.id, mentor_type, notes_hash)
    
    # 如果不是强制刷新，尝试从缓存获取
    if not force_refresh:
        cached_advice = cache.get(cache_key)
        if cached_advice:
            print("从缓存获取建议")
            return cached_advice

    API_KEY = getattr(settings, 'DEEPSEEK_API_KEY', None)
    if not API_KEY:
        print("未配置API密钥")
        return "系统未配置API密钥，请联系管理员..."

    API_URL = "https://api.deepseek.com/v1/chat/completions"
    
    print(f"准备发送的笔记内容: {notes_text[:100]}...")  # 只打印前100个字符
    
    # 获取选定导师的提示词
    mentor = MENTOR_ROLES.get(mentor_type, MENTOR_ROLES["zeng"])
    
    # 构建系统角色和用户输入
    messages = [
        {
            "role": "system",
            "content": mentor["system_prompt"]
        },
        {
            "role": "user",
            "content": f"这是我最近的一些记录和想法，请给我一些建议：\n{notes_text}"
        }
    ]

    # 准备请求数据
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800,
        "stream": False
    }

    # 设置请求头
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        print("开始创建会话...")
        # 创建会话
        session = requests.Session()
        session.verify = False  # 禁用 SSL 验证
        
        print("开始发送请求...")
        # 发送请求
        response = session.post(
            API_URL,
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"收到响应状态码: {response.status_code}")
        # 检查响应状态
        if response.status_code != 200:
            print(f"API返回错误状态码: {response.status_code}")
            print(f"错误响应: {response.text}")
            if response.status_code == 401:
                return "API 密钥无效或已过期，请联系管理员..."
            elif response.status_code == 429:
                return "API 调用次数超限，请稍后再试..."
            elif response.status_code >= 500:
                return "API 服务器出现问题，请稍后再试..."
            return "服务暂时不可用，请稍后再试..."
        
        print("开始解析响应...")
        # 解析响应
        try:
            result = response.json()
            print(f"解析结果: {str(result)[:200]}...")  # 只打印前200个字符
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {str(e)}")
            return "服务返回了无效的数据格式..."
            
        if result and "choices" in result and result["choices"]:
            advice = result["choices"][0]["message"]["content"]
            print(f"成功获取建议: {advice[:100]}...")  # 只打印前100个字符
            
            # 将结果存入缓存，设置过期时间为当天结束
            today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
            cache_timeout = int((today_end - timezone.now()).total_seconds())
            cache.set(cache_key, advice, cache_timeout)
            
            return advice
        else:
            print(f"API返回数据格式错误: {result}")
            return "无法解析服务返回的数据..."
            
    except requests.exceptions.SSLError as e:
        print(f"SSL错误: {str(e)}")
        return "网络连接不安全，请稍后再试..."
    except requests.exceptions.Timeout:
        print("请求超时")
        return "服务响应超时，请稍后再试..."
    except requests.exceptions.ConnectionError as e:
        print(f"连接错误: {str(e)}")
        return "无法连接到服务器，请检查网络..."
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {str(e)}")
        return "请求发生错误，请稍后再试..."
    except Exception as e:
        print(f"未知错误: {str(e)}")
        return "发生未知错误，请稍后再试..."

def get_mentor_insights(user, mentor_type="zeng", force_refresh=False):
    """获取星图导师的见解，包括最近笔记和建议
    Args:
        user: 用户对象
        mentor_type: 导师类型，可选值：munger（芒格）, zeng（曾国藩）
        force_refresh: 是否强制刷新缓存
    """
    try:
        print(f"开始获取用户 {user.username} 的星图导师见解...")
        # 获取用户最近的5条笔记
        recent_notes = Note.objects.filter(user=user).order_by('-created_at')[:5]
        print(f"找到 {recent_notes.count()} 条最近笔记")
        
        # 获取导师建议
        print(f"开始获取{MENTOR_ROLES[mentor_type]['name']}的建议...")
        mentor_advice = get_mentor_advice(recent_notes, mentor_type, force_refresh)
        print(f"成功获取导师建议: {mentor_advice[:100]}...")  # 只打印前100个字符
        
        result = {
            'success': True,
            'recent_notes': recent_notes,
            'mentor_advice': mentor_advice,
            'mentor_name': MENTOR_ROLES[mentor_type]['name']
        }
        print("成功生成结果数据")
        return result
    except Exception as e:
        print(f"获取星图导师见解时出错: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        } 