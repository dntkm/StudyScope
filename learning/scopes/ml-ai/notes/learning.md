# 学习目标与训练机制

本文整理 Topic 2 已讨论的训练基础与损失函数例子。先明确符号和贯穿示例，再分别说明求梯度、更新参数及它们的适用条件；实际学习状态见 `path.json`。

## 符号与量的角色

- $\mathbf{x}$：当前样本的输入向量；$x_1,x_2$ 是其中的两个分量。本文的向量按列向量理解。
- $\mathbf{W}_1,\mathbf{b}_1$：第一层的权重矩阵与偏置向量；$\mathbf{W}_2,b_2$：输出层的权重矩阵与偏置。输出只有一个数，因此 $b_2$ 写作标量。它们是训练要调整的参数。
- $w_{11}$：$\mathbf{W}_1$ 中第 $1$ 行、第 $1$ 列的一个具体权重。大写 $\mathbf{W}$ 汇总一层的权重，小写 $w$ 指其中某个数。
- $\mathbf{z}$：第一层加权求和的结果，即 $\mathbf{W}_1\mathbf{x}+\mathbf{b}_1$；还没有经过激活函数。
- $\mathbf{h}$：对 $\mathbf{z}$ 应用激活函数后的中间结果，也叫隐藏表示；$h_1,h_2,h_3$ 是三个隐藏单元的输出。
- $\hat{y}$：模型的最终预测值，读作 y-hat。
- $y$：样本的标签或目标值。
- $L$：根据预测与目标算出的标量损失。
- $g$：损失对某个标量参数的导数；$\mathbf{g}$：全部参数对应的梯度向量。
- $\eta$：学习率，控制更新尺度。
- $\boldsymbol{\theta}$：把全部可训练参数合在一起的参数向量；$\mathbf{d}$ 是在参数空间中选择的一个移动方向。
- $n$：一个 batch 中的样本数，也就是一次更新使用的样本数。后文用 $i$ 表示样本编号。
- $m,\beta$：动量优化器保存的历史梯度累积值、历史保留系数；在优化器一节使用。

输入 $\mathbf{x}$、标签 $y$ 来自数据；$\mathbf{z},\mathbf{h},\hat{y},L$ 是本次计算结果。这里统一使用 $\mathbf{W}_1,\mathbf{b}_1,\mathbf{W}_2,b_2$，以免在不同权重记号间切换。

## 沿用的网络与当前样本

沿用 Topic 1 的两输入、三隐藏单元、一输出网络：

$$
\begin{aligned}
\mathbf{z}&=\mathbf{W}_1\mathbf{x}+\mathbf{b}_1,\\
\mathbf{h}&=\operatorname{ReLU}(\mathbf{z}),\\
\hat{y}&=\mathbf{W}_2\mathbf{h}+b_2.
\end{aligned}
$$

当前参数为：

$$
\mathbf{W}_1=
\begin{bmatrix}1&1\\1&-1\\-1&1\end{bmatrix},
\qquad
\mathbf{b}_1=
\begin{bmatrix}0\\0\\0\end{bmatrix}.
$$

$$
\mathbf{W}_2=\begin{bmatrix}-1&1&1\end{bmatrix},
\qquad b_2=0.
$$

对于输入 $\mathbf{x}=(2,3)^\top$，前向结果是 $\mathbf{z}=(5,-1,1)^\top$、$\mathbf{h}=(5,0,1)^\top$、$\hat{y}=-4$。下面用标签 $y=-6$ 讨论训练。

## 从预测到损失，再反向求梯度

假设上述样本的标签是 $y=-6$，采用：

$$
L=\frac12(\hat{y}-y)^2.
$$

当前误差为 $2$，损失为 $2$。乘 $\frac12$ 是为了让导数简洁，不改变该目标的最优位置。

反向传播沿前向依赖关系逆向应用链式法则，计算损失对各参数的梯度。先看输出层。对于第 $j$ 个输出权重，$j\in\{1,2,3\}$：

$$
\begin{aligned}
\frac{\partial L}{\partial\hat{y}}&=\hat{y}-y=2,\\
\frac{\partial\hat{y}}{\partial(\mathbf{W}_2)_{1,j}}&=h_j,\\
\frac{\partial L}{\partial(\mathbf{W}_2)_{1,j}}&=2h_j.
\end{aligned}
$$

因此，输出层权重矩阵的梯度与它自身形状相同，是一个行向量；偏置的导数是标量：

$$
\nabla_{\mathbf{W}_2}L
=\begin{bmatrix}10&0&2\end{bmatrix},
\qquad
\frac{\partial L}{\partial b_2}=2.
$$

把当前 $\mathbf{h}$ 当作给定特征，这一步就是平方损失线性回归的求导。整个网络还需要继续向前层求导，因为 $\mathbf{h}$ 本身也由可训练参数生成。

只沿第一隐藏单元追一条路径：

$$
w_{11}\longrightarrow z_1\longrightarrow h_1
\longrightarrow\hat{y}\longrightarrow L.
$$

$$
\begin{aligned}
\frac{\partial L}{\partial w_{11}}
&=\frac{\partial L}{\partial\hat{y}}
  \frac{\partial\hat{y}}{\partial h_1}
  \frac{\partial h_1}{\partial z_1}
  \frac{\partial z_1}{\partial w_{11}}\\
&=2\cdot(-1)\cdot1\cdot2=-4.
\end{aligned}
$$

四个因子分别是：损失对预测的导数、输出层第一个权重、ReLU 在 $z_1=5>0$ 处的导数、输入 $x_1=2$。普通梯度下降会把 $w_{11}$ 调大；这使 $h_1$ 增大，经负的输出权重作用后，预测降低，朝 $-6$ 靠近。

反向传播中也会计算损失对 $\mathbf{z},\mathbf{h}$ 等中间结果的导数，以便继续往前求导。优化器最终调整的是参数。当前样本的 $h_2=0$，使连接它的输出权重梯度为零；换个输入，$h_2$ 可能非零，这不表示该参数永远无法学习。

## 为什么先求完梯度，再更新参数

一次标准梯度下降更新中，各参数梯度描述同一个更新前的模型状态。梯度可以按层依次计算并保存，求导所使用的数值应对应这次前向计算。

例如，上述 $w_{11}$ 的梯度为：

$$
\frac{\partial L}{\partial w_{11}}
=2\cdot(-1)\cdot1\cdot2=-4.
$$

如果先把输出层第一个权重从 $-1$ 改成 $-1.1$，再拿它继续旧的求导链，就会得到：

$$
2\cdot(-1.1)\cdot1\cdot2=-4.4.
$$

这里旧预测对应的导数与新权重混在一起，已不是旧参数点的梯度。

标准顺序是：当前参数做前向 → 对应损失做反向并保存梯度 → 优化器更新参数 → 新参数用于下一次前向。如果采用先改一部分参数、再调整另一部分的方案，需要重新计算对应状态下的预测与梯度。

## 一个 batch 怎样构成一个 step

一次更新使用 $n$ 个样本时，常采用平均损失。记第 $i$ 个样本的损失为 $L_i$，它对全部参数的梯度为 $\mathbf{g}_i=\nabla_{\boldsymbol{\theta}}L_i$：

$$
\begin{aligned}
L_{\mathrm{batch}}&=\frac1n\sum_{i=1}^{n}L_i,\\
\mathbf{g}_{\mathrm{batch}}
&=\nabla_{\boldsymbol{\theta}}L_{\mathrm{batch}}
=\frac1n\sum_{i=1}^{n}\mathbf{g}_i.
\end{aligned}
$$

这些样本使用同一组当前参数。按样本看，要产生 $n$ 份预测；实现时通常把样本组成 batch，执行一次批量前向。因此标准 step 是：

$n$ 个样本 → 批量前向 → 平均损失 → 一次反向 → 一次参数更新。

一次反向已包含这一批所有样本的贡献。例如，对同一个参数，两个样本的梯度是 $+4,-2$，平均为 $+1$，普通梯度下降倾向把参数调小。一次更新可以改善某些样本，同时牺牲另一些样本；梯度给出的是批次平均损失的局部下降方向。

## 梯度与优化器更新量

反向传播给出梯度，优化器根据梯度、内部历史状态与超参数决定更新方向和幅度。在固定模型结构与训练目标下，它尝试寻找损失较低的参数。下面用下标 $\mathrm{old},\mathrm{new}$ 表示更新前后。

只考虑损失梯度、不含动量和其他附加项的 SGD 使用：

$$
w_{\mathrm{new}}=w_{\mathrm{old}}-\eta g.
$$

学习率固定时，零梯度使该参数不变，小梯度对应小更新，大梯度对应大更新，可能跨过合适位置。

动量 Momentum 保存历史梯度的加权累积。$m$ 是历史累积值，$\beta$ 是历史保留系数。一种常见写法是：

$$
\begin{aligned}
m_{\mathrm{new}}&=\beta m_{\mathrm{old}}+g,\\
w_{\mathrm{new}}&=w_{\mathrm{old}}-\eta m_{\mathrm{new}}.
\end{aligned}
$$

连续同方向的贡献会累积，方向变化时贡献可能部分抵消。例如：

$$
m_{\mathrm{old}}=4,\qquad \beta=0.9,\qquad g=0.
$$

$$
m_{\mathrm{new}}=0.9\cdot4+0=3.6.
$$

当 $\eta=0.1$ 时，参数仍减少 $0.36$。因此当前梯度为零，不一定意味着这一步参数不动。

某个参数梯度为零，也不能说明整个模型已最优。每步损失都下降、最终收敛、达到局部最优，都需要条件与观察，不能仅凭使用优化器推断。训练目标降低与真实任务表现改善，还需要分别评估。

Adam、梯度消失与爆炸的具体机制和处理方法尚未展开。当前关于小梯度、大梯度与更新幅度的直接比例关系，特指上面的普通 SGD。

## 损失怎样影响预测倾向

先固定极简模型：无论输入是什么，都输出同一个数字 $a$。历史耗时是 $(2,3,3,4,18)$ 分钟，各样本权重相同。这里 $y_i$ 表示第 $i$ 条观测，样本数为 $5$。

绝对损失与平方损失分别为：

$$
L_{\mathrm{abs}}(a)=\sum_{i=1}^{5}\lvert a-y_i\rvert,
\qquad
L_{\mathrm{sq}}(a)=\sum_{i=1}^{5}(a-y_i)^2.
$$

- 绝对损失：$L_{\mathrm{abs}}(3)=17$，$L_{\mathrm{abs}}(6)=24$。
- 平方损失：$L_{\mathrm{sq}}(3)=227$，$L_{\mathrm{sq}}(6)=182$。

分别比较同一种损失下的候选预测。对于这个固定输出的模型，绝对损失在中位数 $3$ 处最小，平方损失在平均值 $6$ 处最小。除以固定的样本数不改变最优位置；不同损失的数值及单位不能直接比较大小。

选择中位数不要求先删除 $18$，也不要求认定它是错误记录。它可能是真实慢任务，仍参与计算；是否属于数据错误需要额外证据。

把 $18$ 改成 $180$，绝对损失仍偏好 $3$，平方损失偏好平均值 $38.4$。看预测从 $3$ 调到 $4$ 的变化，记损失变化为 $\Delta L$：

- 总绝对损失：前四条增加 $2$，最后一条减少 $1$，合计增加 $1$。
- 总平方损失：前四条增加 $4$，最后一条减少 $177^2-176^2=353$，合计变化为 $4-353=-349$。

绝对损失下，在移动没有跨过数据值的区间，每个等权样本对再挪一步的影响大小相同；平方损失下，大误差带来更大的局部变化幅度。如果数据变成 $(2,3,180,180,180)$，绝对损失也会偏好 $180$：从 $3$ 调到 $4$，两条小值合计增加 $2$，三条大值合计减少 $3$，总变化为 $\Delta L=-1$。拉远一个点与增加远处样本数量，是不同的变化。

业务可以区分错误方向。例如低估每分钟罚 $3$ 分、高估每分钟罚 $1$ 分。记单个样本的损失为 $\ell(a,y)$：

$$
\ell(a,y)=
\begin{cases}
3(y-a),&a<y,\\
a-y,&a\ge y.
\end{cases}
$$

原数据 $(2,3,3,4,18)$ 中，从预测 $3$ 调到 $4$，变化是：

$$
\Delta L=1+1+1-3-3=-3.
$$

总代价从 $49$ 降到 $46$。继续从 $4$ 往 $18$ 移动，前四条每分钟合计多罚 $4$，最后一条少罚 $3$，总代价开始增加，因此新目标偏好 $4$。

报 $18$ 可以不低于这五条历史耗时，但不能保证未来不出现更长耗时。数据描述样本，损失规定错误代价，优化在模型能表达的范围内寻找较低损失的参数。

## 梯度方向与学习率的局部边界

对于可微损失，当前参数为 $\boldsymbol{\theta}$，梯度为 $\mathbf{g}=\nabla_{\boldsymbol{\theta}}L$。沿 $\mathbf{d}$ 移动足够小的一步，取 $\eta>0$：

$$
\boldsymbol{\theta}_{\mathrm{new}}
=\boldsymbol{\theta}+\eta\mathbf{d}.
$$

一阶损失变化约为：

$$
L(\boldsymbol{\theta}+\eta\mathbf{d})-L(\boldsymbol{\theta})
\approx\eta\,\mathbf{g}^{\top}\mathbf{d}.
$$

- 夹角小于 $90^\circ$，内积为正，足够小的步子增大损失。
- 夹角大于 $90^\circ$，内积为负，足够小的步子减小损失。
- 垂直时一阶变化为零，有限步长仍可能改变损失。沿等高线的切线直走，不等于沿等高线弯曲前进。

正确的局部下降方向不保证任意步长都能降低损失。狭长谷地里，统一的大步长可能跨谷震荡，小步长则会减慢沿平缓方向的推进。在有限训练步数下可能还未接近谷底；不能仅凭学习率小断言最终无法收敛。

## 尚待继续

已讨论损失取舍、梯度局部信息、链式反向、同一参数状态下更新、批次平均梯度，以及 SGD 和动量的基础。

Adam 的历史方向与逐参数尺度、梯度消失和爆炸的具体机制与处理方式，仍待展开。噪声假设、最大似然、模型规模、数据量和正则化的相互影响也尚未学习；当前接续以 path.json 为准。

## 来源

- [PyTorch：自动微分与计算图](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html)：链式法则和反向梯度计算。
- [PyTorch：参数优化](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html)：前向、反向与参数更新的训练流程。
- [PyTorch：SGD 与动量](https://docs.pytorch.org/docs/2.14/generated/torch.optim.SGD.html)：普通 SGD 与动量更新规则。
- [Google MLCC：损失函数](https://developers.google.com/machine-learning/crash-course/linear-regression/loss)：绝对损失、平方损失及大误差的代价。
- [scikit-learn：回归损失准则](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html)：固定预测下均值与中位数对应的损失最小化。
- [Google MLCC：梯度下降](https://developers.google.com/machine-learning/crash-course/linear-regression/gradient-descent)：斜率、参数更新与学习率。
