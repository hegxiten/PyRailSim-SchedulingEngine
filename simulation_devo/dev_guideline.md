# --------- deprecated ---------#
1. 将信号系统与车的行进系统离散，两个系统互相不影响，通过映射建立block与某两盏灯的关系。
2. 订阅关系分为两种：1. 灯与灯之间的依赖关系。这个关系在系统刚刚建立完成时已经确定，属于既定的关系，后期不会因为火车的移动而变化。
                  2. 车所在的block与灯的关系。这个关系会随着车的移动或者让车逻辑，block进行变化，那么有车的block会对其观察者进行影响。观察了这个block的那几盏灯会变红。
                  那几盏灯变红后，会使得其余订阅了这几盏灯的其余灯根据既定的灯与灯之间的关系进行变化。
3. 车的前进逻辑与轨道的数据结构基本不变，仍旧按照addlength或者addsignal里面的关系进行。
4. 信号灯系统中，仍旧可以利用control point与bigblock的概念进行开发，减少灯个体之间的订阅，改为更大类之间的订阅。
5. 可以考虑建立一个映射类，将灯与实际的block联系起来。
# --------- deprecated ---------#

2019-07-09:
1. 每一次步进更新时，列车更新顺序很关键。
    1.1 更新顺序和迫近的冲突最有关系，memoryless。                  √
    1.2. 顺序可以由列车列表的sort()方法返回，或者自行设计。          √

2. 每次新增列车或新减列车，以及列车发生相对位置的变化（完成实质性的pass和meet），就触发一次调度方法。每次调度方法接受额外传参（原调度安排，新增/新减列车）返回新调度安排（routing和aspect）。列车继续更新。
3. 调度方法接受传参（原调度安排，列车状态新增列车，现所有列车的状态，比如速度，位置，制动曲线）。在不违反系统要求的前提下，计算新调度安排。
    3.1 若有解，则接受新增列车，返回新调度安排。
    3.2 若无解，拒绝新增列车，返回原调度安排。