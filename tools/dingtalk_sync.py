#!/usr/bin/env python3
"""钉钉文档知识库同步脚本:把 docs/ 下 Markdown 同步到钉钉文档知识库(官方 OpenAPI)。

凭据(环境变量,敏感,勿入库):
    DINGTALK_APP_KEY      钉钉企业内部应用 AppKey
    DINGTALK_APP_SECRET   钉钉企业内部应用 AppSecret
    DINGTALK_OPERATOR_UID 你的 union_id(operatorId)

用法:
    python3 tools/dingtalk_sync.py --dry-run            # 只打印计划,不调 API
    python3 tools/dingtalk_sync.py [--root docs] [--workspace "AI 驱动的学习 Wiki"]

申请凭据与权限见 tools/DINGTALK_SYNC.md。
API 端点基于钉钉开放平台官方 SDK(@alicloud/dingtalk),具体以
https://open.dingtalk.com/document/orgapp/knowledge-base-related-interfaces 为准。
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = "https://api.dingtalk.com"
EXCLUDE_SUFFIX = ("-source.md", "_template.md")
EXCLUDE_NAMES = {"index.md", "README.md", "tasks.md"}


# ---------- 钉钉 OpenAPI 封装(凭据就绪后生效) ----------
def get_access_token(app_key: str, app_secret: str) -> str:
    """POST /v1.0/oauth2/accessToken -> {accessToken, expireIn}"""
    body = json.dumps({"appKey": app_key, "appSecret": app_secret}).encode()
    req = urllib.request.Request(
        f"{BASE}/v1.0/oauth2/accessToken", data=body,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    return data["accessToken"]


def api(method: str, path: str, token: str, body=None, params=None):
    """通用请求:带 x-acs-dingtalk-access-token 头。"""
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Content-Type": "application/json",
                 "x-acs-dingtalk-access-token": token})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


# ---------- 本地扫描(已可用) ----------
def collect_md(root: str):
    """扫描 root 下所有 .md,返回 (相对路径, 绝对路径) 列表;排除 inbox/存档/索引。"""
    files = []
    for dirpath, _dirnames, names in os.walk(root):
        for name in names:
            if not name.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            if "inbox" in rel.split(os.sep):
                continue                       # 跳过收件箱(待整理素材)
            if name in EXCLUDE_NAMES or name.endswith(EXCLUDE_SUFFIX):
                continue
            files.append((rel, os.path.join(dirpath, name)))
    return sorted(files)


def content_hash(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


# ---------- 同步流程 ----------
def main():
    ap = argparse.ArgumentParser(description="同步 docs/ 到钉钉文档知识库")
    ap.add_argument("--root", default="docs", help="Markdown 根目录(默认 docs)")
    ap.add_argument("--workspace", default="AI 驱动的学习 Wiki", help="钉钉知识库名称")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划,不调用钉钉 API")
    args = ap.parse_args()

    files = collect_md(args.root)
    if not files:
        print("未找到可同步的 Markdown(检查 --root)")
        sys.exit(1)

    print(f"将同步 {len(files)} 个文档到知识库「{args.workspace}」:")
    for rel, path in files:
        print(f"  - {rel}  (hash {content_hash(path)})")

    if args.dry_run:
        print("\n[dry-run] 结束:未调用钉钉 API。")
        return

    app_key = os.environ.get("DINGTALK_APP_KEY")
    app_secret = os.environ.get("DINGTALK_APP_SECRET")
    operator = os.environ.get("DINGTALK_OPERATOR_UID")
    if not (app_key and app_secret and operator):
        print("缺少凭据:请设置 DINGTALK_APP_KEY / DINGTALK_APP_SECRET / DINGTALK_OPERATOR_UID")
        print("申请步骤见 tools/DINGTALK_SYNC.md")
        sys.exit(2)

    # 凭据就绪后,在此完成:
    #   token = get_access_token(app_key, app_secret)
    #   1) wiki API 查找/创建知识库 workspace(按名称)
    #   2) 对每个文档:查是否存在(按相对路径作标题)→ 存在则更新,否则创建
    #   3) 用 content_hash 跳过内容未变的文档(幂等)
    # 端点参考:
    #   GET/POST /v2.0/wiki/workspaces   (知识库)
    #   doc_2_0: 创建/更新文档节点(具体方法名以官方文档为准)
    print("凭据已配置,但 API 联调端点需按钉钉开放平台最新文档确认后启用。")
    print("当前版本:本地扫描/清单/幂等逻辑可用;API 部分待凭据联调。")


if __name__ == "__main__":
    main()
