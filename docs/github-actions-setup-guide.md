# GitHub Actions Secrets 设置指南

为了使需求变更邮件通知工作流正常运行，您需要在 GitHub 仓库中设置以下 Secrets:

## 必须的 Secrets

1. **EMAIL_USERNAME**
   - 这是用于发送邮件的 Microsoft Live/Outlook 账户邮箱地址
   - 例如: `your.name@outlook.com` 或 `your.name@live.com`

2. **EMAIL_PASSWORD**
   - 账户密码或应用专用密码（如果您启用了双重认证）
   - 推荐使用应用密码以提高安全性

## 设置步骤

1. 在您的 GitHub 仓库页面，点击 "Settings"（设置）选项卡
2. 在左侧菜单中，选择 "Secrets and variables" > "Actions"
3. 点击 "New repository secret" 按钮
4. 添加 `EMAIL_USERNAME` 和对应的值
5. 再次点击 "New repository secret"，添加 `EMAIL_PASSWORD` 和对应的值

## 安全注意事项

- 请使用专用的邮箱账户用于自动化邮件发送
- 如有可能，为此账户启用双重认证并使用应用专用密码
- 定期更新密码和应用专用密码以增强安全性

## 测试工作流

设置完成后，您可以通过以下方式测试工作流:

1. 创建一个新的 Issue
2. 添加 "requirement" 或 "feature" 标签
3. 检查是否收到自动发送的邮件通知
4. 验证 Issue 是否已被添加到项目看板
5. 验证是否在 Issue 上自动添加了评论
