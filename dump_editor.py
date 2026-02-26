import urllib.request
import urllib.parse
from http.cookiejar import CookieJar
import re

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Get CSRF
opener.open('http://127.0.0.1:8000/accounts/login/')
csrf = ''
for c in cj:
    if c.name == 'csrftoken': csrf = c.value

# Post login
data = urllib.parse.urlencode({'username':'testteam1', 'password':'password', 'csrfmiddlewaretoken':csrf}).encode()
opener.open('http://127.0.0.1:8000/accounts/login/', data)

# Fetch dashboard
dash = opener.open('http://127.0.0.1:8000/compiler/dashboard/').read().decode()
match = re.search(r'href="(.*?)"[^>]*>Resume', dash)
if not match:
    match = re.search(r'href="(.*?)"[^>]*>Enter Round', dash)

if match:
    url = 'http://127.0.0.1:8000' + match.group(1)
    
    # Actually wait we want to visit the problem list then enter compiler editor
    # Let's say we are on problem_list. Let's fetch problem list.
    prob_list = opener.open(url).read().decode()
    match2 = re.search(r'href="(.*?)"[^>]*>Solve', prob_list)
    if match2:
        editor_url = 'http://127.0.0.1:8000' + match2.group(1)
        editor = opener.open(editor_url).read().decode()
        with open('editor_dump.html', 'w', encoding='utf-8') as f:
            f.write(editor)
        print('Saved to editor_dump.html')
    else:
        print('No editor link found in problem list')
else:
    print('No problem list link found in dashboard')
