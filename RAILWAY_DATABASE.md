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