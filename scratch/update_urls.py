import os
d = 'c:/Users/adars/OneDrive/Desktop/My_Protfolio/frontend'
target = 'https://ai-portfolio-ynsq.onrender.com/api'
source = 'http://localhost:5000/api'

for root, dirs, files in os.walk(d):
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(root, f)
            try:
                with open(p, 'r', encoding='utf-8') as file:
                    content = file.read()
                if source in content:
                    print(f"Updating {p}")
                    new_content = content.replace(source, target)
                    with open(p, 'w', encoding='utf-8') as file:
                        file.write(new_content)
            except Exception as e:
                print(f"Error processing {p}: {e}")
