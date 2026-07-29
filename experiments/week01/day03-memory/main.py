from memory import Memory

memory = Memory()

memory.save("name", "Alex", {"type": "user_info"})
print("已保存 name -> Alex")

val = memory.retrieve("name")
print(f"检索 name -> {val}")

results = memory.search("Alex")
print(f"语义搜索 'Alex' -> {results}")
