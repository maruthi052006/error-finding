import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bugbuster_app.settings')
django.setup()

from accounts.models import CustomUser
from events.models import Round, Problem, Team

# CustomUser setup
if not CustomUser.objects.filter(username='admin').exists():
    admin = CustomUser.objects.create_superuser('admin', 'admin@bugbuster.com', 'admin123')
    admin.role = 'admin'
    admin.save()
    print("Superuser 'admin' created with password 'admin123'")

if not CustomUser.objects.filter(username='coord1').exists():
    coord = CustomUser.objects.create_user('coord1', 'coord1@bugbuster.com', 'coord123')
    coord.role = 'coordinator'
    coord.is_staff = True
    coord.save()
    print("Coordinator 'coord1' created with password 'coord123'")
    
# Mock Round Easy (3 problems)
if not Round.objects.filter(name='Mock Round Easy').exists():
    r1 = Round.objects.create(name='Mock Round Easy', difficulty='Easy', duration_minutes=15, is_active=True)
    
    # Problem 1
    c1 = '#include <stdio.h>\nint main() {\n    printf("Hello Bug Buster") // error\n    return 0;\n}'
    p1 = 'def greet():\n    print("Hello Bug Buster" # error\ngreet()'
    Problem.objects.create(round=r1, title='P1: Syntax Error', description='Fix basic grammar.', buggy_code_c=c1, buggy_code_python=p1, expected_output='Hello Bug Buster\n')
    
    # Problem 2
    c2 = '#include <stdio.h>\nint main() {\n    int a = 5, b = 0;\n    printf("%d", a/b);\n    return 0;\n}'
    p2 = 'a = 5\nb = 0\nprint(a/b)'
    Problem.objects.create(round=r1, title='P2: Runtime Zero', description='Fix Division by zero to print 1.', buggy_code_c=c2, buggy_code_python=p2, expected_output='1\n')
    
    # Problem 3
    c3 = '#include <stdio.h>\nint main() {\n    int i;\n    for(i=0; i<=5; i++);\n        printf("%d", i);\n    return 0;\n}'
    p3 = 'for i in range(6):\n    pass\nprint(i)\n'
    Problem.objects.create(round=r1, title='P3: Logical Loop', description='Fix logic error in loops to print numbers 0 to 5 on new lines.', buggy_code_c=c3, buggy_code_python=p3, expected_output='0\n1\n2\n3\n4\n5\n')
    
    print("Created Mock Round Easy (3 problems).")

# Mock Round Hard (2 problems)
if not Round.objects.filter(name='Mock Round Hard').exists():
    r2 = Round.objects.create(name='Mock Round Hard', difficulty='Hard', duration_minutes=30, is_active=True)
    
    # Problem 1
    c1 = '#include <stdio.h>\nvoid swap(int a, int b) {\n    int t=a; a=b; b=t;\n}\nint main() {\n    int x=1, y=2; swap(x,y); printf("%d %d", x, y);\n    return 0;\n}'
    p1 = 'def swap(a, b):\n    t=a; a=b; b=t\nx=1; y=2\nswap(x,y)\nprint(x, y)'
    Problem.objects.create(round=r2, title='P1: Pass by Value', description='Swap two numbers correctly by reference. Print "2 1".', buggy_code_c=c1, buggy_code_python=p1, expected_output='2 1\n')
    
    # Problem 2
    c2 = '#include <stdio.h>\n#include <stdlib.h>\nint main() {\n    int *ptr = malloc(sizeof(int));\n    *ptr = 10;\n    free(ptr);\n    printf("%d", *ptr);\n    return 0;\n}'
    p2 = 'def memory_leak():\n    lst = []\n    while True:\n        lst.append("Memory")\n        break\n    print(lst[1])\nmemory_leak()'
    Problem.objects.create(round=r2, title='P2: Memory Access', description='Fix the invalid memory access.', buggy_code_c=c2, buggy_code_python=p2, expected_output='10\n')
    
    print("Created Mock Round Hard (2 problems).")
