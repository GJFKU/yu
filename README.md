# 🎧 耳机评测站

蓝牙耳机、头戴式耳机、降噪耳机评测与推荐网站。

**站点：** https://earbuds-review.pages.dev

## 技术栈

- **框架：** [Astro](https://astro.build) v6 (静态站点)
- **样式：** [Tailwind CSS](https://tailwindcss.com) v4
- **内容：** MDX
- **部署：** [Cloudflare Pages](https://pages.cloudflare.com)
- **CI/CD：** GitHub Actions（推送到 `master` 自动部署）

## 本地开发

```bash
npm install        # 安装依赖
npm run dev        # 启动本地服务 http://localhost:4321
npm run build      # 构建到 dist/
npm run preview    # 本地预览构建结果
```

## 部署流程

推送到 GitHub `master` 分支后自动触发部署：

```
git add .
git commit -m "新文章"
git push
```

CI 自动执行：`npm ci` → `npm run build` → `wrangler pages deploy`

## 项目结构

```
src/
├── assets/            # 静态资源
├── components/        # Astro 组件
├── content/           # MDX 文章
├── data/              # 数据文件
├── layouts/           # 布局模板
├── pages/             # 页面路由
├── styles/            # 全局样式
└── content.config.ts  # 内容集合配置
```

## SEO

- ✅ Sitemap: `https://earbuds-review.pages.dev/sitemap-index.xml`
- ✅ Google Search Console 已验证
- ✅ 结构化语义标签

## 环境变量

| 变量 | 说明 |
|------|------|
| `CLOUDFLARE_API_TOKEN` | Cloudflare API 令牌（GitHub Secret） |
| `CLOUDFLARE_ACCOUNT_ID` | `3402daeab80cd7951bdafea3a9c0217f` |

## GitHub 仓库

https://github.com/GJFKU/yu
