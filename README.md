# IPTV 自动维护 → Cloudflare Pages

把 [Guovin/iptv-api](https://github.com/Guovin/iptv-api) 的"抓取 + 测速 + 过滤 + 生成 m3u"引擎，
跑在 **GitHub Actions**（无需自建服务器），结果自动发布到 **Cloudflare Pages**，
投影仪/平板上的播放器只认一个固定地址，源怎么变都不用再碰。

## 已就绪的 Cloudflare 资源（已创建）
- Pages 项目：`jakmz-iptv`（子域 `jakmz-iptv.pages.dev`）
- 自定义域名：`iptv.jakmz.de5.net`（DNS CNAME 已加，已验证可正常访问）
- 部署后访问地址：
  - `https://iptv.jakmz.de5.net/result.m3u`（推荐，自定义域）
  - `https://jakmz-iptv.pages.dev/result.m3u`（备用）
  - 同时提供 `result.txt`；EPG（`/epg.xml`）当前未生成，可选（需要时再开 `open_epg` 并补充 EPG 源）

## 你需要补的最后一步：GitHub Secrets
在 GitHub 仓库 **Settings → Secrets and variables → Actions** 添加两个：
- `CLOUDFLARE_API_TOKEN` = 你的 CF 令牌（`cfut_…`，需含 **Pages Write** 权限；现有令牌已满足）
- `CLOUDFLARE_ACCOUNT_ID` = `b6511939508dcd267ef7dfe9e318c189`

## 播放器（投影仪用 TiviMate）
- **TiviMate**（投影仪/Android TV 首选，遥控器体验好）：添加播放列表 → 选 **M3U 播放列表** → 填
  `https://iptv.jakmz.de5.net/result.m3u` → 完成。
- **安卓平板**：TiviMate 同样可装；或装 **IPTV Smarters / TBox**（触屏操作更顺手）。同样填上面的 M3U 地址。
- EPG 可选填：`https://iptv.jakmz.de5.net/epg.xml`（当前未生成，留空即可）。

## 过滤与安全（对应用户要求）
- **无成人内容**：`config/demo.txt` 是频道白名单模板，当前只列 **央视频道 / 卫视频道 / 广东频道** 的干净频道名；
  模板里没列的频道（含任何成人台）在"对频道"匹配阶段即被丢弃，不会进结果。
- **无违法广告**：`config/user_config.ini` 中 `open_filter_ad = True`，自动剔除广告/无信号循环占位源。
- **质量过滤已放宽**：分辨率(720p)、速率(0.5MiB/s) 两道过滤当前**关闭**，目的是让匹配到的干净频道尽量多进来
  （播放器自身有缓冲，慢源可手动切）；安全底线仍由上面的白名单 + 广告过滤兜底。
- 结果通过公开 URL 可访问（URL 即密码）；若要进一步隐藏，可把地址当私密保管，或后续接入 CF Access（需 Zero Trust，当前未启用）。

## 自动化
- 每 12 小时自动跑一次（`cron: "0 */12 * * *"`）。
- 也可在 Actions 页面点 **Run workflow** 手动触发（改了 config 后立刻生效）。
- 改频道分组/订阅源：编辑 `config/` 后手动触发一次即可。

## 本地调试（省 Cloudflare 额度）
- 转换器 `scripts/mk_m3u.py` 是纯 Python，**可完全本地验证、无需跑 Actions**：
  1. 准备 `output/result.txt`（用真实引擎产物或手造样例）；
  2. `python3 scripts/mk_m3u.py` → 生成 `site/result.m3u`；
  3. 检查 `#EXTINF` 数量、分组、是否误收 junk/成人频道。
  改转换器逻辑时先本地跑通再提交，能省下每次远程部署额度。
- 注：iptv-api **引擎本身需要 Docker**（本机无 Docker 环境），所以改 `config/user_config.ini` /
  `subscribe.txt` / `demo.txt` 这类「影响抓取结果」的配置，仍需一次远程运行才能看到真实产出；
  建议把这类改动**攒一批再触发一次**，避免频繁消耗额度。

## 目录
- `.github/workflows/deploy.yml` — Actions：跑引擎 → 发 Pages
- `config/user_config.ini` — 过滤/输出配置
- `config/subscribe.txt` — 订阅源（通用国内源，不含成人源）
