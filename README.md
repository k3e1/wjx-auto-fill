## Fill-Questionnaire

### 简介

该项目使用selenium实现问卷自动填写。支持IP切换、题项比例设定以及问卷填写方式(通过微信、QQ还是链接填写)

### 实现思路

![image-20240216194754592](C:\Users\zz\AppData\Roaming\Typora\typora-user-images\image-20240216194754592.png)

#### 1.爬取问卷

```python
driver = webdriver.Edge()
driver.get(url)
```

