# 📡 数据抓取 / 分析经验笔记

> 滚动记录数据抓取、解析与分析过程中的实战经验——**场景 / 方法 / 坑 / 解法 / 可复用**,供后续任务直接复用。由 `data-scraping-experience` skill 维护,按日期顺序追加。
>
> 规则:不覆盖已有条目;每条至少一个可检索标签;涉及敏感信息打码;已整理成正式文章的在条目内注明。

---

### 2026-08-09 [1]:微信文章正文抓取(绕过环境验证)

- **场景**:抓取 `mp.weixin.qq.com/s/xxx` 文章正文,存入知识库收件箱
- **方法**:`curl -sL -A "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1" <url> -o page.html`;再用 python 正则提取 `<div id="js_content">` 内容、去 HTML 标签、`html.unescape` 还原
- **坑**:`web_fetch` / 默认 UA / r.jina.ai 代理都会命中"环境异常"验证页(反爬);Google cache 也不可用
- **解法**:手机 UA 的 curl 直接拿到完整 HTML(约 3.5MB,无验证页);`og:title` meta 拿标题、`var nickname` 或 `id="js_name"` 拿公众号名;抓完用 `grep -c "环境异常"` 快速判断是否被拦
- **可复用**:
  - 微信文章一律用手机 UA curl 下载原始 HTML 再本地解析,不要用 web_fetch;
  - 解析正文:正则 `r'<div[^>]*id="js_content"[^>]*>(.*?)</div>'` + `re.sub(r'<[^>]+>', '', text)` + `html.unescape`;
  - 标题:正则 `r'<meta property="og:title" content="([^"]*)"'`;
  - 判断是否被反爬拦截:`grep -c "环境异常"` 返回 >0 则被拦。
- **标签**: `微信抓取` `反爬` `curl` `HTML解析`

---
