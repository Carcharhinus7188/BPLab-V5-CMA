# 更新现有GitHub仓库和Streamlit应用

本次不需要新建仓库，也不需要新建Streamlit应用，原网址保持不变。

## 1. 备份旧仓库

在GitHub旧仓库点击 `Code` → `Download ZIP`，保存旧版本。

## 2. 更新GitHub

1. 解压本项目ZIP。
2. 打开原GitHub仓库。
3. 点击 `Add file` → `Upload files`。
4. 在Finder中打开解压后的文件夹，按 `Command + A` 全选文件夹内全部内容并拖入上传区。
5. 同名文件会被覆盖；新增文件会被加入。
6. Commit message填写：`Update BPLab CMA 11-item final version`。
7. 点击 `Commit changes`。

建议确保仓库根目录直接看到：

- `app.py`
- `schemas.py`
- `calculations.py`
- `word_export.py`
- `requirements.txt`
- `templates/`
- `.streamlit/`

## 3. 删除旧版冲突文件

如旧仓库仍有以下文件，可在GitHub中删除：

- `database.py`
- `experiments.py`
- `pages/`
- `core/`
- 旧版 `assets/`

删除方式：进入文件，点击垃圾桶图标，提交变更。文件夹中的文件全部删除后，文件夹会自动消失。

## 4. Streamlit自动更新

GitHub提交后等待约1～3分钟，原Streamlit应用会自动更新。

若仍显示旧版：

1. Streamlit后台进入 `My apps`。
2. 选择原应用。
3. 点击 `Manage app` → `Reboot app`。
4. 手机或平板彻底关闭旧网页，重新打开；必要时使用无痕模式。

## 5. 部署设置

- Branch：`main`
- Main file path：`app.py`
- Python：建议 `3.12`

## 6. 使用提示

- 每完成一个步骤先点击保存。
- 定期下载JSON草稿，防止云端会话结束导致未下载数据丢失。
- 完成后下载Word和JSON，并按实验室记录控制程序归档。
- 免费Streamlit Cloud不应作为CMA记录的唯一长期存储位置。
