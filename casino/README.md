# casino (Frontend)

基于 Vue 3 + Vue CLI 的在线游戏前端，已接入后端 API（Django + DRF）。

## 包含游戏：
- 龙虎斗
- 轮盘
- 21点
- 骰子
- 百家乐
- 捕鱼
- 持续更新主流游戏（含CS开箱玩法，区块链玩法）...

## 预览
- 旧静态预览（仅演示 UI，不含后端）：`https://xzgame888.netlify.app/`

## 功能
- 用户注册/登录（JWT）
- 个人中心：余额、最近投注、最近交易
- 充值/提现
- 游戏大厅与若干示例游戏（21 点、百家乐、轮盘、龙虎斗、捕鱼、骰子）

## 重要说明：路径与存储
- 已将 `@/` 等绝对路径改为相对路径，移动目录不再失效
- 原本的“假存储”（localStorage/sessionStorage）已逐步替换为后端 API：
  - Auth 登录/注册：走 `/api/accounts/login/`、`/api/accounts/register/`
  - 余额/充值/提现：走 `/api/accounts/balance/`、`/api/accounts/deposit/`、`/api/accounts/withdraw/`
  - 投注记录与统计：走 `/api/bets/records/`、`/api/bets/statistics/`

## 环境要求
- Node.js 16+/18+
- pnpm（推荐）或 npm/yarn
- 本地运行需后端 API 在线（默认 `http://localhost:8000/api`）

## 安装
```bash
pnpm install
# 或
npm install
```

## 开发
```bash
# 启动前端（默认 http://localhost:8080）
pnpm serve
# 或
npm run serve
```

确保后端已在 `http://localhost:8000` 启动，否则登录与数据接口将报 401。

## 打包
```bash
pnpm build
# 或
npm run build
```

## 代码格式化
```bash
pnpm lint
# 或
npm run lint
```

## 与后端对接
- 统一 API 客户端：`src/utils/api.js`（Axios 实例，自动附带 `Authorization: Bearer <token>`）
- 登录/注册：`src/components/AuthModal.vue`
- 首页状态与 token 刷新：`src/views/Home.vue`
- 个人中心：`src/views/UserProfile.vue`（余额、最近投注、最近交易、提现）
- 充值页：`src/views/Deposit.vue`
- 投注历史：`src/views/BettingHistory.vue`

如需修改后端地址，请编辑：`src/utils/api.js`
```js
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
});
```

## 常见问题
- 启动时报 `Can't resolve 'axios'`：请执行 `pnpm add axios`。
- 登录后接口 401：清空浏览器 localStorage 后重试；确认后端运行且 CORS 开启。
- 图片资源路径 404：已从 `@/assets` 改为相对路径，请确保未新增绝对路径引用。

## 开发建议
- 生产中请将 API baseURL 指向线上域名，并限制后端 CORS 源
- 对接更多游戏时，统一通过后端 `bets/create/` 写入投注记录

