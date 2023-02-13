# -*-  coding: utf-8 -*-
from sklearn import datasets  # 导入方法类
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import graphviz
from sklearn.tree import export_graphviz


iris = datasets.load_iris()  # 加载 iris 数据集
# print(iris)
iris_feature = iris.data  # 特征数据
iris_target = iris.target  # 分类数据

# 查看数据
features = pd.DataFrame(iris_feature, columns=iris.feature_names)
# print(feature)
targets = pd.DataFrame(iris_target, columns=["type"])  # 如果你的数据只有一列，对于column,需要加个中括号
# print(target)


# 划分训练集和测试集，7：3
# 方法一：按顺序人工划分
split_num = int(len(iris_feature) * 0.7)
train_feature = features[:split_num]
test_feature = features[split_num:]
train_target = targets[:split_num]
test_target = targets[split_num:]
# print(train_feature)

# 方法二：随机打乱后划分
feature_train, features_test, target_train, target_test = train_test_split(features, targets, test_size=0.3,
                                                                           random_state=42)  # random_state 参数表示乱序程度
# print(feature_train)


# 模型训练和预测
'''DecisionTreeClassifier() 模型方法中也包含非常多的参数值。例如：
    criterion = gini/entropy 可以用来选择用基尼指数或者熵来做损失函数。
    splitter = best/random 用来确定每个节点的分裂策略。支持 “最佳” 或者“随机”。
    max_depth = int 用来控制决策树的最大深度，防止模型出现过拟合。
    min_samples_leaf = int 用来设置叶节点上的最少样本数量，用于对树进行修剪。'''

model = DecisionTreeClassifier()  # 参数均置为默认状态
model.fit(feature_train, target_train) # 使用训练集训练模型
predict_results = model.predict(features_test) # 使用模型对测试


# 将预测结果和测试集的真实值分别输出，对照比较
print('predict_results:', predict_results)
print('target_test:', target_test.values.flatten())


# 通过 scikit-learn 中提供的评估计算方法查看预测结果的准确度
# 方法一：使用accuracy_score()方法
accuracy_score = accuracy_score(predict_results, target_test.values.flatten())
# print(accuracy_score)

# 方法二：使用 scikit-learn 中的分类决策树模型就带有 score 方法，只是传入的参数和 accuracy_score() 不太一致
score = model.score(features_test, target_test)
print(score)


# 画出模型
image = export_graphviz(model, out_file=None, feature_names=iris.feature_names, class_names=iris.target_names)
graph = graphviz.Source(image)
print(graph)
# 运行代码就会自动生成graphvie的dot文件:
graph.view()
