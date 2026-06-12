# Auto Brand Article Writer - One per boot

每次 OpenClaw 启动后运行（每 3 小时检查一次），从耳机品牌统计.xlsx 中按顺序取一个还没写过的品牌，生成推荐文章。

## 工作流程

1. 用 python 读取 `C:\Users\yu\Desktop\耳机品牌统计.xlsx` 的「蓝牙耳机品牌」sheet
2. 读取 `C:\Users\yu\Desktop\earbuds-review\.brand-tracker.json`，找到下一个 `done: false` 的品牌
3. 获取该品牌的 核心定位、一句话亮点、市场地位
4. 根据这些信息写一篇 MDX 文章，推荐 3-5 款该品牌的耳机
5. 文章格式参考 `C:\Users\yu\Desktop\earbuds-review\src\content\articles\apple-earbuds-recommend-2026.mdx`
6. 购买链接统一放在底部按钮区域，没有真实链接用 `#` 代替
7. 保存到 `src/content/articles/{品牌slug}-earbuds-recommend-2026.mdx`
8. 更新 `.brand-tracker.json` 把该品牌标记为 done
9. cd 到项目目录：`git add -A && git commit -m "add {品牌名} earbuds recommendation article" && git push`
10. 如果所有品牌都写完了，回复"所有品牌已全部完成"，不要继续处理

## 文章 slug 规则

- 小米 → xiaomi
- 漫步者 → edifier
- OPPO/一加 → oppo-oneplus
- 索尼 → sony
- Bose → bose
- 韶音 → shokz
- JBL → jbl
- Beats → beats
- 三星 → samsung
- QCY → qcy
- FIIL → fiil
- HIFIMAN → hifiman
- 水月雨 → moondrop
- SoundPEATS → soundpeats
- 飞傲 → fiio
- 万魔 → 1more
- 倍思 → baseus
- 塞那 → sanag
- 科大讯飞 → iflytek
- Nothing/CMF → nothing
- IKF → ikf
- Linklike → linklike
- 击音 → jiyin
- 金运 → jinyun
- DALI/达尼 → dali
- QoA → qoa
- 粤声 → yuesheng
- 丽弦 → lixian
- 原道 → yuandao
- 瓷音未来 → ciying
- MORROR ART → morror
- 虹觅 → hongmi
- Newyu → newyu
- 渡哲特 → duzhete

## 文章目录

保存到 `C:\Users\yu\Desktop\earbuds-review\src\content\articles\`

## 购买链接

购买链接统一放在文章末尾的 `<div class="flex flex-wrap gap-4 mt-6">` 区域。
如果没有真实购买链接，用 `href="#"` 占位，按钮文字用「查看{产品名}价格 →」
