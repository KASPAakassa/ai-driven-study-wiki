# 同步知识库到钉钉文档:申请凭据 + 使用脚本

目标:把本仓库 `docs/` 下的 Markdown 知识文章同步一份到**钉钉文档知识库**(官方 OpenAPI 自动化)。
钉钉文档**没有官方 CLI**,本方案用官方开放平台 API:企业内部应用凭据(AppKey/AppSecret)→ 获取 access token → 操作知识库/文档。

## 一、申请凭据(约 10 分钟,一次性)

1. **打开开发者后台**:https://open.dingtalk.com,用钉钉扫码登录(需是组织管理员或可创建应用);
2. **创建企业内部应用**:开发者后台 → 应用开发 → 企业内部应用 → 创建应用(填名称/描述,类型选"企业内部应用");
3. **拿到 AppKey / AppSecret**:创建后进入应用详情 → "凭证与基础信息" 页,复制这两个值(**AppSecret 只显示一次,务必保存**);
4. **开通文档/知识库权限**:应用详情 → "权限管理" → 搜索并添加以下权限(申请后可能需要管理员审批):
   - 钉钉文档:创建文档、编辑文档(至少读);
   - 知识库(云文档 wiki):创建知识库、查看知识库、读写文档节点;
   - 通讯录管理:获取部门用户详情(用于拿你的 union_id,可选)。
5. **拿到你的 union_id(operatorId)**:钉钉管理后台 → 通讯录 → 你的用户详情里可见 `unionId`(一串数字);脚本用它标识"以谁的身份"创建文档。

!!! warning "凭据安全**
    AppSecret 是敏感凭证:**不要写进仓库、不要提交 git**。用环境变量传入(见下)。

## 二、使用同步脚本

```bash
# 1. 配置凭据(每次运行前,或用 .env 加载)
export DINGTALK_APP_KEY="你的AppKey"
export DINGTALK_APP_SECRET="你的AppSecret"
export DINGTALK_OPERATOR_UID="你的union_id"

# 2. 先预览计划(不调用钉钉 API)
python3 tools/dingtalk_sync.py --dry-run

# 3. 正式同步:扫描 docs/ 下所有 .md(排除 inbox 的 *-source.md),
#    在钉钉知识库创建/更新同名文档
python3 tools/dingtalk_sync.py
```

## 三、脚本说明与边界

- **扫描范围**:`docs/` 下所有 `.md`,排除 `inbox/` 的 `*-source.md`(原始存档)与 `index.md`(可配置);
- **同步策略**:按相对路径生成文档标题(`03-agents/agent-intro` → 文档名);已存在则更新,不存在则创建;
- **知识库**:脚本会用钉钉 wiki API 查找/创建名为「AI 驱动的学习 Wiki」的知识库(可配置 `--workspace`);
- **格式**:Markdown 正文按原样上传(钉钉文档支持 Markdown 渲染;`!!! admonition` 等 MkDocs 语法会显示为引用,不报错);
- **幂等**:每个文档带内容 hash,内容未变跳过(省 API 调用);
- **当前状态**:本地扫描/清单/幂等逻辑已可用;API 调用函数已封装,具体端点以钉钉开放平台文档为准(https://open.dingtalk.com/document/orgapp/knowledge-base-related-interfaces),拿到凭据后联调。

## 四、常见问题

| 问题 | 处理 |
| --- | --- |
| 401 Unauthorized | AppKey/AppSecret 错误,或应用未开通对应权限 |
| 403 无权限 | 到应用"权限管理"补开文档/知识库权限,等待审批生效 |
| 找不到 union_id | 管理后台通讯录用户详情;或调 contact API `GET /v1.0/contact/users/{userId}` |
| 想同步到指定知识库 | 脚本 `--workspace <名称>` 指定;或先手工建知识库再同步 |

## 五、维护

- 同步是"一份快照"关系,不是双向同步;钉钉侧改动不会回写;
- 建议每次知识库更新后手动跑一次,或加 cron(注意 access token 2 小时过期,脚本每次自动获取);
- 内容以本仓库 Markdown 为准,钉钉侧为分发副本。
