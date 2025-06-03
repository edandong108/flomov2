# Railway部署指南

本文档包含将Flomo-v2项目部署到Railway平台的关键步骤和配置要求。

## 必要的环境变量

在Railway项目中，需要设置以下环境变量：

| 环境变量名 | 说明 | 示例 |
|------------|------|------|
| `RAILWAY_ENVIRONMENT` | 指定为生产环境 | `production` |
| `DJANGO_SETTINGS_MODULE` | 指定使用生产设置 | `flomo2.settings_production` |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | （您的实际API密钥） |
| `SECRET_KEY` | Django密钥 | （一个长随机字符串） |
| `DATABASE_URL` | 数据库连接URL | （Railway自动提供） |

## 问题排查

### 重定向循环问题

如果遇到重定向循环问题，请确认：
- `SECURE_SSL_REDIRECT`设置为`False`（在settings_production.py中）
- `SECURE_PROXY_SSL_HEADER`已正确配置为`('HTTP_X_FORWARDED_PROTO', 'https')`

### DisallowedHost错误

如果遇到DisallowedHost错误，请确认：
- `ALLOWED_HOSTS`包含了所有需要的域名（如`.railway.app`和特定的Railway应用域名）
- 如果使用自定义域名，请将其添加到`ALLOWED_HOSTS`列表中

### API密钥问题

如果DeepSeek API功能无法正常工作：
- 验证`DEEPSEEK_API_KEY`环境变量已在Railway项目中正确设置
- 访问`/debug-info/`路径（仅在DEBUG=True时可用）检查环境变量
- 检查应用日志中是否有相关错误信息

## 部署流程

1. 确保所有代码更改已推送到GitHub仓库
2. Railway会自动部署最新的代码更改
3. 在Railway仪表板中查看部署日志，确认无错误
4. 验证应用是否可以正常访问
5. 检查核心功能是否正常工作 