### Agemt Loop

###  1、observe（观察）
获取用户输入的当前信息，将信息转换成agent可以理解的信息
###  2、Thinking（思考）
理解用户的问题：
    现在是什么状态？
    目标是什么？
    我需要做什么？
    下一步应该做什么？
###  3、Act（行动）
调用工具（根据思考所得的下一步做什么，开始执行）——会有很多Tool，集成所有可用的Tool
##  4、Observe结果
观察是否完成目标，没有完成则继续，
完成了，则结束


 User
  ↓
 Agent
  ↓
 Think
  ↓
 Action
  ↓
 Observation
  ↓
 Answer


 Agent = LLM+ Memory + Tools + Loop + Decision

###  OpenAI Function Calling思想。
 LLM:
 我需要调用calculator
 ↓
 程序执行
 ↓
 结果返回LLM
 ↓
 继续回答



