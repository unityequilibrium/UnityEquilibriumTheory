import os

topics_dir = r"c:\Users\santa\Desktop\uet_harness\docs\topics"

def update_front_matter():
    for topic in os.listdir(topics_dir):
        topic_path = os.path.join(topics_dir, topic)
        if os.path.isdir(topic_path):
            readme_path = os.path.join(topic_path, "README.md")
            if os.path.exists(readme_path):
                with open(readme_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check for existing YAML front matter
                if content.startswith("---"):
                    # Already has front matter, we need to ensure 'layout: article' is present
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        yaml_block = parts[1]
                        if "layout:" not in yaml_block:
                            yaml_block = "layout: article\n" + yaml_block
                        elif "layout: default" in yaml_block:
                            yaml_block = yaml_block.replace("layout: default", "layout: article")
                        
                        new_content = "---" + yaml_block + "---" + parts[2]
                        with open(readme_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        print(f"Updated [EXISTING]: {topic}")
                else:
                    # No front matter, add it
                    title = topic.split("_", 1)[1].replace("_", " ") if "_" in topic else topic
                    header = f"---\nlayout: article\ntitle: \"UET Topic {topic.split('_')[0]}: {title}\"\ndescription: \"Research module for {title} within the Unity Equilibrium Theory framework.\"\n---\n\n"
                    new_content = header + content
                    with open(readme_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Added [NEW]: {topic}")

if __name__ == "__main__":
    update_front_matter()
