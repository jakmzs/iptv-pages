# IPTV 自动维护 → Cloudflare Pages

把 [Guovin/iptv-api](https://github.com/Guovin/iptv-api) 的"抓取 + 测速 + 过滤 + 生成 m3u"引擎，
跑在 **GitHub Actions**（无需自建服务器），结果自动发布到 **Cloudflare Pages**，
投影仪/平板上的播放器只认一个固定地址，源怎么变都不用再碰。

## 已就绪的 Cloudflare 资源（已创建）
- Pages 项目：`jakmz-iptv`（子域 `jakmz-iptv.pages.dev`）
- 自定义域名：`iptv.jakmz.de5.net`（DNS CNAME 已加，待 CF 验证生效）
- 部署后访问地址：
  - `https://iptv.jakmz.de5.net/result.m3u`（推荐，自定义域）
  - `https://jakmz-iptv.pages.dev/result.m3u`（备用）
  - 同时提供 `result.txt`；EPG：`/epg.xml`

## 你需要补的最后一步：GitHub Secrets
在 GitHub 仓库 **Settings → Secrets and variables → Actions** 添加两个：
- `CLOUDFLARE_API_TOKEN` = 你的 CF 令牌（`cfut_…`，需含 **Pages Write** 权限；现有令牌已满足）
- `CLOUDFLARE_ACCOUNT_ID` = `b6511939508dcd267ef7dfe9e318c189`

## 播放器（投影仪用 TiviMate）
添加播放列表 → M3U → 填 `https://iptv.jakmz.de5.net/result.m3u`
EPG 可选填：`https://iptv.jakmz.de5.net/epg.xml`

## 过滤与安全（对应用户要求）
- **无成人内容**：`config/demo.txt` 是频道模板，只列央视/卫视/港澳台/电影/体育/动画/游戏/音乐/经典剧场；
  模板里没列的频道（含任何成人台）在"对频道"阶段即被丢弃，不会进结果。
- **无违法广告**：`config/user_config.ini` 中 `open_filter_ad = True`，自动剔除广告/无信号循环占位源；
  另叠加 分辨率≥720p + 速率≥0.5MiB/s 过滤。
- 结果通过公开 URL 可访问（URL 即密码）；若要进一步隐藏，可把地址当私密保管，或后续接入 CF Access（需 Zero Trust，当前未启用）。

## 自动化
- 每 12 小时自动跑一次（`cron: "0 */12 * * *"`）。
- 也可在 Actions 页面点 **Run workflow** 手动触发（改了 config 后立刻生效）。
- 改频道分组：编辑 `config/` 后手动触发一次即可。

## 目录
- `.github/workflows/deploy.yml` — Actions：跑引擎 → 发 Pages
- `config/user_config.ini` — 过滤/输出配置
- `config/subscribe.txt` — 订阅源（通用国内源，不含成人源）
