def human_approval_tool(query: str) -> str:
    print("\n=== SQL QUERY PROPOSED ===")
    print(query)
    
    decision = input("Approve query? (y/n/edit): ")

    if decision == "y":
        return query
    
    if decision == "edit":
        edited = input("Paste edited SQL: ")
        return edited
    
    raise Exception("Query rejected by human")
