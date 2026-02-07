from src.engine import AIEngine
from src.skills.productivity import ProductivityManager
from datetime import datetime, timedelta
import os

def test_deadline_flow():
    # Use a dummy file
    test_file = "test_productivity_deadline.json"
    if os.path.exists(test_file): os.remove(test_file)
    
    pm = ProductivityManager(test_file)
    engine = AIEngine(pm)
    
    # Test 1: "Deadline for Project X tomorrow"
    cmd1 = "Deadline for Project Alpha tomorrow"
    resp1 = engine.process_input(cmd1)
    print(f"CMD: '{cmd1}' -> RESP: '{resp1}'")
    
    # Test 2: "Project Beta due tomorrow"
    cmd2 = "Project Beta due tomorrow"
    resp2 = engine.process_input(cmd2)
    print(f"CMD: '{cmd2}' -> RESP: '{resp2}'")
    
    # Verify Data
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    tasks = pm.get_tasks_for_date(tomorrow)
    
    alpha_ok = False
    beta_ok = False
    
    for t in tasks:
        print(f"Task Found: {t['title']} | Category: {t.get('category')}")
        if "Project Alpha" in t['title'] and t.get('category') == "Deadline":
            alpha_ok = True
        if "Project Beta" in t['title'] and t.get('category') == "Deadline":
            beta_ok = True
            
    if alpha_ok and beta_ok:
        print("SUCCESS: Both deadline formats parsed correctly.")
    else:
        print("FAILURE: Deadlines missing or incorrect category.")

    # Cleanup
    if os.path.exists(test_file): os.remove(test_file)

if __name__ == "__main__":
    test_deadline_flow()
