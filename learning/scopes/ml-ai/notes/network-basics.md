# 模型结构与前向计算

本文整理 Topic 1 已讨论的结构、非线性与前向计算。符号先定义，再用同一个小网络串起公式和数值例子；实际学习状态见 `path.json`。

## 符号与量的角色

- $\mathbf{x}$：当前样本的输入向量；$x_1,x_2$ 是其中的两个分量。本文的向量按列向量理解。
- $\mathbf{W}_1,\mathbf{b}_1$：第一层的权重矩阵与偏置向量；$\mathbf{W}_2,b_2$：输出层的权重矩阵与偏置。输出只有一个数，因此 $b_2$ 写作标量。它们是训练要调整的参数。
- $w_{11}$：$\mathbf{W}_1$ 中第 $1$ 行、第 $1$ 列的一个具体权重。大写 $\mathbf{W}$ 汇总一层的权重，小写 $w$ 指其中某个数。
- $\mathbf{z}$：第一层加权求和的结果，即 $\mathbf{W}_1\mathbf{x}+\mathbf{b}_1$；还没有经过激活函数。
- $\mathbf{h}$：对 $\mathbf{z}$ 应用激活函数后的中间结果，也叫隐藏表示；$h_1,h_2,h_3$ 是三个隐藏单元的输出。
- $\hat{y}$：模型的最终预测值，读作 y-hat。
- $y$：样本的标签或目标值。

输入 $\mathbf{x}$ 来自数据；$\mathbf{z},\mathbf{h},\hat{y}$ 是当前参数下算出的结果。隐藏表示 $\mathbf{h}$ 不是独立待调的参数，它会随输入与参数重新计算。

## 从一个计算单元到一层

先看一个单元：把每个输入乘以对应权重，相加，再加上该单元的偏置，得到一个数。同样两个输入，可以交给多套不同的权重与偏置，各产生一个数。把三个这样的单元放在一层，就得到二维输入到三维输出的变换：

$$
\underbrace{\mathbf{z}}_{3\times1}
=
\underbrace{\mathbf{W}_1}_{3\times2}
\underbrace{\mathbf{x}}_{2\times1}
+
\underbrace{\mathbf{b}_1}_{3\times1}.
$$

$\mathbf{W}_1$ 的每一行对应一个单元的两个输入权重。

带偏置的 $\mathbf{W}\mathbf{x}+\mathbf{b}$ 严格叫仿射变换；机器学习里通常称为线性层。给输入追加一个固定的 $1$，可以把偏置收进扩充的权重矩阵。输出维度变大，本身不会引入非线性。

## 激活函数、隐藏层与隐藏表示

加权求和之后，可以再应用激活函数。本次具体展开的是 ReLU。对单个数 $s$，定义为：

$$
\operatorname{ReLU}(s)=\max\{0,s\}.
$$

负数变成 $0$，非负数保持原值。对向量逐分量应用，维度不变。例如：

$$
\begin{bmatrix}13\\-1\\4\end{bmatrix}
\xrightarrow{\operatorname{ReLU}}
\begin{bmatrix}13\\0\\4\end{bmatrix}.
$$

ReLU 本身没有可训练参数。sigmoid、tanh 已提及，具体性质和用途留待对应任务展开。

“隐藏层”描述在网络中的位置：处于输入与最终输出之间；“线性变换”“激活函数”描述执行的运算。常见隐藏单元先做加权求和，再经过激活函数。

下一层把 $\mathbf{h}$ 当作输入，因此它是一组中间特征。我们手工设置的例子中，三个特征分别是：

$$
\begin{aligned}
h_1&=\operatorname{ReLU}(x_1+x_2),\\
h_2&=\operatorname{ReLU}(x_1-x_2),\\
h_3&=\operatorname{ReLU}(x_2-x_1).
\end{aligned}
$$

$h_1$ 保留总和的正值部分；$h_2$ 表示 $x_1$ 超过 $x_2$ 的部分；$h_3$ 表示 $x_2$ 超过 $x_1$ 的部分。

两数相差多少，可以直接用下式输出：

$$
h_2+h_3=\lvert x_1-x_2\rvert.
$$

这里的特征作用由手工选择的权重决定；训练要解决的是怎样利用数据与损失，学出有用的权重和中间特征。

## 为什么需要非线性

单个仿射模型不能精确表达所有关系。最简单的例子是绝对值：输入 $-1,0,1$，希望分别输出 $1,0,1$。若直线在左右两点都输出 $1$，它就必须是水平线，无法在中间输出 $0$。

只叠加仿射层仍可合并：

$$
\begin{aligned}
\hat{y}
&=\mathbf{W}_2(\mathbf{W}_1\mathbf{x}+\mathbf{b}_1)+b_2\\
&=(\mathbf{W}_2\mathbf{W}_1)\mathbf{x}
  +(\mathbf{W}_2\mathbf{b}_1+b_2).
\end{aligned}
$$

加入 ReLU 后，可以表达 V 形关系：

$$
\operatorname{ReLU}(x)+\operatorname{ReLU}(-x)=\lvert x\rvert.
$$

把输入限定为 $0$ 或 $1$，差距输出还恰好实现异或 XOR：

$$
\begin{array}{cc|c|c}
x_1&x_2&y&h_2+h_3\\
\hline
0&0&0&0\\
1&0&1&1\\
0&1&1&1\\
1&1&0&0
\end{array}
$$

若要求仿射模型直接精确输出这四个目标值，前三行强制偏置为 $0$、两个权重都为 $1$，第四行就会输出 $2$，产生矛盾。

这里的限制是对原始输入做仿射变换。预先构造非线性特征，再交给线性层，也能改变表达能力；非线性可以出现在特征处理里，也可以出现在网络激活中。表达得出来与训练能否学出来，是不同的问题。

## 一个贯穿全文的小网络与前向计算

结构固定为：两个输入 → 仿射变换得到三个数 → ReLU → 仿射输出一个数。

$$
\begin{aligned}
\mathbf{z}&=\mathbf{W}_1\mathbf{x}+\mathbf{b}_1,\\
\mathbf{h}&=\operatorname{ReLU}(\mathbf{z}),\\
\hat{y}&=\mathbf{W}_2\mathbf{h}+b_2.
\end{aligned}
$$

下面使用一组手工指定的参数：

$$
\mathbf{W}_1=
\begin{bmatrix}
1&1\\
1&-1\\
-1&1
\end{bmatrix},
\qquad
\mathbf{b}_1=
\begin{bmatrix}0\\0\\0\end{bmatrix}.
$$

$$
\mathbf{W}_2=\begin{bmatrix}-1&1&1\end{bmatrix},
\qquad b_2=0.
$$

输入 $\mathbf{x}=(2,3)^\top$，按顺序代入：

1. 加权求和，得到 $\mathbf{z}$。
2. 对各分量应用 ReLU，得到 $\mathbf{h}$。
3. 用输出层组合隐藏表示，得到 $\hat{y}$。

$$
\mathbf{z}
=\begin{bmatrix}2+3\\2-3\\-2+3\end{bmatrix}
=\begin{bmatrix}5\\-1\\1\end{bmatrix},
\qquad
\mathbf{h}
=\begin{bmatrix}5\\0\\1\end{bmatrix}.
$$

$$
\hat{y}=-h_1+h_2+h_3=-5+0+1=-4.
$$

这就是前向计算：使用当前参数，从输入算出中间结果与预测。训练时再结合标签计算损失。

输出变换要匹配任务。若预测摄氏气温，最后加 ReLU 会把输出限制为非负数，无法预测负温度。隐藏层使用 ReLU 不妨碍最终输出为负：输出层的负权重或偏置仍可产生负结果。

## 理解边界

本次用具体网络与绝对值、XOR 例子讨论了结构和表达。表达得出来、训练能学出来以及能否泛化仍需分别判断；参数怎样通过数据学习，在 Topic 2 接续。

## 来源

- [Google MLCC：节点与隐藏层](https://developers.google.com/machine-learning/crash-course/neural-networks/nodes-hidden-layers)
- [Google MLCC：激活函数](https://developers.google.com/machine-learning/crash-course/neural-networks/activation-functions)
