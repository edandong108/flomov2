# Railway持久数据库配置指南

## 问题：每次部署后数据丢失

在Railway上，如果没有正确配置持久数据库，每次重新部署应用时都会创建一个新的临时数据库实例，导致之前的用户数据丢失。

## 解决方案：添加PostgreSQL持久服务

### 1. 添加PostgreSQL服务

1. 登录Railway控制面板 (https://railway.app)
2. 选择您的项目 (flomov2)
3. 点击"New Service"按钮
4. 选择"Database" > "PostgreSQL"
5. 等待PostgreSQL服务创建完成

### 2. 连接数据库和应用

1. 在Railway项目仪表板中，选择您的Web应用服务
2. 点击"Settings" > "Environment"
3. 在"Service Linking"部分，选择刚创建的PostgreSQL服务
4. 这将自动创建`DATABASE_URL`环境变量，指向PostgreSQL数据库

### 3. 验证环境变量

确保在Railway的环境变量中存在以下变量：
- `DATABASE_URL` - 由Railway自动设置，指向PostgreSQL数据库
- `RAILWAY_ENVIRONMENT=production`
- `DJANGO_SETTINGS_MODULE=flomo2.settings_production`

### 4. 重新部署应用

1. 触发应用重新部署
2. 检查部署日志，确保应用成功连接到数据库
3. 部署完成后，您的应用将使用持久数据库，数据不会在重新部署后丢失

### 5. 初始数据迁移

首次设置持久数据库后，您需要创建一个新账户，因为之前的数据无法恢复。

## 注意事项

- PostgreSQL服务会产生额外费用，请查看Railway的定价计划
- 定期备份数据库内容是个好习惯
- 在settings_production.py中的数据库配置已经设置为使用`DATABASE_URL`环境变量，无需修改代码

## 如何验证数据库配置

访问您的应用URL后，注册一个新账户并添加一些笔记。然后重新部署应用，验证您的账户和笔记数据是否保留。

如果需要调试，可以访问`/debug-info/?debug_token=flomo2_debug_YYYYMMDD`端点（将YYYYMMDD替换为当前日期）查看环境配置。

# Railway PostgreSQL 数据库连接指南

## 1. 添加PostgreSQL服务

1. 在Railway Dashboard中点击 `+ New`
2. 选择 `Database` → `Add PostgreSQL`
3. PostgreSQL服务会自动创建并生成连接信息

## 2. 配置数据库连接

### 自动生成的环境变量
Railway会自动创建这些变量：
- `DATABASE_URL`: 完整的PostgreSQL连接字符串
- `PGHOST`: 数据库主机
- `PGPORT`: 数据库端口
- `PGDATABASE`: 数据库名称
- `PGUSER`: 数据库用户名
- `PGPASSWORD`: 数据库密码

### Django配置
您的 `settings_production.py` 已经配置好：
```python
# 数据库配置 - 使用PostgreSQL
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
```

## 3. 服务连接方式

### 方式A: 使用Shared Variables（推荐）
1. Project Settings → Shared Variables
2. 添加 `DATABASE_URL` 变量
3. 所有服务都可以访问此变量

### 方式B: 服务级别变量
1. 点击Django服务 → Variables
2. 直接添加 `DATABASE_URL`

## 4. 数据库迁移

连接数据库后，需要运行迁移：

```bash
# Railway会自动运行这些命令（如果在build过程中配置）
python manage.py migrate
python manage.py collectstatic --noinput
```

### 在Railway中配置自动迁移
在 `railway.toml` 文件中（可选）：
```toml
[build]
builder = "nixpacks"

[deploy]
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[env]
DJANGO_SETTINGS_MODULE = "flomo2.settings_production"
RAILWAY_ENVIRONMENT = "production"
```

## 5. 验证连接

### 检查连接状态
```python
# 在Django shell中测试
python manage.py shell
>>> from django.db import connection
>>> connection.ensure_connection()
>>> print("数据库连接成功！")
```

### 查看数据库信息
访问您的应用的 `/debug-info/` 端点查看：
- 数据库引擎类型
- 连接状态
- 环境变量

## 6. 常见问题解决

### 连接超时
- 确保PostgreSQL服务正在运行
- 检查网络设置

### 迁移失败
- 确保DATABASE_URL格式正确
- 检查数据库权限

### 性能优化
```python
# settings_production.py 中添加
DATABASES['default']['CONN_MAX_AGE'] = 600  # 连接池
```

## 7. 监控和日志

在Railway中查看：
- PostgreSQL服务的日志
- Django应用的数据库查询日志
- 连接池状态 