# BPLab AI CMA 立即可用版

大连标普检测有限公司实验室电子原始记录系统。

## 功能
- 11项：表面粗糙度、金瓷结合三点弯曲、X射线内部质量、翘曲、热膨胀、急冷急热、弯曲性能、维氏硬度、厚度测量、色稳定性、金相切割。
- 删除两个视觉检验。
- 无Logo、免登录、单实验/单样品加载，适合较旧平板。
- 输出直接使用 `templates` 内原始CMA记录表。
- 可下载JSON草稿，重新导入后继续填写。

## Streamlit Cloud
- 入口文件：`app.py`
- Python：3.12
- 首次部署：新建GitHub仓库，将本文件夹内全部内容上传后部署。
- 更新：在原仓库使用 Add file → Upload files，上传新版本同名文件并 Commit changes；Streamlit会自动更新。

## 注意
免费Streamlit Cloud本地文件不作为唯一长期存储。每次完成后请下载Word与JSON草稿归档。
